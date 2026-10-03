import pytest

from ai_review.config import settings
from ai_review.services.review.filter.service import ReviewFilterService
from ai_review.services.review.gateway.review_comment_gateway import ReviewCommentGateway
from ai_review.services.review.internal.inline.schema import InlineCommentSchema, InlineCommentListSchema
from ai_review.services.review.internal.inline_reply.schema import InlineCommentReplySchema
from ai_review.services.review.internal.summary.schema import SummaryCommentSchema
from ai_review.services.review.internal.summary_reply.schema import SummaryCommentReplySchema
from ai_review.services.vcs.types import ReviewThreadSchema, ReviewCommentSchema, ThreadKind
from ai_review.tests.fixtures.services.artifacts import FakeArtifactsService
from ai_review.tests.fixtures.services.hook import FakeHookService
from ai_review.tests.fixtures.services.vcs import FakeVCSClient, FakeBatchingVCSClient


# === INLINE THREADS ===

@pytest.mark.asyncio
async def test_get_inline_threads_filters_by_tag(
        fake_vcs_client: FakeVCSClient,
        review_comment_gateway: ReviewCommentGateway,
):
    """Should return threads whose latest comment requests an inline reply."""
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


# === GET INLINE COMMENTS ===

@pytest.mark.asyncio
async def test_get_inline_comments_filters_only_ai_comments(
        fake_vcs_client: FakeVCSClient,
        review_comment_gateway: ReviewCommentGateway,
):
    """Should return only inline comments containing AI inline tag."""
    fake_vcs_client.responses["get_inline_comments"] = [
        ReviewCommentSchema(id="1", body=f"{settings.review.inline_tag} AI comment"),
        ReviewCommentSchema(id="2", body="Regular inline comment"),
    ]

    result = await review_comment_gateway.get_inline_comments()

    assert len(result) == 1
    assert result[0].id == "1"

    assert any(call[0] == "get_inline_comments" for call in fake_vcs_client.calls)


@pytest.mark.asyncio
async def test_get_inline_comments_returns_empty_when_no_ai_comments(
        fake_vcs_client: FakeVCSClient,
        review_comment_gateway: ReviewCommentGateway,
):
    """Should return empty list when no AI inline comments exist."""
    fake_vcs_client.responses["get_inline_comments"] = [
        ReviewCommentSchema(id="1", body="Just a comment"),
    ]

    result = await review_comment_gateway.get_inline_comments()

    assert result == []


# === GET SUMMARY COMMENTS ===

@pytest.mark.asyncio
async def test_get_summary_comments_filters_only_ai_comments(
        fake_vcs_client: FakeVCSClient,
        review_comment_gateway: ReviewCommentGateway,
):
    """Should return only summary comments containing AI summary tag."""
    fake_vcs_client.responses["get_general_comments"] = [
        ReviewCommentSchema(id="10", body=f"{settings.review.summary_tag} AI summary"),
        ReviewCommentSchema(id="11", body="Regular summary"),
    ]

    result = await review_comment_gateway.get_summary_comments()

    assert len(result) == 1
    assert result[0].id == "10"

    assert any(call[0] == "get_general_comments" for call in fake_vcs_client.calls)


@pytest.mark.asyncio
async def test_get_summary_comments_returns_empty_when_no_ai_comments(
        fake_vcs_client: FakeVCSClient,
        review_comment_gateway: ReviewCommentGateway,
):
    """Should return empty list when no AI summary comments exist."""
    fake_vcs_client.responses["get_general_comments"] = [
        ReviewCommentSchema(id="1", body="Regular comment"),
    ]

    result = await review_comment_gateway.get_summary_comments()

    assert result == []


