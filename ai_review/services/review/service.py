from ai_review.libs.asynchronous.gather import bounded_gather
from ai_review.libs.logger import get_logger
from ai_review.services.artifacts.service import ArtifactsService
from ai_review.services.cost.service import CostService
from ai_review.services.diff.service import DiffService
from ai_review.services.git.service import GitService
from ai_review.services.hook import hook
from ai_review.services.llm.factory import get_llm_client
from ai_review.services.prompt.adapter import build_prompt_context_from_mr_info
from ai_review.services.prompt.service import PromptService
from ai_review.services.review.gateway.comment import ReviewCommentGateway
from ai_review.services.review.gateway.llm import ReviewLLMGateway
from ai_review.services.review.inline.service import InlineCommentService
from ai_review.services.review.policy.service import ReviewPolicyService
from ai_review.services.review.summary.service import SummaryCommentService
from ai_review.services.vcs.factory import get_vcs_client
from ai_review.services.vcs.types import ReviewInfoSchema

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

        self.llm_gateway = ReviewLLMGateway(
            llm=self.llm,
            cost=self.cost,
            artifacts=self.artifacts
        )
        self.comment_gateway = ReviewCommentGateway(vcs=self.vcs)

    async def process_file_inline(self, file: str, review_info: ReviewInfoSchema) -> None:
        raw_diff = self.git.get_diff_for_file(review_info.base_sha, review_info.head_sha, file)
        if not raw_diff.strip():
            logger.debug(f"No diff for {file}, skipping")
            return

        rendered_file = self.diff.render_file(
            file=file,
            base_sha=review_info.base_sha,
            head_sha=review_info.head_sha,
            raw_diff=raw_diff,
        )
        prompt_context = build_prompt_context_from_mr_info(review_info)
        prompt = self.prompt.build_inline_request(rendered_file, prompt_context)
        prompt_system = self.prompt.build_system_inline_request(prompt_context)
        prompt_result = await self.llm_gateway.ask(prompt, prompt_system)

        comments = self.inline.parse_model_output(prompt_result).dedupe()
        comments.root = self.policy.apply_for_inline_comments(comments.root)
        if not comments.root:
            logger.info(f"No inline comments for file: {file}")
            return

        logger.info(f"Posting {len(comments.root)} inline comments to {file}")
        await self.comment_gateway.process_inline_comments(comments)

    async def run_inline_review(self) -> None:
        await hook.emit_inline_review_start()
        if await self.comment_gateway.has_existing_inline_comments():
            return

        review_info = await self.vcs.get_review_info()
        logger.info(f"Starting inline review: {len(review_info.changed_files)} files changed")

        changed_files = self.policy.apply_for_files(review_info.changed_files)
        await bounded_gather([
            self.process_file_inline(changed_file, review_info)
            for changed_file in changed_files
        ])
        await hook.emit_inline_review_complete(self.cost.aggregate())

    async def run_context_review(self) -> None:
        await hook.emit_context_review_start()
        if await self.comment_gateway.has_existing_inline_comments():
            return

        review_info = await self.vcs.get_review_info()
        changed_files = self.policy.apply_for_files(review_info.changed_files)
        if not changed_files:
            logger.info("No files to review for context review")
            return

        logger.info(f"Starting context inline review: {len(changed_files)} files changed")

        rendered_files = self.diff.render_files(
            git=self.git,
            files=changed_files,
            base_sha=review_info.base_sha,
            head_sha=review_info.head_sha,
        )
        prompt_context = build_prompt_context_from_mr_info(review_info)
        prompt = self.prompt.build_context_request(rendered_files, prompt_context)
        prompt_system = self.prompt.build_system_context_request(prompt_context)
        prompt_result = await self.llm_gateway.ask(prompt, prompt_system)

        comments = self.inline.parse_model_output(prompt_result).dedupe()
        comments.root = self.policy.apply_for_context_comments(comments.root)
        if not comments.root:
            logger.info("No inline comments from context review")
            return

        logger.info(f"Posting {len(comments.root)} inline comments (context review)")
        await self.comment_gateway.process_inline_comments(comments)
        await hook.emit_context_review_complete(self.cost.aggregate())

    async def run_summary_review(self) -> None:
        await hook.emit_summary_review_start()
        if await self.comment_gateway.has_existing_summary_comments():
            return

        review_info = await self.vcs.get_review_info()
        changed_files = self.policy.apply_for_files(review_info.changed_files)
        if not changed_files:
            logger.info("No files to review for summary")
            return

        logger.info(f"Starting summary review: {len(changed_files)} files changed")

        rendered_files = self.diff.render_files(
            git=self.git,
            files=changed_files,
            base_sha=review_info.base_sha,
            head_sha=review_info.head_sha,
        )
        prompt_context = build_prompt_context_from_mr_info(review_info)
        prompt = self.prompt.build_summary_request(rendered_files, prompt_context)
        prompt_system = self.prompt.build_system_summary_request(prompt_context)
        prompt_result = await self.llm_gateway.ask(prompt, prompt_system)

        summary = self.summary.parse_model_output(prompt_result)
        if not summary.text.strip():
            logger.warning("Summary LLM output was empty, skipping comment")
            return

        logger.info(f"Posting summary review comment ({len(summary.text)} chars)")
        await self.comment_gateway.process_summary_comment(summary)
        await hook.emit_summary_review_complete(self.cost.aggregate())

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
