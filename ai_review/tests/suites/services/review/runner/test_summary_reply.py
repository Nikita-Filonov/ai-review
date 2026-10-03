import pytest

from ai_review.config import settings
from ai_review.services.prompt.service import PromptService
from ai_review.services.review.gateway.review_comment_gateway import ReviewCommentGateway
from ai_review.services.review.internal.summary_reply.service import SummaryCommentReplyService
from ai_review.services.review.internal.summary_reply.tools import get_summary_reply_reference
from ai_review.services.review.runner.summary_reply import SummaryReplyReviewRunner
from ai_review.services.vcs.types import ReviewInfoSchema, ReviewThreadSchema, ReviewCommentSchema, ThreadKind
from ai_review.tests.fixtures.services.cost import FakeCostService
from ai_review.tests.fixtures.services.diff import FakeDiffService
from ai_review.tests.fixtures.services.policy import FakePolicyService
from ai_review.tests.fixtures.services.prompt import FakePromptService
from ai_review.tests.fixtures.services.review.gateway.review_comment_gateway import FakeReviewCommentGateway
from ai_review.tests.fixtures.services.review.gateway.review_direct_llm_gateway import FakeReviewDirectLLMGateway
from ai_review.tests.fixtures.services.review.internal.summary_reply import FakeSummaryCommentReplyService
from ai_review.tests.fixtures.services.vcs import FakeVCSClient


@pytest.mark.asyncio
async def test_run_happy_path(
        summary_reply_review_runner: SummaryReplyReviewRunner,
        fake_vcs_client: FakeVCSClient,
        fake_diff_service: FakeDiffService,
        fake_cost_service: FakeCostService,
        fake_prompt_service: FakePromptService,
        fake_review_comment_gateway: FakeReviewCommentGateway,
        fake_review_direct_llm_gateway: FakeReviewDirectLLMGateway,
):
    """Should process all summary threads, call LLM, and post replies."""
    await summary_reply_review_runner.run()

    vcs_calls = [call[0] for call in fake_vcs_client.calls]
    assert "get_review_info" in vcs_calls

    assert any(call[0] == "get_summary_threads" for call in fake_review_comment_gateway.calls)
    assert any(call[0] == "render_files" for call in fake_diff_service.calls)
    assert any(call[0] == "build_summary_reply_request" for call in fake_prompt_service.calls)
    assert any(call[0] == "ask" for call in fake_review_direct_llm_gateway.calls)
    reply_call = next(call for call in fake_review_comment_gateway.calls if call[0] == "process_summary_reply")
    assert reply_call[1]["thread_id"] == "t2"
    assert reply_call[1]["request_comment_id"] == "c4"
    assert any(call[0] == "aggregate" for call in fake_cost_service.calls)


@pytest.mark.asyncio
async def test_run_skips_when_no_threads(
        fake_vcs_client: FakeVCSClient,
        fake_review_comment_gateway: FakeReviewCommentGateway,
        summary_reply_review_runner: SummaryReplyReviewRunner,
):
    """Should skip when there are no AI summary threads."""
    fake_review_comment_gateway.responses["get_summary_threads"] = []

    await summary_reply_review_runner.run()

    vcs_calls = [call[0] for call in fake_vcs_client.calls]
    assert "get_review_info" in vcs_calls
    assert any(call[0] == "get_summary_threads" for call in fake_review_comment_gateway.calls)
    assert not any(call[0] == "process_summary_reply" for call in fake_review_comment_gateway.calls)


