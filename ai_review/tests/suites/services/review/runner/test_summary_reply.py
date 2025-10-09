import pytest

from ai_review.services.review.runner.summary_reply import SummaryReplyReviewRunner
from ai_review.services.vcs.types import ReviewInfoSchema, ReviewThreadSchema, ReviewCommentSchema, ThreadKind
from ai_review.tests.fixtures.services.cost import FakeCostService
from ai_review.tests.fixtures.services.diff import FakeDiffService
from ai_review.tests.fixtures.services.prompt import FakePromptService
from ai_review.tests.fixtures.services.review.gateway.review_comment_gateway import FakeReviewCommentGateway
from ai_review.tests.fixtures.services.review.gateway.review_llm_gateway import FakeReviewLLMGateway
from ai_review.tests.fixtures.services.review.internal.policy import FakeReviewPolicyService
from ai_review.tests.fixtures.services.review.internal.summary_reply import FakeSummaryCommentReplyService
from ai_review.tests.fixtures.services.vcs import FakeVCSClient


@pytest.mark.asyncio
async def test_run_happy_path(
        summary_reply_review_runner: SummaryReplyReviewRunner,
        fake_vcs_client: FakeVCSClient,
        fake_diff_service: FakeDiffService,
        fake_cost_service: FakeCostService,
        fake_prompt_service: FakePromptService,
        fake_review_llm_gateway: FakeReviewLLMGateway,
        fake_review_comment_gateway: FakeReviewCommentGateway,
):
    """Should process all summary threads, call LLM, and post replies."""
    await summary_reply_review_runner.run()

    vcs_calls = [call[0] for call in fake_vcs_client.calls]
    assert "get_review_info" in vcs_calls

    assert any(call[0] == "get_summary_threads" for call in fake_review_comment_gateway.calls)
    assert any(call[0] == "render_files" for call in fake_diff_service.calls)
    assert any(call[0] == "build_summary_reply_request" for call in fake_prompt_service.calls)
    assert any(call[0] == "ask" for call in fake_review_llm_gateway.calls)
    assert any(call[0] == "process_summary_reply" for call in fake_review_comment_gateway.calls)
    assert any(call[0] == "aggregate" for call in fake_cost_service.calls)


@pytest.mark.asyncio
async def test_run_skips_when_no_threads(
        summary_reply_review_runner: SummaryReplyReviewRunner,
        fake_review_comment_gateway: FakeReviewCommentGateway,
        fake_vcs_client: FakeVCSClient,
):
    """Should skip when there are no AI summary threads."""
    fake_review_comment_gateway.responses["get_summary_threads"] = []

    await summary_reply_review_runner.run()

    vcs_calls = [call[0] for call in fake_vcs_client.calls]
    assert "get_review_info" in vcs_calls
    assert any(call[0] == "get_summary_threads" for call in fake_review_comment_gateway.calls)
    assert not any(call[0] == "process_summary_reply" for call in fake_review_comment_gateway.calls)


@pytest.mark.asyncio
async def test_process_thread_reply_skips_when_no_allowed_files(
        summary_reply_review_runner: SummaryReplyReviewRunner,
        fake_review_policy_service: FakeReviewPolicyService,
        fake_review_comment_gateway: FakeReviewCommentGateway,
):
    """Should skip processing thread if policy filtered out all files."""
    fake_review_policy_service.responses["apply_for_files"] = []

    review_info = ReviewInfoSchema(base_sha="A", head_sha="B", changed_files=["a.py"])
    thread = ReviewThreadSchema(
        id="99",
        kind=ThreadKind.SUMMARY,
        comments=[ReviewCommentSchema(id="c1", body="Summary comment")],
    )

    await summary_reply_review_runner.process_thread_reply(thread, review_info)

    assert not any(call[0] == "process_summary_reply" for call in fake_review_comment_gateway.calls)


@pytest.mark.asyncio
async def test_process_thread_reply_skips_when_no_reply(
        summary_reply_review_runner: SummaryReplyReviewRunner,
        fake_summary_comment_reply_service: FakeSummaryCommentReplyService,
        fake_review_llm_gateway: FakeReviewLLMGateway,
        fake_review_comment_gateway: FakeReviewCommentGateway,
):
    """Should not post reply if model output produced no reply schema."""
    fake_summary_comment_reply_service.reply = None

    review_info = ReviewInfoSchema(base_sha="A", head_sha="B", changed_files=["x.py"])
    thread = ReviewThreadSchema(
        id="42",
        kind=ThreadKind.SUMMARY,
        comments=[ReviewCommentSchema(id="cm1", body="AI summary comment")],
    )

    await summary_reply_review_runner.process_thread_reply(thread, review_info)

    assert any(call[0] == "ask" for call in fake_review_llm_gateway.calls)
    assert not any(call[0] == "process_summary_reply" for call in fake_review_comment_gateway.calls)
