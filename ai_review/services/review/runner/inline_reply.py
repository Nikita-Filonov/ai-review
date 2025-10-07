from ai_review.libs.asynchronous.gather import bounded_gather
from ai_review.libs.logger import get_logger
from ai_review.services.cost.types import CostServiceProtocol
from ai_review.services.diff.types import DiffServiceProtocol
from ai_review.services.git.types import GitServiceProtocol
from ai_review.services.hook import hook
from ai_review.services.prompt.adapter import build_prompt_context_from_review_info
from ai_review.services.prompt.types import PromptServiceProtocol
from ai_review.services.review.gateway.types import ReviewCommentGatewayProtocol, ReviewLLMGatewayProtocol
from ai_review.services.review.internal.inline_reply.types import InlineCommentReplyServiceProtocol
from ai_review.services.review.internal.policy.types import ReviewPolicyServiceProtocol
from ai_review.services.review.runner.types import ReviewRunnerProtocol
from ai_review.services.vcs.types import ReviewInfoSchema, VCSClientProtocol, ReviewThreadSchema

logger = get_logger("INLINE_REPLY_REVIEW_RUNNER")


class InlineReplyReviewRunner(ReviewRunnerProtocol):
    def __init__(
            self,
            vcs: VCSClientProtocol,
            git: GitServiceProtocol,
            diff: DiffServiceProtocol,
            cost: CostServiceProtocol,
            prompt: PromptServiceProtocol,
            review_policy: ReviewPolicyServiceProtocol,
            review_llm_gateway: ReviewLLMGatewayProtocol,
            inline_comment_reply: InlineCommentReplyServiceProtocol,
            review_comment_gateway: ReviewCommentGatewayProtocol,
    ):
        self.vcs = vcs
        self.git = git
        self.diff = diff
        self.cost = cost
        self.prompt = prompt
        self.review_policy = review_policy
        self.review_llm_gateway = review_llm_gateway
        self.inline_comment_reply = inline_comment_reply
        self.review_comment_gateway = review_comment_gateway

    async def process_thread_reply(self, thread: ReviewThreadSchema, review_info: ReviewInfoSchema):
        logger.info(f"Processing inline reply for thread {thread.id}")

        raw_diff = self.git.get_diff_for_file(review_info.base_sha, review_info.head_sha, thread.file)
        if not raw_diff.strip():
            logger.debug(f"No diff for {thread.file}, skipping")
            return

        rendered_file = self.diff.render_file(
            file=thread.file,
            base_sha=review_info.base_sha,
            head_sha=review_info.head_sha,
            raw_diff=raw_diff
        )

        prompt_context = build_prompt_context_from_review_info(review_info)
        prompt = self.prompt.build_inline_reply_request(rendered_file, thread, prompt_context)
        prompt_system = self.prompt.build_system_inline_reply_request(prompt_context)
        prompt_result = await self.review_llm_gateway.ask(prompt, prompt_system)

        reply = self.inline_comment_reply.parse_model_output(prompt_result)
        if not reply:
            logger.info(f"AI model returned no valid reply for thread {thread.id} ({len(thread.comments)} comments)")
            return

        await self.review_comment_gateway.process_inline_reply(thread.id, reply)

    async def run(self) -> None:
        await hook.emit_inline_reply_review_start()

        review_info = await self.vcs.get_review_info()
        threads = await self.review_comment_gateway.get_inline_threads()
        if not threads:
            logger.info("No AI inline threads found, skipping reply mode")
            return

        logger.info(f"Found {len(threads)} AI inline threads for reply")

        await bounded_gather([self.process_thread_reply(thread, review_info) for thread in threads])
        await hook.emit_inline_reply_review_complete(self.cost.aggregate())