@pytest.mark.asyncio
async def test_summary_detection_and_clear_distinguish_requests_replies_and_summaries(
        fake_vcs_client: FakeVCSClient,
        review_comment_gateway: ReviewCommentGateway,
):
    request = ReviewCommentSchema(id="request", body="Why? #ai-review-summary-reply")
    reply = ReviewCommentSchema(
        id="reply", body=SummaryCommentReplySchema(text="Answer").body_for_request("request", "request"),
    )
    summary = ReviewCommentSchema(id="summary", body="Review #ai-review-summary")
    fallback = ReviewCommentSchema(id="fallback", body="Finding #ai-review-inline-fallback")
    fake_vcs_client.responses["get_general_comments"] = [request, reply, fallback]
    assert await review_comment_gateway.get_summary_comments() == []

    fake_vcs_client.responses["get_general_comments"].append(summary)
    assert await review_comment_gateway.get_summary_comments() == [summary]
    await review_comment_gateway.clear_summary_comments()

    deleted = [call[1][0] for call in fake_vcs_client.calls if call[0] == "delete_general_comment"]
    assert deleted == ["reply", "fallback", "summary"]


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

    call = next(call for call in fake_vcs_client.calls if call[0] == "create_inline_reply")
    assert call[1] == ("t1", reply.body_with_tag)

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
    await review_comment_gateway.process_summary_reply("t42", reply, request_comment_id="c1")
    call = next(call for call in fake_vcs_client.calls if call[0] == "create_summary_reply")
    assert call[1] == ("t42", reply.body_for_request("t42", "c1"))

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
    await review_comment_gateway.process_summary_reply("t42", reply, request_comment_id="c1")
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
    """Should fall back to inline fallback comment when inline comment fails."""

    async def failing_create_inline_comment(file: str, line: int, message: str):
        raise RuntimeError("Failed to post inline")

    fake_vcs_client.create_inline_comment = failing_create_inline_comment

    comment = InlineCommentSchema(file="x.py", line=5, message="AI inline")
    await review_comment_gateway.process_inline_comment(comment)
    output = capsys.readouterr().out

    assert "Falling back to general comment" in output
    assert any(call[0] == "create_general_comment" for call in fake_vcs_client.calls)

    fallback_call = next(call for call in fake_vcs_client.calls if call[0] == "create_general_comment")
    posted_body = fallback_call[1][0]
    assert settings.review.inline_fallback_tag in posted_body
    assert settings.review.summary_tag not in posted_body

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


# === INLINE FALLBACK COMMENT ===

@pytest.mark.asyncio
async def test_process_inline_fallback_comment_happy_path(
        fake_vcs_client: FakeVCSClient,
        fake_artifacts_service: FakeArtifactsService,
        review_comment_gateway: ReviewCommentGateway,
):
    """Should create general comment with inline fallback tag."""
    comment = SummaryCommentSchema(text="**x.py:42** — missing check")
    await review_comment_gateway.process_inline_fallback_comment(comment)

    assert any(call[0] == "create_general_comment" for call in fake_vcs_client.calls)

    fallback_call = next(call for call in fake_vcs_client.calls if call[0] == "create_general_comment")
    posted_body = fallback_call[1][0]
    assert settings.review.inline_fallback_tag in posted_body
    assert settings.review.summary_tag not in posted_body

    assert ("save_vcs_summary", {"comment": comment}) in fake_artifacts_service.calls


@pytest.mark.asyncio
async def test_process_inline_fallback_comment_error(
        capsys: pytest.CaptureFixture,
        fake_vcs_client: FakeVCSClient,
        fake_artifacts_service: FakeArtifactsService,
        review_comment_gateway: ReviewCommentGateway,
):
    """Should log error if inline fallback comment creation fails."""

    async def failing_create_general_comment(body: str):
        raise RuntimeError("Backend down")

    fake_vcs_client.create_general_comment = failing_create_general_comment

    comment = SummaryCommentSchema(text="Broken fallback")
    await review_comment_gateway.process_inline_fallback_comment(comment)
    output = capsys.readouterr().out

    assert "Failed to process inline fallback comment" in output

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


# === CLEAR ===

