from typing import Literal

from ai_review.config import settings
from ai_review.libs.asynchronous.gather import bounded_gather
from ai_review.libs.logger import get_logger
from ai_review.services.artifacts.service import ArtifactsService
from ai_review.services.cost.service import CostService
from ai_review.services.diff.service import DiffService
from ai_review.services.git.service import GitService
from ai_review.services.llm.factory import get_llm_client
from ai_review.services.prompt.adapter import build_prompt_context_from_mr_info
from ai_review.services.prompt.service import PromptService
from ai_review.services.review.inline.schema import InlineCommentListSchema
from ai_review.services.review.inline.service import InlineCommentService
from ai_review.services.review.policy.service import ReviewPolicyService
from ai_review.services.review.summary.service import SummaryCommentService
from ai_review.services.vcs.factory import get_vcs_client
from ai_review.services.vcs.types import MRInfoSchema

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
        self.artifacts = ArtifactsService()

    async def ask_llm(self, prompt: str, prompt_system: str) -> str:
        try:
            result = await self.llm.chat(prompt, prompt_system)
            if not result.text:
                logger.warning(
                    f"LLM returned an empty response (prompt length={len(prompt)} chars)"
                )

            report = self.cost.calculate(result)
            if report:
                logger.info(report.pretty())

            await self.artifacts.save_llm_interaction(prompt, prompt_system, result.text)

            return result.text
        except Exception as error:
            logger.exception(f"LLM request failed: {error}")
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

    async def has_existing_summary_comments(self) -> bool:
        comments = await self.vcs.get_comments()
        has_comments = any(settings.review.summary_tag in comment.body for comment in comments)
        if has_comments:
            logger.info("Skipping summary review: AI summary comment already exists")

        return has_comments

    async def process_discussions(self, flow: Literal["inline", "context"], comments: InlineCommentListSchema) -> None:
        results = await bounded_gather([
            self.vcs.create_discussion(
                file=comment.file,
                line=comment.line,
                message=comment.body_with_tag
            )
            for comment in comments.root
        ])
        fallbacks = [
            self.vcs.create_comment(comment.fallback_body_with_tag)
            for comment, result in zip(comments.root, results)
            if isinstance(result, Exception)
        ]
        if fallbacks:
            logger.warning(f"Falling back to {len(fallbacks)} general comments ({flow} review)")
            await bounded_gather(fallbacks)

    async def process_file_inline(self, file: str, mr_info: MRInfoSchema) -> None:
        raw_diff = self.git.get_diff_for_file(mr_info.base_sha, mr_info.head_sha, file)
        if not raw_diff.strip():
            logger.debug(f"No diff for {file}, skipping")
            return

        rendered_file = self.diff.render_file(
            file=file,
            base_sha=mr_info.base_sha,
            head_sha=mr_info.head_sha,
            raw_diff=raw_diff,
        )
        prompt_context = build_prompt_context_from_mr_info(mr_info)
        prompt = self.prompt.build_inline_request(rendered_file, prompt_context)
        prompt_system = self.prompt.build_system_inline_request(prompt_context)
        prompt_result = await self.ask_llm(prompt, prompt_system)

        comments = self.inline.parse_model_output(prompt_result).dedupe()
        comments.root = self.policy.apply_for_inline_comments(comments.root)
        if not comments.root:
            logger.info(f"No inline comments for file: {file}")
            return

        logger.info(f"Posting {len(comments.root)} inline comments to {file}")
        await self.process_discussions(flow="inline", comments=comments)

    async def run_inline_review(self) -> None:
        if await self.has_existing_inline_discussions():
            return

        mr_info = await self.vcs.get_mr_info()

        logger.info(f"Starting inline review: {len(mr_info.changed_files)} files changed")

        changed_files = self.policy.apply_for_files(mr_info.changed_files)
        await bounded_gather([
            self.process_file_inline(changed_file, mr_info)
            for changed_file in changed_files
        ])

    async def run_context_review(self) -> None:
        if await self.has_existing_inline_discussions():
            return

        mr_info = await self.vcs.get_mr_info()
        changed_files = self.policy.apply_for_files(mr_info.changed_files)

        if not changed_files:
            logger.info("No files to review for context review")
            return

        logger.info(f"Starting context inline review: {len(changed_files)} files changed")

        rendered_files = self.diff.render_files(
            git=self.git,
            files=changed_files,
            base_sha=mr_info.base_sha,
            head_sha=mr_info.head_sha,
        )
        prompt_context = build_prompt_context_from_mr_info(mr_info)
        prompt = self.prompt.build_context_request(rendered_files, prompt_context)
        prompt_system = self.prompt.build_system_context_request(prompt_context)
        prompt_result = await self.ask_llm(prompt, prompt_system)

        comments = self.inline.parse_model_output(prompt_result).dedupe()
        comments.root = self.policy.apply_for_context_comments(comments.root)
        if not comments.root:
            logger.info("No inline comments from context review")
            return

        logger.info(f"Posting {len(comments.root)} inline comments (context review)")
        await self.process_discussions(flow="context", comments=comments)

    async def run_summary_review(self) -> None:
        if await self.has_existing_summary_comments():
            return

        mr_info = await self.vcs.get_mr_info()
        changed_files = self.policy.apply_for_files(mr_info.changed_files)

        if not changed_files:
            logger.info("No files to review for summary")
            return

        logger.info(f"Starting summary review: {len(changed_files)} files changed")

        rendered_files = self.diff.render_files(
            git=self.git,
            files=changed_files,
            base_sha=mr_info.base_sha,
            head_sha=mr_info.head_sha,
        )
        prompt_context = build_prompt_context_from_mr_info(mr_info)
        prompt = self.prompt.build_summary_request(rendered_files, prompt_context)
        prompt_system = self.prompt.build_system_summary_request(prompt_context)
        prompt_result = await self.ask_llm(prompt, prompt_system)

        summary = self.summary.parse_model_output(prompt_result)
        if not summary.text.strip():
            logger.warning("Summary LLM output was empty, skipping comment")
            return

        logger.info(f"Posting summary review comment ({len(summary.text)} chars)")
        await self.vcs.create_comment(summary.body_with_tag)

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
