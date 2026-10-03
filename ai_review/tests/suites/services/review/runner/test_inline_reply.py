import pytest

from ai_review.config import settings
from ai_review.services.prompt.service import PromptService
from ai_review.services.review.gateway.review_comment_gateway import ReviewCommentGateway
from ai_review.services.review.internal.inline_reply.schema import InlineCommentReplySchema
from ai_review.services.review.internal.inline_reply.service import InlineCommentReplyService
from ai_review.services.review.runner.inline_reply import InlineReplyReviewRunner
from ai_review.services.vcs.types import ReviewInfoSchema, ReviewThreadSchema, ReviewCommentSchema, ThreadKind
from ai_review.tests.fixtures.services.cost import FakeCostService
from ai_review.tests.fixtures.services.diff import FakeDiffService
from ai_review.tests.fixtures.services.git import FakeGitService
from ai_review.tests.fixtures.services.prompt import FakePromptService
from ai_review.tests.fixtures.services.review.gateway.review_comment_gateway import FakeReviewCommentGateway
from ai_review.tests.fixtures.services.review.gateway.review_direct_llm_gateway import FakeReviewDirectLLMGateway
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
        fake_review_comment_gateway: FakeReviewCommentGateway,
        fake_review_direct_llm_gateway: FakeReviewDirectLLMGateway,
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
    assert any(call[0] == "ask" for call in fake_review_direct_llm_gateway.calls)
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
        fake_review_comment_gateway: FakeReviewCommentGateway,
        fake_review_direct_llm_gateway: FakeReviewDirectLLMGateway,
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

    assert not any(call[0] == "ask" for call in fake_review_direct_llm_gateway.calls)
    assert not any(call[0] == "process_inline_reply" for call in fake_review_comment_gateway.calls)


@pytest.mark.asyncio
async def test_process_thread_reply_skips_when_no_reply(
        inline_reply_review_runner: InlineReplyReviewRunner,
        fake_git_service: FakeGitService,
        fake_review_comment_gateway: FakeReviewCommentGateway,
        fake_review_direct_llm_gateway: FakeReviewDirectLLMGateway,
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

    assert any(call[0] == "ask" for call in fake_review_direct_llm_gateway.calls)
    assert not any(call[0] == "process_inline_reply" for call in fake_review_comment_gateway.calls)


@pytest.mark.asyncio
@pytest.mark.usefixtures("fake_prompts")
async def test_reply_runs_preserve_history_without_reanswering_handled_threads(
        monkeypatch: pytest.MonkeyPatch,
        inline_reply_review_runner: InlineReplyReviewRunner,
        review_comment_gateway: ReviewCommentGateway,
        fake_vcs_client: FakeVCSClient,
        fake_git_service: FakeGitService,
        fake_review_direct_llm_gateway: FakeReviewDirectLLMGateway,
):
    """A later run answers only new requests and includes the complete conversation."""
    inline_reply_review_runner.review_comment_gateway = review_comment_gateway
    inline_reply_review_runner.inline_comment_reply = InlineCommentReplyService()
    inline_reply_review_runner.prompt = PromptService()
    fake_git_service.responses["get_diff_for_file"] = "SOME_DIFF"
    fake_review_direct_llm_gateway.responses["ask"] = '{"message": "The value can be null."}'
    thread = ReviewThreadSchema(
        id="thread-1",
        kind=ThreadKind.INLINE,
        file="main.py",
        comments=[
            ReviewCommentSchema(id=1, body=f"Possible NPE.\n\n{settings.review.inline_tag}"),
            ReviewCommentSchema(id=2, body=f"Why? {settings.review.inline_reply_tag}"),
        ],
    )
    handled_thread = ReviewThreadSchema(
        id="thread-2",
        kind=ThreadKind.INLINE,
        file="other.py",
        comments=[
            ReviewCommentSchema(id=3, body=f"Old question {settings.review.inline_reply_tag}"),
            ReviewCommentSchema(id=4, body=f"Old answer\n\n{settings.review.inline_tag}"),
        ],
    )
    fake_vcs_client.responses["get_inline_threads"] = [thread, handled_thread]
    create_inline_reply = fake_vcs_client.create_inline_reply

    async def store_reply(thread_id: str | int, message: str):
        await create_inline_reply(thread_id, message)
        target = next(t for t in fake_vcs_client.responses["get_inline_threads"] if t.id == thread_id)
        target.comments.append(ReviewCommentSchema(id=len(target.comments) + 10, body=message))

    monkeypatch.setattr(fake_vcs_client, "create_inline_reply", store_reply)

    await inline_reply_review_runner.run()
    assert thread.comments[-1].body == InlineCommentReplySchema(message="The value can be null.").body_with_tag
    assert len(fake_review_direct_llm_gateway.calls) == 1

    await inline_reply_review_runner.run()
    assert len(fake_review_direct_llm_gateway.calls) == 1

    thread.comments.append(ReviewCommentSchema(id=20, body="What about a guard?"))
    await inline_reply_review_runner.run()
    assert len(fake_review_direct_llm_gateway.calls) == 1

    thread.comments.append(ReviewCommentSchema(
        id=21, body=f"Would a null check help? {settings.review.inline_reply_tag}",
    ))
    await inline_reply_review_runner.run()
    assert len(fake_review_direct_llm_gateway.calls) == 2
    prompt = fake_review_direct_llm_gateway.calls[-1][1]["prompt"]
    history = [
        "Possible NPE.", "Why?", "The value can be null.",
        "What about a guard?", "Would a null check help?",
    ]
    positions = [prompt.index(message) for message in history]
    assert positions == sorted(positions)
    assert "Old question" not in prompt
    replies = [call for call in fake_vcs_client.calls if call[0] == "create_inline_reply"]
    assert [call[1][0] for call in replies] == ["thread-1", "thread-1"]


@pytest.mark.asyncio
@pytest.mark.parametrize("output", ['{"message": "No reply.", "suggestion": null}', "No reply."])
async def test_no_reply_output_never_reaches_vcs(
        output: str,
        inline_reply_review_runner: InlineReplyReviewRunner,
        review_comment_gateway: ReviewCommentGateway,
        fake_vcs_client: FakeVCSClient,
        fake_git_service: FakeGitService,
        fake_review_direct_llm_gateway: FakeReviewDirectLLMGateway,
):
    inline_reply_review_runner.review_comment_gateway = review_comment_gateway
    inline_reply_review_runner.inline_comment_reply = InlineCommentReplyService()
    fake_git_service.responses["get_diff_for_file"] = "SOME_DIFF"
    fake_review_direct_llm_gateway.responses["ask"] = output
    fake_vcs_client.responses["get_inline_threads"] = [ReviewThreadSchema(
        id="thread-1",
        kind=ThreadKind.INLINE,
        file="main.py",
        comments=[ReviewCommentSchema(id=1, body=f"Question {settings.review.inline_reply_tag}")],
    )]

    await inline_reply_review_runner.run()

    assert len(fake_review_direct_llm_gateway.calls) == 1
    assert not any(call[0] == "create_inline_reply" for call in fake_vcs_client.calls)
