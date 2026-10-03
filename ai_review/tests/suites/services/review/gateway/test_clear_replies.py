import pytest

from ai_review.config import settings
from ai_review.services.review.gateway.review_comment_gateway import ReviewCommentGateway
from ai_review.services.review.gateway.review_dry_run_comment_gateway import ReviewDryRunCommentGateway
from ai_review.services.review.internal.inline_reply.schema import InlineCommentReplySchema
from ai_review.services.review.internal.summary_reply.schema import SummaryCommentReplySchema
from ai_review.services.vcs.types import ReviewCommentSchema
from ai_review.tests.fixtures.services.vcs import FakeVCSClient


@pytest.mark.asyncio
async def test_clear_inline_replies_preserves_questions_and_regular_findings(
        fake_vcs_client: FakeVCSClient,
        review_comment_gateway: ReviewCommentGateway,
):
    fake_vcs_client.responses["get_inline_comments"] = [
        ReviewCommentSchema(id="question", body=f"Why? {settings.review.inline_reply_tag}"),
        ReviewCommentSchema(id="finding", body=f"Problem {settings.review.inline_tag}"),
        ReviewCommentSchema(id="reply", body=InlineCommentReplySchema(message="Because").body_with_tag),
        ReviewCommentSchema(id="legacy", body=f"Old answer {settings.review.inline_reply_tag}"),
    ]

    await review_comment_gateway.clear_inline_replies()

    assert [call[1][0] for call in fake_vcs_client.calls if call[0] == "delete_inline_comment"] == ["reply"]


@pytest.mark.asyncio
async def test_clear_inline_replies_also_handles_general_comment_fallback(
        fake_vcs_client: FakeVCSClient,
        review_comment_gateway: ReviewCommentGateway,
):
    fake_vcs_client.responses["get_general_comments"] = [
        ReviewCommentSchema(id="question", body=f"Why? {settings.review.inline_reply_tag}"),
        ReviewCommentSchema(id="reply", body=InlineCommentReplySchema(message="Because").body_with_tag),
        ReviewCommentSchema(id="summary", body=f"Review {settings.review.summary_tag}"),
    ]

    await review_comment_gateway.clear_inline_replies()

    assert [call[1][0] for call in fake_vcs_client.calls if call[0] == "delete_general_comment"] == ["reply"]


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
async def test_clear_summary_replies_preserves_questions_and_regular_summaries(
        fake_vcs_client: FakeVCSClient,
        review_comment_gateway: ReviewCommentGateway,
):
    fake_vcs_client.responses["get_general_comments"] = [
        ReviewCommentSchema(id="question", body=f"Why? {settings.review.summary_reply_tag}"),
        ReviewCommentSchema(id="summary", body=f"Review {settings.review.summary_tag}"),
        ReviewCommentSchema(id="fallback", body=f"Fallback {settings.review.inline_fallback_tag}"),
        ReviewCommentSchema(id="reply", body=SummaryCommentReplySchema(text="Because").body_for_request("t", "q")),
        ReviewCommentSchema(id="legacy", body=f"Old answer {settings.review.summary_reply_tag}"),
    ]

    await review_comment_gateway.clear_summary_replies()

    assert [call[1][0] for call in fake_vcs_client.calls if call[0] == "delete_general_comment"] == ["reply"]


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
async def test_clear_inline_replies_handles_no_replies(
        fake_vcs_client: FakeVCSClient,
        review_comment_gateway: ReviewCommentGateway,
):
    await review_comment_gateway.clear_inline_replies()

    assert all(call[0] != "delete_inline_comment" for call in fake_vcs_client.calls)


@pytest.mark.asyncio
async def test_clear_summary_replies_handles_no_replies(
        fake_vcs_client: FakeVCSClient,
        review_comment_gateway: ReviewCommentGateway,
):
    await review_comment_gateway.clear_summary_replies()

    assert all(call[0] != "delete_general_comment" for call in fake_vcs_client.calls)


@pytest.mark.asyncio
async def test_clear_inline_replies_reports_lookup_failure(
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture,
        review_comment_gateway: ReviewCommentGateway,
):
    async def fail_lookup():
        raise RuntimeError("lookup failed")

    monkeypatch.setattr(review_comment_gateway, "get_inline_replies", fail_lookup)

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

    await review_comment_gateway.clear_summary_replies()

    assert "Failed to clear summary replies" in capsys.readouterr().out


@pytest.mark.asyncio
async def test_dry_run_inline_reply_cleanup_does_not_delete(
        capsys: pytest.CaptureFixture,
        fake_vcs_client: FakeVCSClient,
        review_dry_run_comment_gateway: ReviewDryRunCommentGateway,
):
    fake_vcs_client.responses["get_inline_comments"] = [
        ReviewCommentSchema(id="reply", body=InlineCommentReplySchema(message="Answer").body_with_tag),
    ]

    await review_dry_run_comment_gateway.clear_inline_replies()

    assert "Would delete inline reply reply" in capsys.readouterr().out
    assert all(call[0] != "delete_inline_comment" for call in fake_vcs_client.calls)


@pytest.mark.asyncio
async def test_dry_run_inline_reply_cleanup_reports_general_fallback(
        capsys: pytest.CaptureFixture,
        fake_vcs_client: FakeVCSClient,
        review_dry_run_comment_gateway: ReviewDryRunCommentGateway,
):
    fake_vcs_client.responses["get_general_comments"] = [
        ReviewCommentSchema(id="reply", body=InlineCommentReplySchema(message="Answer").body_with_tag),
    ]

    await review_dry_run_comment_gateway.clear_inline_replies()

    assert "Would delete general inline reply reply" in capsys.readouterr().out
    assert all(call[0] != "delete_general_comment" for call in fake_vcs_client.calls)


@pytest.mark.asyncio
async def test_dry_run_clear_inline_reports_general_fallback(
        capsys: pytest.CaptureFixture,
        fake_vcs_client: FakeVCSClient,
        review_dry_run_comment_gateway: ReviewDryRunCommentGateway,
):
    fake_vcs_client.responses["get_general_comments"] = [
        ReviewCommentSchema(id="reply", body=InlineCommentReplySchema(message="Answer").body_with_tag),
    ]

    await review_dry_run_comment_gateway.clear_inline_comments()

    assert "Would delete general inline reply reply" in capsys.readouterr().out
    assert all(call[0] != "delete_general_comment" for call in fake_vcs_client.calls)


@pytest.mark.asyncio
async def test_dry_run_summary_reply_cleanup_does_not_delete(
        capsys: pytest.CaptureFixture,
        fake_vcs_client: FakeVCSClient,
        review_dry_run_comment_gateway: ReviewDryRunCommentGateway,
):
    fake_vcs_client.responses["get_general_comments"] = [
        ReviewCommentSchema(id="reply", body=SummaryCommentReplySchema(text="Answer").body_for_request("t", "q")),
    ]

    await review_dry_run_comment_gateway.clear_summary_replies()

    assert "Would delete summary reply reply" in capsys.readouterr().out
    assert all(call[0] != "delete_general_comment" for call in fake_vcs_client.calls)
