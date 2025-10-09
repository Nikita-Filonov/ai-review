import pytest

from ai_review.services.review.internal.summary.schema import SummaryCommentSchema
from ai_review.services.review.runner.summary import SummaryReviewRunner
from ai_review.tests.fixtures.services.cost import FakeCostService
from ai_review.tests.fixtures.services.diff import FakeDiffService
from ai_review.tests.fixtures.services.prompt import FakePromptService
from ai_review.tests.fixtures.services.review.gateway.review_comment_gateway import FakeReviewCommentGateway
from ai_review.tests.fixtures.services.review.gateway.review_llm_gateway import FakeReviewLLMGateway
from ai_review.tests.fixtures.services.review.internal.policy import FakeReviewPolicyService
from ai_review.tests.fixtures.services.review.internal.summary import FakeSummaryCommentService
from ai_review.tests.fixtures.services.vcs import FakeVCSClient


@pytest.mark.asyncio
async def test_run_happy_path(
        summary_review_runner: SummaryReviewRunner,
        fake_vcs_client: FakeVCSClient,
        fake_diff_service: FakeDiffService,
        fake_cost_service: FakeCostService,
        fake_prompt_service: FakePromptService,
        fake_review_llm_gateway: FakeReviewLLMGateway,
        fake_review_policy_service: FakeReviewPolicyService,
        fake_review_comment_gateway: FakeReviewCommentGateway,
):
    """Should render all changed files, call LLM and post summary comment."""
    await summary_review_runner.run()

    vcs_calls = [call[0] for call in fake_vcs_client.calls]
    assert "get_review_info" in vcs_calls

    assert any(call[0] == "render_files" for call in fake_diff_service.calls)
    assert any(call[0] == "apply_for_files" for call in fake_review_policy_service.calls)
    assert any(call[0] == "build_summary_request" for call in fake_prompt_service.calls)
    assert any(call[0] == "ask" for call in fake_review_llm_gateway.calls)
    assert any(call[0] == "process_summary_comment" for call in fake_review_comment_gateway.calls)

    assert any(call[0] == "aggregate" for call in fake_cost_service.calls)


@pytest.mark.asyncio
async def test_run_skips_when_existing_summary_comments(
        summary_review_runner: SummaryReviewRunner,
        fake_vcs_client: FakeVCSClient,
        fake_review_llm_gateway: FakeReviewLLMGateway,
        fake_review_comment_gateway: FakeReviewCommentGateway,
):
    """Should skip summary review if summary comment already exists."""
    fake_review_comment_gateway.responses["has_existing_summary_comments"] = True

    await summary_review_runner.run()

    vcs_calls = [call[0] for call in fake_vcs_client.calls]
    assert vcs_calls == []
    assert not any(call[0] == "ask" for call in fake_review_llm_gateway.calls)


@pytest.mark.asyncio
async def test_run_skips_when_no_changed_files(
        summary_review_runner: SummaryReviewRunner,
        fake_vcs_client: FakeVCSClient,
        fake_review_policy_service: FakeReviewPolicyService,
):
    """Should skip when no changed files remain after policy filtering."""
    fake_review_policy_service.responses["apply_for_files"] = []

    await summary_review_runner.run()

    vcs_calls = [call[0] for call in fake_vcs_client.calls]
    assert "get_review_info" in vcs_calls
    assert any(call[0] == "apply_for_files" for call in fake_review_policy_service.calls)


@pytest.mark.asyncio
async def test_run_skips_when_empty_summary_from_llm(
        summary_review_runner: SummaryReviewRunner,
        fake_review_llm_gateway: FakeReviewLLMGateway,
        fake_review_comment_gateway: FakeReviewCommentGateway,
        fake_summary_comment_service: FakeSummaryCommentService,
):
    """Should skip posting comment if LLM output is empty."""
    fake_summary_comment_service.responses["parse_model_output"] = SummaryCommentSchema(text="")

    await summary_review_runner.run()

    assert any(call[0] == "ask" for call in fake_review_llm_gateway.calls)
    assert not any(call[0] == "process_summary_comment" for call in fake_review_comment_gateway.calls)
