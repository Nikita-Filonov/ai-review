from config import settings
from libs.asynchronous.gather import bounded_gather
from libs.logger import get_logger
from services.cost.service import CostService
from services.diff.service import DiffService
from services.git.service import GitService
from services.llm.factory import get_llm_client
from services.prompt.service import PromptService
from services.review.inline.service import InlineCommentService
from services.review.policy.service import ReviewPolicyService
from services.review.summary.service import SummaryCommentService
from services.vcs.factory import get_vcs_client

logger = get_logger("REVIEW_SERVICE")


class ReviewService:
    def __init__(self):
        self.llm = get_llm_client()
        self.vcs = get_vcs_client()
        self.git = GitService()
        self.diff = DiffService()
        self.cost = CostService()
        self.prompt = PromptService()
        self.policy = ReviewPolicyService()
        self.inline = InlineCommentService()
        self.summary = SummaryCommentService()

    async def ask_llm(self, prompt_text: str) -> str:
        try:
            result = await self.llm.chat(prompt_text)
            if not result.text:
                logger.warning(
                    f"LLM returned an empty response (prompt length={len(prompt_text)} chars)"
                )

            report = self.cost.calculate(result)
            if report:
                logger.info(report.pretty())

            return result.text
        except Exception as error:
            logger.error(f"LLM request failed: {error}")
            raise

    async def has_existing_inline_discussions(self) -> bool:
        discussions = await self.vcs.get_discussions()
        has_discussions = any(
            settings.review.inline_tag in note.body
            for discussion in discussions
            for note in discussion.notes
        )
        if has_discussions:
            logger.info("Skipping inline review: AI inline discussions already exist")

        return has_discussions

    async def has_existing_summary_discussions(self) -> bool:
        discussions = await self.vcs.get_discussions()
        has_discussions = any(
            settings.review.summary_tag in note.body
            for discussion in discussions
            for note in discussion.notes
        )
        if has_discussions:
            logger.info("Skipping summary review: AI summary comment already exists")

        return has_discussions

    async def process_file_inline(self, file: str, base_sha: str, head_sha: str) -> None:
        raw_diff = self.git.get_diff_for_file(base_sha, head_sha, file)
        if not raw_diff.strip():
            logger.debug(f"No diff for {file}, skipping")
            return

        annotated = self.diff.apply_diff(raw_diff, file)
        prompt_text = self.prompt.build_inline_request(f"# File: {file}\n{annotated}")
        prompt_result = await self.ask_llm(prompt_text)

        changed_lines = self.diff.build_changed_lines_by_file(raw_diff, file)
        comments = (
            self.inline.parse_model_output(prompt_result)
            .dedupe()
            .filter(changed_lines)
        )

        if not comments.root:
            logger.info(f"No inline comments for file: {file}")
            return

        logger.info(f"Posting {len(comments.root)} inline comments to {file}")

        results = await bounded_gather([
            self.vcs.create_discussion(
                file=comment.file,
                line=comment.line,
                message=f"{comment.message}\n\n{settings.review.inline_tag}"
            )
            for comment in comments.root
        ])
        fallbacks = [
            self.vcs.create_comment(
                f"**{comment.file}:{comment.line}** — {comment.message}\n\n{settings.review.inline_tag}"
            )
            for comment, result in zip(comments.root, results)
            if isinstance(result, Exception)
        ]
        if fallbacks:
            logger.warning(f"Falling back to {len(fallbacks)} general comments for {file}")
            await bounded_gather(fallbacks)

    async def run_inline_review(self) -> None:
        if await self.has_existing_inline_discussions():
            return

        mr_info = await self.vcs.get_mr_info()
        logger.info(f"Starting inline review: {len(mr_info.changed_files)} files changed")

        changed_files = self.policy.apply(mr_info.changed_files)
        await bounded_gather([
            self.process_file_inline(changed_file, mr_info.base_sha, mr_info.head_sha)
            for changed_file in changed_files
        ])

    async def run_summary_review(self) -> None:
        if await self.has_existing_summary_discussions():
            return

        mr_info = await self.vcs.get_mr_info()
        changed_files = self.policy.apply(mr_info.changed_files)

        if not changed_files:
            logger.info("No files to review for summary")
            return

        logger.info(f"Starting summary review: {len(changed_files)} files changed")

        diffs_by_file = {
            file: self.git.get_diff_for_file(mr_info.base_sha, mr_info.head_sha, file)
            for file in changed_files
        }
        annotated_diffs = self.diff.apply_diff_for_files(diffs_by_file)
        if not annotated_diffs:
            logger.info("No annotated diffs generated for summary review")
            return

        prompt_text = self.prompt.build_summary_request(annotated_diffs)
        prompt_result = await self.ask_llm(prompt_text)

        summary = self.summary.parse_model_output(prompt_result)
        if not summary.text.strip():
            logger.warning("Summary LLM output was empty, skipping comment")
            return

        logger.info(f"Posting summary review comment ({len(summary.text)} chars)")

        try:
            await self.vcs.create_comment(f"{summary.text}\n\n{settings.review.summary_tag}")
        except Exception as error:
            logger.error(f"Failed to post summary comment: {error}")

    def report_total_cost(self):
        total_report = self.cost.aggregate()
        if total_report:
            logger.info(
                "\n=== TOTAL REVIEW COST ===\n"
                f"{total_report.pretty()}\n"
                "========================="
            )
        else:
            logger.info("No cost data collected for this review")
