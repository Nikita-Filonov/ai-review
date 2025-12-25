import pytest

from ai_review.config import settings
from ai_review.services.review.gateway.review_comment_gateway import ReviewCommentGateway
from ai_review.services.review.internal.inline.schema import InlineCommentSchema, InlineCommentListSchema
from ai_review.services.review.internal.inline_reply.schema import InlineCommentReplySchema
from ai_review.services.review.internal.summary.schema import SummaryCommentSchema
from ai_review.services.review.internal.summary_reply.schema import SummaryCommentReplySchema
from ai_review.services.vcs.types import ReviewThreadSchema, ReviewCommentSchema, ThreadKind
from ai_review.tests.fixtures.services.artifacts import FakeArtifactsService
from ai_review.tests.fixtures.services.vcs import FakeVCSClient


# === INLINE THREADS ===

@pytest.mark.asyncio
async def test_get_inline_threads_filters_by_tag(
        fake_vcs_client: FakeVCSClient,
        review_comment_gateway: ReviewCommentGateway,
):
    """Should return only threads containing AI inline tags."""
    threads = [
        ReviewThreadSchema(
            id="1",
            kind=ThreadKind.INLINE,
            file="a.py",
            comments=[ReviewCommentSchema(id="1", body=f"Hello {settings.review.inline_reply_tag}")]
        ),
        ReviewThreadSchema(
            id="2",
            kind=ThreadKind.INLINE,
            file="b.py",
            comments=[ReviewCommentSchema(id="2", body="No AI tag here")]
        ),
    ]
    fake_vcs_client.responses["get_inline_threads"] = threads

    result = await review_comment_gateway.get_inline_threads()

    assert len(result) == 1
    assert result[0].id == "1"
    assert any(call[0] == "get_inline_threads" for call in fake_vcs_client.calls)


@pytest.mark.asyncio
async def test_get_summary_threads_filters_by_tag(
        fake_vcs_client: FakeVCSClient,
        review_comment_gateway: ReviewCommentGateway,
):
    """Should return only threads containing AI summary tags."""
    threads = [
        ReviewThreadSchema(
            id="10",
            kind=ThreadKind.SUMMARY,
            comments=[ReviewCommentSchema(id="1", body=f"AI {settings.review.summary_reply_tag}")]
        ),
        ReviewThreadSchema(
            id="11",
            kind=ThreadKind.SUMMARY,
            comments=[ReviewCommentSchema(id="2", body="No tags here")]
        ),
    ]
    fake_vcs_client.responses["get_general_threads"] = threads

    result = await review_comment_gateway.get_summary_threads()

    assert len(result) == 1
    assert result[0].id == "10"
    assert any(call[0] == "get_general_threads" for call in fake_vcs_client.calls)


# === EXISTING COMMENTS ===

@pytest.mark.asyncio
async def test_has_existing_inline_comments_true(
        capsys: pytest.CaptureFixture,
        fake_vcs_client: FakeVCSClient,
        review_comment_gateway: ReviewCommentGateway,
):
    """Should detect existing inline comments and log skip message."""
    fake_vcs_client.responses["get_inline_comments"] = [
        ReviewCommentSchema(id="1", body=f"{settings.review.inline_tag} existing comment")
    ]

    result = await review_comment_gateway.has_existing_inline_comments()
    output = capsys.readouterr().out

    assert result is True
    assert "AI inline comments already exist" in output


@pytest.mark.asyncio
async def test_has_existing_summary_comments_false(
        fake_vcs_client: FakeVCSClient,
        review_comment_gateway: ReviewCommentGateway,
):
    """Should return False when no summary AI comments exist."""
    fake_vcs_client.responses["get_general_comments"] = [
        ReviewCommentSchema(id="1", body="Regular comment")
    ]
    result = await review_comment_gateway.has_existing_summary_comments()
    assert result is False


# === INLINE REPLY ===

