import pytest

from ai_review.services.review.runner.context import ContextReviewRunner
from ai_review.tests.fixtures.services.cost import FakeCostService
from ai_review.tests.fixtures.services.diff import FakeDiffService
from ai_review.tests.fixtures.services.prompt import FakePromptService
from ai_review.tests.fixtures.services.review.gateway.review_comment_gateway import FakeReviewCommentGateway
from ai_review.tests.fixtures.services.review.gateway.review_llm_gateway import FakeReviewLLMGateway
from ai_review.tests.fixtures.services.review.internal.inline import FakeInlineCommentService
from ai_review.tests.fixtures.services.review.internal.policy import FakeReviewPolicyService
from ai_review.tests.fixtures.services.vcs import FakeVCSClient


@pytest.mark.asyncio
async def test_run_happy_path(
        context_review_runner: ContextReviewRunner,
        fake_vcs_client: FakeVCSClient,
        fake_diff_service: FakeDiffService,
        fake_cost_service: FakeCostService,
        fake_prompt_service: FakePromptService,
        fake_review_llm_gateway: FakeReviewLLMGateway,
        fake_review_policy_service: FakeReviewPolicyService,
        fake_review_comment_gateway: FakeReviewCommentGateway,
):
    """Should render all changed files, call LLM and post inline comments."""
    await context_review_runner.run()

    vcs_calls = [call[0] for call in fake_vcs_client.calls]
    assert "get_review_info" in vcs_calls

    assert any(call[0] == "render_files" for call in fake_diff_service.calls)
    assert any(call[0] == "apply_for_files" for call in fake_review_policy_service.calls)
    assert any(call[0] == "build_context_request" for call in fake_prompt_service.calls)
    assert any(call[0] == "ask" for call in fake_review_llm_gateway.calls)
    assert any(call[0] == "process_inline_comments" for call in fake_review_comment_gateway.calls)

    assert any(call[0] == "aggregate" for call in fake_cost_service.calls)


@pytest.mark.asyncio
async def test_run_skips_when_existing_comments(
        context_review_runner: ContextReviewRunner,
        fake_vcs_client: FakeVCSClient,
        fake_review_llm_gateway: FakeReviewLLMGateway,
        fake_review_comment_gateway: FakeReviewCommentGateway,
):
    """Should skip context review if inline comments already exist."""
    fake_review_comment_gateway.responses["has_existing_inline_comments"] = True

    await context_review_runner.run()

    vcs_calls = [call[0] for call in fake_vcs_client.calls]
    assert vcs_calls == []
    assert not any(call[0] == "ask" for call in fake_review_llm_gateway.calls)


@pytest.mark.asyncio
async def test_run_skips_when_no_changed_files(
        context_review_runner: ContextReviewRunner,
        fake_vcs_client: FakeVCSClient,
        fake_review_policy_service: FakeReviewPolicyService,
):
    """Should skip when no changed files after policy filtering."""
    fake_review_policy_service.responses["apply_for_files"] = []

    await context_review_runner.run()

    vcs_calls = [call[0] for call in fake_vcs_client.calls]
    assert "get_review_info" in vcs_calls
    assert any(call[0] == "apply_for_files" for call in fake_review_policy_service.calls)


@pytest.mark.asyncio
async def test_run_skips_when_no_comments_after_llm(
        context_review_runner: ContextReviewRunner,
        fake_review_llm_gateway: FakeReviewLLMGateway,
        fake_review_policy_service: FakeReviewPolicyService,
        fake_review_comment_gateway: FakeReviewCommentGateway,
        fake_inline_comment_service: FakeInlineCommentService,

):
    """Should not post comments if LLM output is empty."""
    fake_inline_comment_service.comments = []

    await context_review_runner.run()

    assert any(call[0] == "ask" for call in fake_review_llm_gateway.calls)
    assert any(call[0] == "apply_for_context_comments" for call in fake_review_policy_service.calls)
    assert not any(call[0] == "process_inline_comments" for call in fake_review_comment_gateway.calls)
