from ai_review.libs.logger import get_logger
from ai_review.services.cost.types import CostServiceProtocol
from ai_review.services.diff.types import DiffServiceProtocol
from ai_review.services.git.types import GitServiceProtocol
from ai_review.services.hook import hook
from ai_review.services.prompt.adapter import build_prompt_context_from_review_info
from ai_review.services.prompt.types import PromptServiceProtocol
from ai_review.services.review.gateway.types import ReviewLLMGatewayProtocol, ReviewCommentGatewayProtocol
from ai_review.services.review.internal.policy.types import ReviewPolicyServiceProtocol
from ai_review.services.review.internal.summary.types import SummaryCommentServiceProtocol
from ai_review.services.review.runner.types import ReviewRunnerProtocol
from ai_review.services.vcs.types import VCSClientProtocol

logger = get_logger("SUMMARY_REVIEW_RUNNER")


class SummaryReviewRunner(ReviewRunnerProtocol):
    def __init__(
            self,
            vcs: VCSClientProtocol,
            git: GitServiceProtocol,
            diff: DiffServiceProtocol,
            cost: CostServiceProtocol,
            prompt: PromptServiceProtocol,
            review_policy: ReviewPolicyServiceProtocol,
            summary_comment: SummaryCommentServiceProtocol,
            review_llm_gateway: ReviewLLMGatewayProtocol,
            review_comment_gateway: ReviewCommentGatewayProtocol,
    ):
        self.vcs = vcs
        self.git = git
        self.diff = diff
        self.cost = cost
        self.prompt = prompt
        self.review_policy = review_policy
        self.summary_comment = summary_comment
        self.review_llm_gateway = review_llm_gateway
        self.review_comment_gateway = review_comment_gateway

    async def run(self) -> None:
        await hook.emit_summary_review_start()
        if await self.review_comment_gateway.has_existing_summary_comments():
            return

        review_info = await self.vcs.get_review_info()
        changed_files = self.review_policy.apply_for_files(review_info.changed_files)
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
        prompt_context = build_prompt_context_from_review_info(review_info)
        prompt = self.prompt.build_summary_request(rendered_files, prompt_context)
        prompt_system = self.prompt.build_system_summary_request(prompt_context)
        prompt_result = await self.review_llm_gateway.ask(prompt, prompt_system)

        summary = self.summary_comment.parse_model_output(prompt_result)
        if not summary.text.strip():
            logger.warning("Summary LLM output was empty, skipping comment")
            return

        logger.info(f"Posting summary review comment ({len(summary.text)} chars)")
        await self.review_comment_gateway.process_summary_comment(summary)
        await hook.emit_summary_review_complete(self.cost.aggregate())