@pytest.mark.asyncio
async def test_process_inline_reply_happy_path(
        fake_vcs_client: FakeVCSClient,
        fake_artifacts_service: FakeArtifactsService,
        review_comment_gateway: ReviewCommentGateway,
):
    """Should create inline reply and emit hook events."""
    reply = InlineCommentReplySchema(message="AI reply text")

    await review_comment_gateway.process_inline_reply("t1", reply)

    assert any(call[0] == "create_inline_reply" for call in fake_vcs_client.calls)

    assert ("save_vcs_inline_reply", {"thread_id": "t1", "reply": reply}) in fake_artifacts_service.calls


@pytest.mark.asyncio
async def test_process_inline_reply_error(
        capsys: pytest.CaptureFixture,
        fake_vcs_client: FakeVCSClient,
        fake_artifacts_service: FakeArtifactsService,
        review_comment_gateway: ReviewCommentGateway,
):
    """Should log and emit error if VCS fails to create reply."""

    async def failing_create_inline_reply(thread_id: str, body: str):
        raise RuntimeError("API error")

    fake_vcs_client.create_inline_reply = failing_create_inline_reply

    reply = InlineCommentReplySchema(message="AI reply text")
    await review_comment_gateway.process_inline_reply("t1", reply)
    output = capsys.readouterr().out

    assert "Failed to create inline reply" in output

    assert all(call[0] != "save_vcs_inline_reply" for call in fake_artifacts_service.calls)


# === SUMMARY REPLY ===

@pytest.mark.asyncio
async def test_process_summary_reply_success(
        fake_vcs_client: FakeVCSClient,
        fake_artifacts_service: FakeArtifactsService,
        review_comment_gateway: ReviewCommentGateway,
):
    """Should create summary reply comment."""
    reply = SummaryCommentReplySchema(text="AI summary reply")
    await review_comment_gateway.process_summary_reply("t42", reply)
    assert any(call[0] == "create_summary_reply" for call in fake_vcs_client.calls)

    assert ("save_vcs_summary_reply", {"thread_id": "t42", "reply": reply}) in fake_artifacts_service.calls


@pytest.mark.asyncio
async def test_process_summary_reply_error(
        capsys: pytest.CaptureFixture,
        fake_vcs_client: FakeVCSClient,
        review_comment_gateway: ReviewCommentGateway,
):
    """Should log and emit error on exception in summary reply."""

    async def failing_create_summary_reply(thread_id: str, body: str):
        raise RuntimeError("Network fail")

    fake_vcs_client.create_summary_reply = failing_create_summary_reply

    reply = SummaryCommentReplySchema(text="AI summary reply")
    await review_comment_gateway.process_summary_reply("t42", reply)
    output = capsys.readouterr().out

    assert "Failed to create summary reply" in output


# === INLINE COMMENT ===

@pytest.mark.asyncio
async def test_process_inline_comment_happy_path(
        fake_vcs_client: FakeVCSClient,
        fake_artifacts_service: FakeArtifactsService,
        review_comment_gateway: ReviewCommentGateway,
):
    """Should create inline comment via VCS."""
    comment = InlineCommentSchema(file="f.py", line=1, message="AI inline comment")
    await review_comment_gateway.process_inline_comment(comment)
    assert any(call[0] == "create_inline_comment" for call in fake_vcs_client.calls)

    assert ("save_vcs_inline", {"comment": comment}) in fake_artifacts_service.calls
    assert all(call[0] != "save_vcs_summary" for call in fake_artifacts_service.calls)
    assert all(call[0] != "save_vcs_summary_reply" for call in fake_artifacts_service.calls)