@pytest.mark.asyncio
@pytest.mark.parametrize("layout", ["flat", "threaded", "threaded_separate_reply"])
async def test_summary_replies_once_per_request_and_allows_follow_up(
        layout: str,
        monkeypatch: pytest.MonkeyPatch,
        summary_reply_review_runner: SummaryReplyReviewRunner,
        review_comment_gateway: ReviewCommentGateway,
        fake_vcs_client: FakeVCSClient,
        fake_review_direct_llm_gateway: FakeReviewDirectLLMGateway,
        fake_prompts: None,
):
    summary_reply_review_runner.review_comment_gateway = review_comment_gateway
    summary_reply_review_runner.summary_comment_reply = SummaryCommentReplyService()
    summary_reply_review_runner.prompt = PromptService()
    fake_review_direct_llm_gateway.responses["ask"] = "Add a null check."

    summary = ReviewCommentSchema(id=1, body=f"Possible NPE. {settings.review.summary_tag}")
    question = ReviewCommentSchema(id=2, body=f"Why? {settings.review.summary_reply_tag}")
    thread = ReviewThreadSchema(
        id="request", kind=ThreadKind.SUMMARY,
        comments=[question] if layout == "flat" else [summary, question],
    )
    threads = [thread]
    if layout == "flat":
        threads.append(ReviewThreadSchema(id="summary", kind=ThreadKind.SUMMARY, comments=[summary]))
    fake_vcs_client.responses["get_general_threads"] = threads
    create_summary_reply = fake_vcs_client.create_summary_reply

    async def store_reply(thread_id: str | int, message: str):
        await create_summary_reply(thread_id, message)
        reply = ReviewCommentSchema(id=f"answer-{len(fake_vcs_client.calls)}", body=message)
        if layout == "threaded":
            thread.comments.append(reply)
        else:
            threads.append(ReviewThreadSchema(id=reply.id, kind=ThreadKind.SUMMARY, comments=[reply]))

    monkeypatch.setattr(fake_vcs_client, "create_summary_reply", store_reply)

    await summary_reply_review_runner.run()
    assert len(fake_review_direct_llm_gateway.calls) == 1
    first_reply = next(call for call in fake_vcs_client.calls if call[0] == "create_summary_reply")
    assert first_reply[1][0] == "request"
    assert get_summary_reply_reference(first_reply[1][1]) == ("request", "2")
    assert settings.review.summary_reply_tag not in first_reply[1][1]

    # Recreate the gateway: acknowledgement must survive a new process.
    summary_reply_review_runner.review_comment_gateway = ReviewCommentGateway(
        vcs=fake_vcs_client, artifacts=review_comment_gateway.artifacts,
    )
    await summary_reply_review_runner.run()
    assert len(fake_review_direct_llm_gateway.calls) == 1

    untagged = ReviewCommentSchema(id=3, body="What about a guard?")
    follow_up = ReviewCommentSchema(id=4, body=f"Would a guard help? {settings.review.summary_reply_tag}")
    if layout == "flat":
        threads.append(ReviewThreadSchema(id="untagged", kind=ThreadKind.SUMMARY, comments=[untagged]))
    else:
        thread.comments.append(untagged)
    await summary_reply_review_runner.run()
    assert len(fake_review_direct_llm_gateway.calls) == 1

    if layout == "flat":
        threads.append(ReviewThreadSchema(id="follow-up", kind=ThreadKind.SUMMARY, comments=[follow_up]))
    else:
        thread.comments.append(follow_up)
    await summary_reply_review_runner.run()
    assert len(fake_review_direct_llm_gateway.calls) == 2

    prompt = fake_review_direct_llm_gateway.calls[-1][1]["prompt"]
    assert "Would a guard help?" in prompt
    if layout != "flat":
        history = ["Possible NPE.", "Why?", "What about a guard?", "Would a guard help?"]
        positions = [prompt.index(message) for message in history]
        assert positions == sorted(positions)
    if layout == "threaded":
        assert prompt.index("Why?") < prompt.index("Add a null check.") < prompt.index("What about a guard?")

    await summary_reply_review_runner.run()
    assert len(fake_review_direct_llm_gateway.calls) == 2
    replies = [call for call in fake_vcs_client.calls if call[0] == "create_summary_reply"]
    expected_thread = "follow-up" if layout == "flat" else "request"
    assert get_summary_reply_reference(replies[-1][1][1]) == (expected_thread, "4")


