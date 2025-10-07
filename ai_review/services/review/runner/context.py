from ai_review.libs.logger import get_logger
from ai_review.services.cost.types import CostServiceProtocol
from ai_review.services.diff.types import DiffServiceProtocol
from ai_review.services.git.types import GitServiceProtocol
from ai_review.services.hook import hook
from ai_review.services.prompt.adapter import build_prompt_context_from_review_info
from ai_review.services.prompt.types import PromptServiceProtocol
from ai_review.services.review.gateway.types import ReviewLLMGatewayProtocol, ReviewCommentGatewayProtocol
from ai_review.services.review.internal.inline.types import InlineCommentServiceProtocol
from ai_review.services.review.internal.policy.types import ReviewPolicyServiceProtocol
from ai_review.services.review.runner.types import ReviewRunnerProtocol
from ai_review.services.vcs.types import VCSClientProtocol

logger = get_logger("CONTEXT_REVIEW_RUNNER")


class ContextReviewRunner(ReviewRunnerProtocol):
    def __init__(
            self,
            vcs: VCSClientProtocol,
            git: GitServiceProtocol,
            diff: DiffServiceProtocol,
            cost: CostServiceProtocol,
            prompt: PromptServiceProtocol,
            review_policy: ReviewPolicyServiceProtocol,
            inline_comment: InlineCommentServiceProtocol,
            review_llm_gateway: ReviewLLMGatewayProtocol,
            review_comment_gateway: ReviewCommentGatewayProtocol,
    ):
        self.vcs = vcs
        self.git = git
        self.diff = diff
        self.cost = cost
        self.prompt = prompt
        self.review_policy = review_policy
        self.inline_comment = inline_comment
        self.review_llm_gateway = review_llm_gateway
        self.review_comment_gateway = review_comment_gateway

    async def run(self) -> None:
        await hook.emit_context_review_start()
        if await self.review_comment_gateway.has_existing_inline_comments():
            return

        review_info = await self.vcs.get_review_info()
        changed_files = self.review_policy.apply_for_files(review_info.changed_files)
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
        prompt_context = build_prompt_context_from_review_info(review_info)
        prompt = self.prompt.build_context_request(rendered_files, prompt_context)
        prompt_system = self.prompt.build_system_context_request(prompt_context)
        prompt_result = await self.review_llm_gateway.ask(prompt, prompt_system)

        comments = self.inline_comment.parse_model_output(prompt_result).dedupe()
        comments.root = self.review_policy.apply_for_context_comments(comments.root)
        if not comments.root:
            logger.info("No inline comments from context review")
            return

        logger.info(f"Posting {len(comments.root)} inline comments (context review)")
        await self.review_comment_gateway.process_inline_comments(comments)
        await hook.emit_context_review_complete(self.cost.aggregate())