@pytest.mark.asyncio
@pytest.mark.parametrize(
    "method, expected_inline, expected_general",
    [
        ("clear_inline_comments", {"1", "3"}, set()),
        ("clear_summary_comments", set(), {"4", "6", "7"}),
        ("clear_inline_replies", {"2"}, set()),
        ("clear_summary_replies", set(), {"5"}),
    ],
)
async def test_clear_commands_select_only_their_comment_types(
        method: str,
        expected_inline: set[str],
        expected_general: set[str],
        fake_vcs_client: FakeVCSClient,
        review_comment_gateway: ReviewCommentGateway,
):
    """Each command starts with the same PR and selects its own comment type."""
    fake_vcs_client.responses["get_inline_comments"] = [
        ReviewCommentSchema(id="1", body=f"Finding mentions {settings.review.summary_reply_tag}\n{settings.review.inline_tag}"),
        ReviewCommentSchema(id="2", body=f"Why? {settings.review.inline_reply_tag}"),
        ReviewCommentSchema(id="3", body=InlineCommentReplySchema(
            message=f"Because you asked {settings.review.summary_reply_tag}"
        ).body_with_tag),
    ]
    fake_vcs_client.responses["get_general_comments"] = [
        ReviewCommentSchema(id="4", body=f"Overview mentions {settings.review.inline_reply_tag}\n{settings.review.summary_tag}"),
        ReviewCommentSchema(id="5", body=f"Which tests? {settings.review.summary_reply_tag}"),
        ReviewCommentSchema(id="6", body=SummaryCommentReplySchema(
            text=f"Add edge cases for {settings.review.inline_reply_tag}"
        ).body_for_request("t", "5")),
        ReviewCommentSchema(id="7", body=f"Fallback {settings.review.inline_fallback_tag}"),
    ]

    await getattr(review_comment_gateway, method)()

    assert {call[1][0] for call in fake_vcs_client.calls if call[0] == "delete_inline_comment"} == expected_inline
    assert {call[1][0] for call in fake_vcs_client.calls if call[0] == "delete_general_comment"} == expected_general


@pytest.mark.asyncio
async def test_clear_inline_comments_deletes_all_ai_comments(
        fake_vcs_client: FakeVCSClient,
        review_comment_gateway: ReviewCommentGateway,
):
    """Should delete all existing AI inline comments."""
    fake_vcs_client.responses["get_inline_comments"] = [
        ReviewCommentSchema(id="1", body=f"{settings.review.inline_tag} comment 1"),
        ReviewCommentSchema(id="2", body=f"{settings.review.inline_tag} comment 2"),
    ]

    await review_comment_gateway.clear_inline_comments()

    deleted = [call for call in fake_vcs_client.calls if call[0] == "delete_inline_comment"]
    assert len(deleted) == 2
    assert {call[1][0] for call in deleted} == {"1", "2"}


@pytest.mark.asyncio
async def test_inline_detection_and_clear_preserve_user_reply_requests(
        fake_vcs_client: FakeVCSClient,
        review_comment_gateway: ReviewCommentGateway,
):
    request = ReviewCommentSchema(id="user", body=f"Why? {settings.review.inline_reply_tag}")
    generated = ReviewCommentSchema(id="bot", body=f"Explanation\n\n{settings.review.inline_tag}")
    fake_vcs_client.responses["get_inline_comments"] = [request]
    assert await review_comment_gateway.get_inline_comments() == []

    fake_vcs_client.responses["get_inline_comments"] = [request, generated]
    assert await review_comment_gateway.get_inline_comments() == [generated]
    await review_comment_gateway.clear_inline_comments()

    deleted = [call[1][0] for call in fake_vcs_client.calls if call[0] == "delete_inline_comment"]
    assert deleted == ["bot"]


@pytest.mark.asyncio
async def test_clear_inline_comments_emits_start_and_complete_hooks(
        monkeypatch: pytest.MonkeyPatch,
        fake_hook_service: FakeHookService,
        fake_vcs_client: FakeVCSClient,
        review_comment_gateway: ReviewCommentGateway,
):
    """Should emit clear-inline start and complete hooks with deleted comments."""
    monkeypatch.setattr("ai_review.services.review.gateway.review_comment_gateway.hook", fake_hook_service)
    comments = [
        ReviewCommentSchema(id="1", body=f"{settings.review.inline_tag} comment 1"),
        ReviewCommentSchema(id="2", body=f"{settings.review.inline_tag} comment 2"),
    ]
    fake_vcs_client.responses["get_inline_comments"] = comments

    await review_comment_gateway.clear_inline_comments()

    assert fake_hook_service.calls == [
        ("emit_clear_inline_comments_start", {}),
        ("emit_clear_inline_comments_complete", {"comments": comments}),
    ]


