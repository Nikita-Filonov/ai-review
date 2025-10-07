import pytest

from ai_review.services.cost.types import CostServiceProtocol
from ai_review.services.diff.types import DiffServiceProtocol
from ai_review.services.git.types import GitServiceProtocol
from ai_review.services.prompt.types import PromptServiceProtocol
from ai_review.services.review.gateway.types import ReviewLLMGatewayProtocol, ReviewCommentGatewayProtocol
from ai_review.services.review.internal.inline_reply.types import InlineCommentReplyServiceProtocol
from ai_review.services.review.internal.policy.types import ReviewPolicyServiceProtocol
from ai_review.services.review.runner.inline_reply import InlineReplyReviewRunner
from ai_review.services.review.runner.types import ReviewRunnerProtocol
from ai_review.services.vcs.types import VCSClientProtocol


class FakeInlineReplyReviewRunner(ReviewRunnerProtocol):
    def __init__(self):
        self.calls = []

    async def run(self) -> None:
        self.calls.append(("run", {}))


@pytest.fixture
def fake_inline_reply_review_runner() -> FakeInlineReplyReviewRunner:
    return FakeInlineReplyReviewRunner()


@pytest.fixture
def inline_reply_review_runner(
        fake_vcs_client: VCSClientProtocol,
        fake_git_service: GitServiceProtocol,
        fake_diff_service: DiffServiceProtocol,
        fake_cost_service: CostServiceProtocol,
        fake_prompt_service: PromptServiceProtocol,
        fake_review_llm_gateway: ReviewLLMGatewayProtocol,
        fake_review_policy_service: ReviewPolicyServiceProtocol,
        fake_review_comment_gateway: ReviewCommentGatewayProtocol,
        fake_inline_comment_reply_service: InlineCommentReplyServiceProtocol,
) -> InlineReplyReviewRunner:
    return InlineReplyReviewRunner(
        vcs=fake_vcs_client,
        git=fake_git_service,
        diff=fake_diff_service,
        cost=fake_cost_service,
        prompt=fake_prompt_service,
        review_policy=fake_review_policy_service,
        review_llm_gateway=fake_review_llm_gateway,
        inline_comment_reply=fake_inline_comment_reply_service,
        review_comment_gateway=fake_review_comment_gateway,
    )