@pytest.mark.asyncio
@pytest.mark.parametrize("output", ["No reply", "No reply.", "", " \n "])
async def test_empty_summary_reply_is_not_posted_or_acknowledged(
        output: str,
        summary_reply_review_runner: SummaryReplyReviewRunner,
        review_comment_gateway: ReviewCommentGateway,
        fake_vcs_client: FakeVCSClient,
        fake_review_direct_llm_gateway: FakeReviewDirectLLMGateway,
):
    summary_reply_review_runner.review_comment_gateway = review_comment_gateway
    summary_reply_review_runner.summary_comment_reply = SummaryCommentReplyService()
    fake_review_direct_llm_gateway.responses["ask"] = output
    thread = ReviewThreadSchema(
        id="t1", kind=ThreadKind.SUMMARY,
        comments=[ReviewCommentSchema(id="c1", body=f"Question {settings.review.summary_reply_tag}")],
    )
    fake_vcs_client.responses["get_general_threads"] = [thread]

    await summary_reply_review_runner.run()

    assert len(fake_review_direct_llm_gateway.calls) == 1
    assert not any(call[0] == "create_summary_reply" for call in fake_vcs_client.calls)
    assert await review_comment_gateway.get_summary_threads() == [thread]


@pytest.mark.asyncio
async def test_failed_summary_publication_can_be_retried(
        summary_reply_review_runner: SummaryReplyReviewRunner,
        review_comment_gateway: ReviewCommentGateway,
        fake_vcs_client: FakeVCSClient,
        fake_review_direct_llm_gateway: FakeReviewDirectLLMGateway,
):
    summary_reply_review_runner.review_comment_gateway = review_comment_gateway
    thread = ReviewThreadSchema(
        id="t1", kind=ThreadKind.SUMMARY,
        comments=[ReviewCommentSchema(id="c1", body=f"Question {settings.review.summary_reply_tag}")],
    )
    fake_vcs_client.responses["get_general_threads"] = [thread]
    fake_vcs_client.responses["create_summary_reply_error"] = RuntimeError("Publication failed")

    await summary_reply_review_runner.run()
    assert await review_comment_gateway.get_summary_threads() == [thread]

    del fake_vcs_client.responses["create_summary_reply_error"]
    await summary_reply_review_runner.run()
    assert len(fake_review_direct_llm_gateway.calls) == 2
    assert len([call for call in fake_vcs_client.calls if call[0] == "create_summary_reply"]) == 2


@pytest.mark.asyncio
async def test_process_empty_summary_thread_skips_llm(
        summary_reply_review_runner: SummaryReplyReviewRunner,
        fake_review_direct_llm_gateway: FakeReviewDirectLLMGateway,
):
    thread = ReviewThreadSchema(id="t1", kind=ThreadKind.SUMMARY, comments=[])
    await summary_reply_review_runner.process_thread_reply(thread, ReviewInfoSchema(changed_files=["a.py"]))

    assert fake_review_direct_llm_gateway.calls == []


@pytest.mark.asyncio
async def test_process_thread_reply_skips_when_no_allowed_files(
        fake_policy_service: FakePolicyService,
        fake_review_comment_gateway: FakeReviewCommentGateway,
        summary_reply_review_runner: SummaryReplyReviewRunner,
):
    """Should skip processing thread if policy filtered out all files."""
    fake_policy_service.responses["apply_for_files"] = []

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
        fake_review_comment_gateway: FakeReviewCommentGateway,
        fake_review_direct_llm_gateway: FakeReviewDirectLLMGateway,
        fake_summary_comment_reply_service: FakeSummaryCommentReplyService,
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

    assert any(call[0] == "ask" for call in fake_review_direct_llm_gateway.calls)
    assert not any(call[0] == "process_summary_reply" for call in fake_review_comment_gateway.calls)
