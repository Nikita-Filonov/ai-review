from ai_review.config import settings
from ai_review.libs.logger import get_logger
from ai_review.services.agent.loop.service import AgentLoopService
from ai_review.services.agent.tool.service import AgentToolService
from ai_review.services.artifacts.service import ArtifactsService
from ai_review.services.cost.service import CostService
from ai_review.services.diff.service import DiffService
from ai_review.services.git.service import GitService
from ai_review.services.llm.factory import get_llm_client
from ai_review.services.policy.service import PolicyService
from ai_review.services.prompt.service import PromptService
from ai_review.services.review.gateway.review_agent_llm_gateway import ReviewAgentLLMGateway
from ai_review.services.review.gateway.review_comment_gateway import ReviewCommentGateway
from ai_review.services.review.gateway.review_direct_llm_gateway import ReviewDirectLLMGateway
from ai_review.services.review.gateway.review_dry_run_comment_gateway import ReviewDryRunCommentGateway
from ai_review.services.review.internal.inline.service import InlineCommentService
from ai_review.services.review.internal.inline_reply.service import InlineCommentReplyService
from ai_review.services.review.internal.summary.service import SummaryCommentService
from ai_review.services.review.internal.summary_reply.service import SummaryCommentReplyService
from ai_review.services.review.runner.context import ContextReviewRunner
from ai_review.services.review.runner.inline import InlineReviewRunner
from ai_review.services.review.runner.inline_reply import InlineReplyReviewRunner
from ai_review.services.review.runner.summary import SummaryReviewRunner
from ai_review.services.review.runner.summary_reply import SummaryReplyReviewRunner
from ai_review.services.vcs.factory import get_vcs_client

logger = get_logger("REVIEW_SERVICE")


class ReviewService:
    def __init__(self):
        self.llm = get_llm_client()
        self.vcs = get_vcs_client()
        self.git = GitService()
        self.diff = DiffService()
        self.cost = CostService()
        self.policy = PolicyService()
        self.prompt = PromptService()
        self.artifacts = ArtifactsService()
        self.inline_comment = InlineCommentService()
        self.summary_comment = SummaryCommentService()
        self.inline_comment_reply = InlineCommentReplyService()
        self.summary_comment_reply = SummaryCommentReplyService()

        self.agent_tool = AgentToolService(policy=self.policy)
        self.agent_loop = AgentLoopService(
            llm=self.llm,
            prompt=self.prompt,
            agent_tool=self.agent_tool,
        )

        self.review_direct_llm_gateway = ReviewDirectLLMGateway(
            llm=self.llm,
            cost=self.cost,
            artifacts=self.artifacts,
        )
        self.review_agent_llm_gateway = ReviewAgentLLMGateway(
            llm=self.llm,
            cost=self.cost,
            artifacts=self.artifacts,
            agent_loop=self.agent_loop,
            fallback_gateway=self.review_direct_llm_gateway,
        )
        self.review_llm_gateway = (
            self.review_agent_llm_gateway
            if settings.agent.enabled
            else self.review_direct_llm_gateway
        )

        self.review_comment_gateway = (
            ReviewDryRunCommentGateway(vcs=self.vcs, artifacts=self.artifacts)
            if settings.review.dry_run
            else ReviewCommentGateway(vcs=self.vcs, artifacts=self.artifacts)
        )

        self.inline_review_runner = InlineReviewRunner(
            vcs=self.vcs,
            git=self.git,
            diff=self.diff,
            cost=self.cost,
            prompt=self.prompt,
            policy=self.policy,
            inline_comment=self.inline_comment,
            review_llm_gateway=self.review_llm_gateway,
            review_comment_gateway=self.review_comment_gateway
        )
        self.context_review_runner = ContextReviewRunner(
            vcs=self.vcs,
            git=self.git,
            diff=self.diff,
            cost=self.cost,
            prompt=self.prompt,
            policy=self.policy,
            inline_comment=self.inline_comment,
            review_llm_gateway=self.review_llm_gateway,
            review_comment_gateway=self.review_comment_gateway
        )
        self.summary_review_runner = SummaryReviewRunner(
            vcs=self.vcs,
            git=self.git,
            diff=self.diff,
            cost=self.cost,
            prompt=self.prompt,
            policy=self.policy,
            summary_comment=self.summary_comment,
            review_llm_gateway=self.review_llm_gateway,
            review_comment_gateway=self.review_comment_gateway
        )
        self.inline_reply_review_runner = InlineReplyReviewRunner(
            vcs=self.vcs,
            git=self.git,
            diff=self.diff,
            cost=self.cost,
            prompt=self.prompt,
            policy=self.policy,
            review_llm_gateway=self.review_llm_gateway,
            inline_comment_reply=self.inline_comment_reply,
            review_comment_gateway=self.review_comment_gateway
        )
        self.summary_reply_review_runner = SummaryReplyReviewRunner(
            vcs=self.vcs,
            git=self.git,
            diff=self.diff,
            cost=self.cost,
            prompt=self.prompt,
            policy=self.policy,
            review_llm_gateway=self.review_llm_gateway,
            summary_comment_reply=self.summary_comment_reply,
            review_comment_gateway=self.review_comment_gateway
        )

    async def run_inline_review(self) -> None:
        await self.inline_review_runner.run()

    async def run_context_review(self) -> None:
        await self.context_review_runner.run()

    async def run_summary_review(self) -> None:
        await self.summary_review_runner.run()

    async def run_inline_reply_review(self) -> None:
        await self.inline_reply_review_runner.run()

    async def run_summary_reply_review(self) -> None:
        await self.summary_reply_review_runner.run()

    async def run_clear_inline_review(self) -> None:
        await self.review_comment_gateway.clear_inline_comments()

    async def run_clear_summary_review(self) -> None:
        await self.review_comment_gateway.clear_summary_comments()

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
