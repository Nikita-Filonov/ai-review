import pytest

from ai_review.services.review.runner.inline_reply import InlineReplyReviewRunner
from ai_review.services.vcs.types import ReviewInfoSchema, ReviewThreadSchema, ReviewCommentSchema, ThreadKind
from ai_review.tests.fixtures.services.cost import FakeCostService
from ai_review.tests.fixtures.services.diff import FakeDiffService
from ai_review.tests.fixtures.services.git import FakeGitService
from ai_review.tests.fixtures.services.prompt import FakePromptService
from ai_review.tests.fixtures.services.review.gateway.review_comment_gateway import FakeReviewCommentGateway
from ai_review.tests.fixtures.services.review.gateway.review_llm_gateway import FakeReviewLLMGateway
from ai_review.tests.fixtures.services.review.internal.inline_reply import FakeInlineCommentReplyService
from ai_review.tests.fixtures.services.vcs import FakeVCSClient


@pytest.mark.asyncio
async def test_run_happy_path(
        inline_reply_review_runner: InlineReplyReviewRunner,
        fake_vcs_client: FakeVCSClient,
        fake_git_service: FakeGitService,
        fake_cost_service: FakeCostService,
        fake_diff_service: FakeDiffService,
        fake_prompt_service: FakePromptService,
        fake_review_llm_gateway: FakeReviewLLMGateway,
        fake_review_comment_gateway: FakeReviewCommentGateway,
):
    """Should process all threads, call LLM, and post replies."""
    fake_git_service.responses["get_diff_for_file"] = "FAKE_DIFF"

    await inline_reply_review_runner.run()

    vcs_calls = [call[0] for call in fake_vcs_client.calls]
    assert "get_review_info" in vcs_calls

    assert any(call[0] == "get_inline_threads" for call in fake_review_comment_gateway.calls)
    assert any(call[0] == "get_diff_for_file" for call in fake_git_service.calls)
    assert any(call[0] == "render_file" for call in fake_diff_service.calls)
    assert any(call[0] == "build_inline_reply_request" for call in fake_prompt_service.calls)
    assert any(call[0] == "ask" for call in fake_review_llm_gateway.calls)
    assert any(call[0] == "process_inline_reply" for call in fake_review_comment_gateway.calls)
    assert any(call[0] == "aggregate" for call in fake_cost_service.calls)


@pytest.mark.asyncio
async def test_run_skips_when_no_threads(
        fake_vcs_client: FakeVCSClient,
        inline_reply_review_runner: InlineReplyReviewRunner,
        fake_review_comment_gateway: FakeReviewCommentGateway,
):
    """Should skip when there are no AI inline threads."""
    fake_review_comment_gateway.responses["get_inline_threads"] = []

    await inline_reply_review_runner.run()

    vcs_calls = [call[0] for call in fake_vcs_client.calls]
    assert "get_review_info" in vcs_calls
    assert any(call[0] == "get_inline_threads" for call in fake_review_comment_gateway.calls)
    assert not any(call[0] == "process_inline_reply" for call in fake_review_comment_gateway.calls)


@pytest.mark.asyncio
async def test_process_thread_reply_skips_when_no_diff(
        inline_reply_review_runner: InlineReplyReviewRunner,
        fake_git_service: FakeGitService,
        fake_review_llm_gateway: FakeReviewLLMGateway,
        fake_review_comment_gateway: FakeReviewCommentGateway,
):
    """Should skip reply processing when no diff found for file."""
    fake_git_service.responses["get_diff_for_file"] = ""

    review_info = ReviewInfoSchema(base_sha="A", head_sha="B")
    thread = ReviewThreadSchema(
        id="1",
        kind=ThreadKind.INLINE,
        file="file.py",
        line=1,
        comments=[ReviewCommentSchema(id="c1", body="Some comment")]
    )

    await inline_reply_review_runner.process_thread_reply(thread, review_info)

    assert not any(call[0] == "ask" for call in fake_review_llm_gateway.calls)
    assert not any(call[0] == "process_inline_reply" for call in fake_review_comment_gateway.calls)


@pytest.mark.asyncio
async def test_process_thread_reply_skips_when_no_reply(
        inline_reply_review_runner: InlineReplyReviewRunner,
        fake_git_service: FakeGitService,
        fake_review_llm_gateway: FakeReviewLLMGateway,
        fake_review_comment_gateway: FakeReviewCommentGateway,
        fake_inline_comment_reply_service: FakeInlineCommentReplyService,
):
    """Should not post reply if model output produces no reply schema."""
    fake_git_service.responses["get_diff_for_file"] = "SOME_DIFF"
    fake_inline_comment_reply_service.reply = None

    review_info = ReviewInfoSchema(base_sha="A", head_sha="B")
    thread = ReviewThreadSchema(
        id="42",
        kind=ThreadKind.INLINE,
        file="main.py",
        line=12,
        comments=[ReviewCommentSchema(id="cm1", body="Fix this!")]
    )

    await inline_reply_review_runner.process_thread_reply(thread, review_info)

    assert any(call[0] == "ask" for call in fake_review_llm_gateway.calls)
    assert not any(call[0] == "process_inline_reply" for call in fake_review_comment_gateway.calls)