@pytest.mark.asyncio
async def test_clear_inline_comments_noop_when_no_comments(
        fake_vcs_client: FakeVCSClient,
        review_comment_gateway: ReviewCommentGateway,
):
    """Should not call delete when no inline AI comments exist."""
    fake_vcs_client.responses["get_inline_comments"] = []

    await review_comment_gateway.clear_inline_comments()

    assert all(call[0] != "delete_inline_comment" for call in fake_vcs_client.calls)


@pytest.mark.asyncio
async def test_clear_inline_replies_deletes_requests_but_preserves_ai_comments(
        fake_vcs_client: FakeVCSClient,
        review_comment_gateway: ReviewCommentGateway,
):
    fake_vcs_client.responses["get_inline_comments"] = [
        ReviewCommentSchema(id="question", body=f"Why? {settings.review.inline_reply_tag}"),
        ReviewCommentSchema(id="finding", body=f"Problem {settings.review.inline_tag}"),
        ReviewCommentSchema(id="reply", body=InlineCommentReplySchema(message="Because").body_with_tag),
        ReviewCommentSchema(id="ordinary", body="A regular comment"),
    ]

    await review_comment_gateway.clear_inline_replies()

    assert [call[1][0] for call in fake_vcs_client.calls if call[0] == "delete_inline_comment"] == ["question"]


@pytest.mark.asyncio
async def test_clear_inline_replies_also_handles_general_comment_requests(
        fake_vcs_client: FakeVCSClient,
        review_comment_gateway: ReviewCommentGateway,
):
    fake_vcs_client.responses["get_general_comments"] = [
        ReviewCommentSchema(id="question", body=f"Why? {settings.review.inline_reply_tag}"),
        ReviewCommentSchema(id="reply", body=InlineCommentReplySchema(message="Because").body_with_tag),
        ReviewCommentSchema(id="summary", body=f"Review {settings.review.summary_tag}"),
    ]

    await review_comment_gateway.clear_inline_replies()

    assert [call[1][0] for call in fake_vcs_client.calls if call[0] == "delete_general_comment"] == ["question"]


@pytest.mark.asyncio
async def test_clear_inline_includes_general_comment_fallback(
        fake_vcs_client: FakeVCSClient,
        review_comment_gateway: ReviewCommentGateway,
):
    fake_vcs_client.responses["get_general_comments"] = [
        ReviewCommentSchema(id="reply", body=InlineCommentReplySchema(message="Because").body_with_tag),
        ReviewCommentSchema(id="question", body=f"Why? {settings.review.inline_reply_tag}"),
    ]

    await review_comment_gateway.clear_inline_comments()

    assert [call[1][0] for call in fake_vcs_client.calls if call[0] == "delete_general_comment"] == ["reply"]


@pytest.mark.asyncio
async def test_inline_reply_marker_survives_tag_configuration_change(
        monkeypatch: pytest.MonkeyPatch,
        fake_vcs_client: FakeVCSClient,
        review_comment_gateway: ReviewCommentGateway,
):
    old_reply = InlineCommentReplySchema(message="Answer").body_with_tag
    fake_vcs_client.responses["get_inline_comments"] = [ReviewCommentSchema(id="inline", body=old_reply)]
    fake_vcs_client.responses["get_general_comments"] = [ReviewCommentSchema(id="general", body=old_reply)]
    monkeypatch.setattr(settings.review, "inline_tag", "#new-inline-tag")

    await review_comment_gateway.clear_inline_comments()

    assert [call[1][0] for call in fake_vcs_client.calls if call[0] == "delete_inline_comment"] == ["inline"]
    assert [call[1][0] for call in fake_vcs_client.calls if call[0] == "delete_general_comment"] == ["general"]


@pytest.mark.asyncio
async def test_clear_inline_replies_handles_no_requests(
        fake_vcs_client: FakeVCSClient,
        review_comment_gateway: ReviewCommentGateway,
):
    await review_comment_gateway.clear_inline_replies()

    assert all(call[0] != "delete_inline_comment" for call in fake_vcs_client.calls)


