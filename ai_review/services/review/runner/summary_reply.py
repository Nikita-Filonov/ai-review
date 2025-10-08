from ai_review.libs.asynchronous.gather import bounded_gather
from ai_review.libs.logger import get_logger
from ai_review.services.cost.types import CostServiceProtocol
from ai_review.services.diff.types import DiffServiceProtocol
from ai_review.services.git.types import GitServiceProtocol
from ai_review.services.hook import hook
from ai_review.services.prompt.adapter import build_prompt_context_from_review_info
from ai_review.services.prompt.types import PromptServiceProtocol
from ai_review.services.review.gateway.types import ReviewCommentGatewayProtocol, ReviewLLMGatewayProtocol
from ai_review.services.review.internal.policy.types import ReviewPolicyServiceProtocol
from ai_review.services.review.internal.summary_reply.types import SummaryCommentReplyServiceProtocol
from ai_review.services.review.runner.types import ReviewRunnerProtocol
from ai_review.services.vcs.types import VCSClientProtocol, ReviewThreadSchema, ReviewInfoSchema

logger = get_logger("SUMMARY_REPLY_REVIEW_RUNNER")


class SummaryReplyReviewRunner(ReviewRunnerProtocol):
    def __init__(
            self,
            vcs: VCSClientProtocol,
            git: GitServiceProtocol,
            diff: DiffServiceProtocol,
            cost: CostServiceProtocol,
            prompt: PromptServiceProtocol,
            review_policy: ReviewPolicyServiceProtocol,
            review_llm_gateway: ReviewLLMGatewayProtocol,
            summary_comment_reply: SummaryCommentReplyServiceProtocol,
            review_comment_gateway: ReviewCommentGatewayProtocol,
    ):
        self.vcs = vcs
        self.git = git
        self.diff = diff
        self.cost = cost
        self.prompt = prompt
        self.review_policy = review_policy
        self.review_llm_gateway = review_llm_gateway
        self.summary_comment_reply = summary_comment_reply
        self.review_comment_gateway = review_comment_gateway

    async def process_thread_reply(self, thread: ReviewThreadSchema, review_info: ReviewInfoSchema):
        logger.info(f"Processing summary reply for thread {thread.id}")

        changed_files = self.review_policy.apply_for_files(review_info.changed_files)
        if not changed_files:
            logger.info("No files to review for summary")
            return

        rendered_files = self.diff.render_files(
            git=self.git,
            files=changed_files,
            base_sha=review_info.base_sha,
            head_sha=review_info.head_sha,
        )
        prompt_context = build_prompt_context_from_review_info(review_info)
        prompt = self.prompt.build_summary_reply_request(rendered_files, thread, prompt_context)
        prompt_system = self.prompt.build_system_summary_reply_request(prompt_context)
        prompt_result = await self.review_llm_gateway.ask(prompt, prompt_system)

        reply = self.summary_comment_reply.parse_model_output(prompt_result)
        if not reply:
            logger.info(f"No valid reply generated for summary thread {thread.id}")
            return

        await self.review_comment_gateway.process_summary_reply(thread.id, reply)

    async def run(self) -> None:
        await hook.emit_summary_reply_review_start()

        review_info = await self.vcs.get_review_info()
        threads = await self.review_comment_gateway.get_summary_threads()
        if not threads:
            logger.info("No AI summary threads found, skipping summary reply mode")
            return

        logger.info(f"Found {len(threads)} AI summary threads for reply")

        await bounded_gather([self.process_thread_reply(thread, review_info) for thread in threads])
        await hook.emit_summary_reply_review_complete(self.cost.aggregate())