@pytest.mark.asyncio
async def test_process_inline_comment_error_fallback(
        capsys: pytest.CaptureFixture,
        fake_vcs_client: FakeVCSClient,
        fake_artifacts_service: FakeArtifactsService,
        review_comment_gateway: ReviewCommentGateway,
):
    """Should fall back to summary comment when inline comment fails."""

    async def failing_create_inline_comment(file: str, line: int, message: str):
        raise RuntimeError("Failed to post inline")

    fake_vcs_client.create_inline_comment = failing_create_inline_comment

    comment = InlineCommentSchema(file="x.py", line=5, message="AI inline")
    await review_comment_gateway.process_inline_comment(comment)
    output = capsys.readouterr().out

    assert "Falling back to general comment" in output
    assert any(call[0] == "create_general_comment" for call in fake_vcs_client.calls)

    assert all(call[0] != "save_vcs_inline" for call in fake_artifacts_service.calls)
    assert any(call[0] == "save_vcs_summary" for call in fake_artifacts_service.calls)


# === SUMMARY COMMENT ===

@pytest.mark.asyncio
async def test_process_summary_comment_happy_path(
        fake_vcs_client: FakeVCSClient,
        fake_artifacts_service: FakeArtifactsService,
        review_comment_gateway: ReviewCommentGateway,
):
    """Should create general summary comment successfully."""
    comment = SummaryCommentSchema(text="AI summary")
    await review_comment_gateway.process_summary_comment(comment)
    assert any(call[0] == "create_general_comment" for call in fake_vcs_client.calls)

    assert ("save_vcs_summary", {"comment": comment}) in fake_artifacts_service.calls


@pytest.mark.asyncio
async def test_process_summary_comment_error(
        capsys: pytest.CaptureFixture,
        fake_vcs_client: FakeVCSClient,
        fake_artifacts_service: FakeArtifactsService,
        review_comment_gateway: ReviewCommentGateway,
):
    """Should log error if summary comment creation fails."""

    async def failing_create_general_comment(body: str):
        raise RuntimeError("Backend down")

    fake_vcs_client.create_general_comment = failing_create_general_comment

    comment = SummaryCommentSchema(text="Broken")
    await review_comment_gateway.process_summary_comment(comment)
    output = capsys.readouterr().out

    assert "Failed to process summary comment" in output

    assert all(call[0] != "save_vcs_summary" for call in fake_artifacts_service.calls)


@pytest.mark.asyncio
async def test_process_inline_comments_calls_each(
        fake_vcs_client: FakeVCSClient,
        review_comment_gateway: ReviewCommentGateway,
):
    """Should process all inline comments concurrently."""
    comments = InlineCommentListSchema(root=[
        InlineCommentSchema(file="a.py", line=1, message="c1"),
        InlineCommentSchema(file="b.py", line=2, message="c2"),
    ])

    await review_comment_gateway.process_inline_comments(comments)

    created = [call for call in fake_vcs_client.calls if call[0] == "create_inline_comment"]
    assert len(created) == 2


@pytest.mark.asyncio
async def test_process_inline_comment_error_no_fallback_when_disabled(
        capsys: pytest.CaptureFixture,
        monkeypatch: pytest.MonkeyPatch,
        fake_vcs_client: FakeVCSClient,
        fake_artifacts_service: FakeArtifactsService,
        review_comment_gateway: ReviewCommentGateway,
):
    """Should NOT fall back to summary comment when inline fallback is disabled."""
    monkeypatch.setattr(settings.review, "inline_comment_fallback", False)

    async def failing_create_inline_comment(file: str, line: int, message: str):
        raise RuntimeError("Failed to post inline")

    fake_vcs_client.create_inline_comment = failing_create_inline_comment

    comment = InlineCommentSchema(file="x.py", line=10, message="AI inline")
    await review_comment_gateway.process_inline_comment(comment)
    output = capsys.readouterr().out

    assert "Failed to process inline comment" in output
    assert "Falling back to general comment" not in output

    assert all(call[0] != "create_general_comment" for call in fake_vcs_client.calls)
    assert all(call[0] != "save_vcs_summary" for call in fake_artifacts_service.calls)
    assert all(call[0] != "save_vcs_inline" for call in fake_artifacts_service.calls)