@pytest.mark.asyncio
async def test_clear_summary_comments_deletes_all_ai_comments(
        fake_vcs_client: FakeVCSClient,
        review_comment_gateway: ReviewCommentGateway,
):
    """Should delete all existing AI summary comments."""
    fake_vcs_client.responses["get_general_comments"] = [
        ReviewCommentSchema(id="10", body=f"{settings.review.summary_tag} summary 1"),
        ReviewCommentSchema(id="11", body=f"{settings.review.summary_tag} summary 2"),
    ]

    await review_comment_gateway.clear_summary_comments()

    deleted = [call for call in fake_vcs_client.calls if call[0] == "delete_general_comment"]
    assert len(deleted) == 2
    assert {call[1][0] for call in deleted} == {"10", "11"}


@pytest.mark.asyncio
async def test_clear_summary_comments_emits_start_and_complete_hooks(
        monkeypatch: pytest.MonkeyPatch,
        fake_hook_service: FakeHookService,
        fake_vcs_client: FakeVCSClient,
        review_comment_gateway: ReviewCommentGateway,
):
    """Should emit clear-summary start and complete hooks with deleted comments."""
    monkeypatch.setattr("ai_review.services.review.gateway.review_comment_gateway.hook", fake_hook_service)
    comments = [
        ReviewCommentSchema(id="10", body=f"{settings.review.summary_tag} summary 1"),
        ReviewCommentSchema(id="11", body=f"{settings.review.summary_tag} summary 2"),
    ]
    fake_vcs_client.responses["get_general_comments"] = comments

    await review_comment_gateway.clear_summary_comments()

    assert fake_hook_service.calls == [
        ("emit_clear_summary_comments_start", {}),
        ("emit_clear_summary_comments_complete", {"comments": comments}),
    ]


@pytest.mark.asyncio
async def test_clear_summary_comments_noop_when_no_comments(
        fake_vcs_client: FakeVCSClient,
        review_comment_gateway: ReviewCommentGateway,
):
    """Should not call delete when no summary AI comments exist."""
    fake_vcs_client.responses["get_general_comments"] = []

    await review_comment_gateway.clear_summary_comments()

    assert all(call[0] != "delete_general_comment" for call in fake_vcs_client.calls)


@pytest.mark.asyncio
async def test_clear_summary_replies_deletes_requests_but_preserves_ai_comments(
        fake_vcs_client: FakeVCSClient,
        review_comment_gateway: ReviewCommentGateway,
):
    fake_vcs_client.responses["get_general_comments"] = [
        ReviewCommentSchema(id="question", body=f"Why? {settings.review.summary_reply_tag}"),
        ReviewCommentSchema(id="summary", body=f"Review {settings.review.summary_tag}"),
        ReviewCommentSchema(id="fallback", body=f"Fallback {settings.review.inline_fallback_tag}"),
        ReviewCommentSchema(id="reply", body=SummaryCommentReplySchema(text="Because").body_for_request("t", "q")),
        ReviewCommentSchema(id="ordinary", body="A regular comment"),
    ]

    await review_comment_gateway.clear_summary_replies()

    assert [call[1][0] for call in fake_vcs_client.calls if call[0] == "delete_general_comment"] == ["question"]


@pytest.mark.asyncio
async def test_summary_reply_marker_survives_tag_configuration_change(
        monkeypatch: pytest.MonkeyPatch,
        fake_vcs_client: FakeVCSClient,
        review_comment_gateway: ReviewCommentGateway,
):
    old_reply = SummaryCommentReplySchema(text="Answer").body_for_request("t", "q")
    fake_vcs_client.responses["get_general_comments"] = [ReviewCommentSchema(id="reply", body=old_reply)]
    monkeypatch.setattr(settings.review, "summary_tag", "#new-summary-tag")

    await review_comment_gateway.clear_summary_comments()

    assert [call[1][0] for call in fake_vcs_client.calls if call[0] == "delete_general_comment"] == ["reply"]


@pytest.mark.asyncio
async def test_clear_summary_replies_handles_no_requests(
        fake_vcs_client: FakeVCSClient,
        review_comment_gateway: ReviewCommentGateway,
):
    await review_comment_gateway.clear_summary_replies()

    assert all(call[0] != "delete_general_comment" for call in fake_vcs_client.calls)


@pytest.mark.asyncio
async def test_get_summary_comments_excludes_fallback_comments(
        fake_vcs_client: FakeVCSClient,
        review_comment_gateway: ReviewCommentGateway,
):
    """Summary comments detection should not include fallback-tagged comments."""
    fake_vcs_client.responses["get_general_comments"] = [
        ReviewCommentSchema(id="10", body=f"Summary {settings.review.summary_tag}"),
        ReviewCommentSchema(id="11", body=f"Fallback {settings.review.inline_fallback_tag}"),
    ]

    result = await review_comment_gateway.get_summary_comments()

    assert len(result) == 1
    assert result[0].id == "10"


@pytest.mark.asyncio
async def test_clear_summary_comments_deletes_inline_fallback_comments(
        fake_vcs_client: FakeVCSClient,
        review_comment_gateway: ReviewCommentGateway,
):
    """Should delete inline-fallback general comments alongside the summary comments."""
    fake_vcs_client.responses["get_general_comments"] = [
        ReviewCommentSchema(id="10", body=f"{settings.review.summary_tag} summary"),
        ReviewCommentSchema(id="11", body=f"{settings.review.inline_fallback_tag} fallback"),
        ReviewCommentSchema(id="12", body="a human wrote this"),
    ]

    await review_comment_gateway.clear_summary_comments()

    deleted = [call for call in fake_vcs_client.calls if call[0] == "delete_general_comment"]
    assert {call[1][0] for call in deleted} == {"10", "11"}


@pytest.mark.asyncio
async def test_get_summary_comments_ignores_inline_fallback_comments(
        fake_vcs_client: FakeVCSClient,
        review_comment_gateway: ReviewCommentGateway,
):
    """Should keep the summary skip-check blind to fallback comments.

    SummaryReviewRunner skips the summary review when this returns anything, so a
    leftover fallback comment must not suppress the summary.
    """
    fake_vcs_client.responses["get_general_comments"] = [
        ReviewCommentSchema(id="11", body=f"{settings.review.inline_fallback_tag} fallback"),
    ]

    comments = await review_comment_gateway.get_summary_comments()

    assert comments == []


@pytest.mark.asyncio
async def test_clear_inline_comments_reports_lookup_failure(
        monkeypatch: pytest.MonkeyPatch,
        fake_hook_service: FakeHookService,
        review_comment_gateway: ReviewCommentGateway,
) -> None:
    monkeypatch.setattr("ai_review.services.review.gateway.review_comment_gateway.hook", fake_hook_service)

    async def fail_lookup() -> None:
        raise RuntimeError("lookup failed")

    monkeypatch.setattr(review_comment_gateway, "get_inline_comments", fail_lookup)
    with pytest.raises(RuntimeError, match="lookup failed"):
        await review_comment_gateway.clear_inline_comments()
    assert fake_hook_service.calls == [
        ("emit_clear_inline_comments_start", {}),
        ("emit_clear_inline_comments_error", {}),
    ]


@pytest.mark.asyncio
async def test_clear_summary_comments_reports_lookup_failure(
        monkeypatch: pytest.MonkeyPatch,
        fake_hook_service: FakeHookService,
        review_comment_gateway: ReviewCommentGateway,
) -> None:
    monkeypatch.setattr("ai_review.services.review.gateway.review_comment_gateway.hook", fake_hook_service)

    async def fail_lookup() -> None:
        raise RuntimeError("lookup failed")

    monkeypatch.setattr(review_comment_gateway, "get_clearable_summary_comments", fail_lookup)
    with pytest.raises(RuntimeError, match="lookup failed"):
        await review_comment_gateway.clear_summary_comments()
    assert fake_hook_service.calls == [
        ("emit_clear_summary_comments_start", {}),
        ("emit_clear_summary_comments_error", {}),
    ]


@pytest.mark.asyncio
async def test_clear_inline_replies_reports_lookup_failure(
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture,
        review_comment_gateway: ReviewCommentGateway,
):
    async def fail_lookup():
        raise RuntimeError("lookup failed")

    monkeypatch.setattr(review_comment_gateway, "get_inline_replies", fail_lookup)

    with pytest.raises(RuntimeError, match="lookup failed"):
        await review_comment_gateway.clear_inline_replies()

    assert "Failed to clear inline replies" in capsys.readouterr().out


@pytest.mark.asyncio
async def test_clear_summary_replies_reports_lookup_failure(
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture,
        review_comment_gateway: ReviewCommentGateway,
):
    async def fail_lookup():
        raise RuntimeError("lookup failed")

    monkeypatch.setattr(review_comment_gateway, "get_summary_replies", fail_lookup)

    with pytest.raises(RuntimeError, match="lookup failed"):
        await review_comment_gateway.clear_summary_replies()

    assert "Failed to clear summary replies" in capsys.readouterr().out


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "method, inline_body, general_body, failed_call",
    [
        ("clear_inline_comments", "Finding #ai-review-inline", None, "delete_inline_comment"),
        ("clear_summary_comments", None, "Summary #ai-review-summary", "delete_general_comment"),
        ("clear_inline_replies", "Question #ai-review-inline-reply", None, "delete_inline_comment"),
        ("clear_summary_replies", None, "Question #ai-review-summary-reply", "delete_general_comment"),
    ],
)
async def test_clear_commands_propagate_vcs_deletion_failure(
        method: str,
        inline_body: str | None,
        general_body: str | None,
        failed_call: str,
        fake_vcs_client: FakeVCSClient,
        review_comment_gateway: ReviewCommentGateway,
):
    if inline_body:
        fake_vcs_client.responses["get_inline_comments"] = [ReviewCommentSchema(id="inline", body=inline_body)]
    if general_body:
        fake_vcs_client.responses["get_general_comments"] = [ReviewCommentSchema(id="general", body=general_body)]
    fake_vcs_client.responses[f"{failed_call}_error"] = RuntimeError("delete denied")

    with pytest.raises(RuntimeError, match="delete denied"):
        await getattr(review_comment_gateway, method)()

    assert any(call[0] == failed_call for call in fake_vcs_client.calls)


# === FINALIZE ===

@pytest.mark.asyncio
async def test_finalize_publishes_batched_comments(
        fake_batching_vcs_client: FakeBatchingVCSClient,
        fake_artifacts_service: FakeArtifactsService,
        review_filter_service: ReviewFilterService,
):
    """Should publish batched comments when the VCS client supports batching."""
    gateway = ReviewCommentGateway(
        vcs=fake_batching_vcs_client, artifacts=fake_artifacts_service, review_filter=review_filter_service,
    )

    await gateway.finalize()

    assert any(call[0] == "publish_comments" for call in fake_batching_vcs_client.calls)


@pytest.mark.asyncio
async def test_finalize_skips_non_batching_vcs(
        fake_vcs_client: FakeVCSClient,
        review_comment_gateway: ReviewCommentGateway,
):
    """Should be a no-op for VCS clients without the batching capability."""
    await review_comment_gateway.finalize()

    assert fake_vcs_client.calls == []


@pytest.mark.asyncio
async def test_finalize_swallows_vcs_errors(
        capsys: pytest.CaptureFixture,
        fake_batching_vcs_client: FakeBatchingVCSClient,
        fake_artifacts_service: FakeArtifactsService,
        review_filter_service: ReviewFilterService,
):
    """Should log and swallow errors from the VCS client."""
    fake_batching_vcs_client.responses["publish_comments_error"] = RuntimeError("boom")
    gateway = ReviewCommentGateway(
        vcs=fake_batching_vcs_client, artifacts=fake_artifacts_service, review_filter=review_filter_service,
    )

    await gateway.finalize()
    output = capsys.readouterr().out

    assert any(call[0] == "publish_comments" for call in fake_batching_vcs_client.calls)
    assert "Failed to publish batched comments" in output
