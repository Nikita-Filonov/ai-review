import pytest

from ai_review.config import settings
from ai_review.services.review.gateway.review_dry_run_comment_gateway import ReviewDryRunCommentGateway
from ai_review.services.review.internal.inline.schema import InlineCommentSchema, InlineCommentListSchema
from ai_review.services.review.internal.inline_reply.schema import InlineCommentReplySchema
from ai_review.services.review.internal.summary.schema import SummaryCommentSchema
from ai_review.services.review.internal.summary_reply.schema import SummaryCommentReplySchema
from ai_review.services.vcs.types import ReviewCommentSchema
from ai_review.tests.fixtures.services.artifacts import FakeArtifactsService
from ai_review.tests.fixtures.services.vcs import FakeVCSClient, FakeBatchingVCSClient


@pytest.mark.asyncio
async def test_process_inline_reply_dry_run_logs_and_no_vcs_calls(
        capsys: pytest.CaptureFixture,
        fake_vcs_client: FakeVCSClient,
        fake_artifacts_service: FakeArtifactsService,
        review_dry_run_comment_gateway: ReviewDryRunCommentGateway
):
    """Dry-run: should log the inline reply but not call VCS."""
    reply = InlineCommentReplySchema(message="AI reply dry-run")
    await review_dry_run_comment_gateway.process_inline_reply("t1", reply)
    output = capsys.readouterr().out

    assert "[dry-run]" in output
    assert "Would create inline reply" in output
    assert settings.review.inline_tag in output
    assert settings.review.inline_reply_tag not in output
    assert not any(call[0].startswith("create_") for call in fake_vcs_client.calls)

    assert ("save_vcs_inline_reply", {"thread_id": "t1", "reply": reply}) in fake_artifacts_service.calls


@pytest.mark.asyncio
async def test_process_summary_reply_dry_run_logs_and_no_vcs_calls(
        capsys: pytest.CaptureFixture,
        fake_vcs_client: FakeVCSClient,
        fake_artifacts_service: FakeArtifactsService,
        review_dry_run_comment_gateway: ReviewDryRunCommentGateway
):
    """Dry-run: should log the summary reply but not call VCS."""
    reply = SummaryCommentReplySchema(text="Dry-run summary reply")
    await review_dry_run_comment_gateway.process_summary_reply("t2", reply, request_comment_id="c2")
    output = capsys.readouterr().out

    assert "[dry-run]" in output
    assert "Would create summary reply" in output
    assert settings.review.summary_reply_tag not in output
    assert reply.body_for_request("t2", "c2") in output
    assert not any(call[0].startswith("create_") for call in fake_vcs_client.calls)

    assert ("save_vcs_summary_reply", {"thread_id": "t2", "reply": reply}) in fake_artifacts_service.calls


@pytest.mark.asyncio
async def test_process_inline_comment_dry_run_logs_and_no_vcs_calls(
        capsys: pytest.CaptureFixture,
        fake_vcs_client: FakeVCSClient,
        fake_artifacts_service: FakeArtifactsService,
        review_dry_run_comment_gateway: ReviewDryRunCommentGateway
):
    """Dry-run: should log inline comment without creating one."""
    comment = InlineCommentSchema(file="a.py", line=10, message="Test comment")
    await review_dry_run_comment_gateway.process_inline_comment(comment)
    output = capsys.readouterr().out

    assert "[dry-run]" in output
    assert "Would create inline comment" in output
    assert "a.py" in output
    assert not any(call[0].startswith("create_") for call in fake_vcs_client.calls)

    assert ("save_vcs_inline", {"comment": comment}) in fake_artifacts_service.calls


@pytest.mark.asyncio
async def test_process_summary_comment_dry_run_logs_and_no_vcs_calls(
        capsys: pytest.CaptureFixture,
        fake_vcs_client: FakeVCSClient,
        fake_artifacts_service: FakeArtifactsService,
        review_dry_run_comment_gateway: ReviewDryRunCommentGateway
):
    """Dry-run: should log summary comment but not send it."""
    comment = SummaryCommentSchema(text="Dry-run summary comment")
    await review_dry_run_comment_gateway.process_summary_comment(comment)
    output = capsys.readouterr().out

    assert "[dry-run]" in output
    assert "Would create summary comment" in output
    assert not any(call[0].startswith("create_") for call in fake_vcs_client.calls)

    assert ("save_vcs_summary", {"comment": comment}) in fake_artifacts_service.calls


@pytest.mark.asyncio
async def test_process_inline_comments_iterates_all(
        capsys: pytest.CaptureFixture,
        fake_vcs_client: FakeVCSClient,
        fake_artifacts_service: FakeArtifactsService,
        review_dry_run_comment_gateway: ReviewDryRunCommentGateway
):
    """Dry-run: should iterate through all inline comments and log each."""
    comments = InlineCommentListSchema(root=[
        InlineCommentSchema(file="a.py", line=1, message="C1"),
        InlineCommentSchema(file="b.py", line=2, message="C2"),
    ])
    await review_dry_run_comment_gateway.process_inline_comments(comments)
    output = capsys.readouterr().out

    assert "[dry-run]" in output
    assert "a.py" in output
    assert "b.py" in output
    assert not any(call[0].startswith("create_") for call in fake_vcs_client.calls)

    assert ("save_vcs_inline", {"comment": comments.root[0]}) in fake_artifacts_service.calls
    assert ("save_vcs_inline", {"comment": comments.root[1]}) in fake_artifacts_service.calls


@pytest.mark.asyncio
async def test_clear_inline_comments_dry_run_no_comments(
        capsys: pytest.CaptureFixture,
        fake_vcs_client: FakeVCSClient,
        review_dry_run_comment_gateway: ReviewDryRunCommentGateway,
):
    """Dry-run: should log and do nothing when no inline comments exist."""
    fake_vcs_client.responses["get_inline_comments"] = []

    await review_dry_run_comment_gateway.clear_inline_comments()
    output = capsys.readouterr().out

    assert "[dry-run] No AI inline comments to clear" in output
    assert not any(call[0].startswith("delete_") for call in fake_vcs_client.calls)


@pytest.mark.asyncio
async def test_clear_inline_comments_dry_run_logs_each_comment(
        capsys: pytest.CaptureFixture,
        fake_vcs_client: FakeVCSClient,
        review_dry_run_comment_gateway: ReviewDryRunCommentGateway,
):
    """Dry-run: should log deletion of each inline comment without calling VCS."""
    fake_vcs_client.responses["get_inline_comments"] = [
        ReviewCommentSchema(id="1", body=f"{settings.review.inline_tag} AI inline"),
        ReviewCommentSchema(id="2", body=f"{settings.review.inline_tag} AI inline"),
    ]

    await review_dry_run_comment_gateway.clear_inline_comments()
    output = capsys.readouterr().out

    assert "[dry-run] Would clear 2 AI inline comments" in output
    assert "[dry-run] Would delete inline comment 1" in output
    assert "[dry-run] Would delete inline comment 2" in output

    assert not any(call[0].startswith("delete_") for call in fake_vcs_client.calls)


@pytest.mark.asyncio
async def test_dry_run_inline_reply_request_cleanup_does_not_delete(
        capsys: pytest.CaptureFixture,
        fake_vcs_client: FakeVCSClient,
        review_dry_run_comment_gateway: ReviewDryRunCommentGateway,
):
    fake_vcs_client.responses["get_inline_comments"] = [
        ReviewCommentSchema(id="question", body=f"Why? {settings.review.inline_reply_tag}"),
        ReviewCommentSchema(id="reply", body=InlineCommentReplySchema(message="Answer").body_with_tag),
    ]

    await review_dry_run_comment_gateway.clear_inline_replies()

    output = capsys.readouterr().out
    assert "Would delete inline reply request question" in output
    assert "Would delete inline reply request reply" not in output
    assert all(call[0] != "delete_inline_comment" for call in fake_vcs_client.calls)


@pytest.mark.asyncio
async def test_dry_run_inline_reply_request_cleanup_reports_general_comment(
        capsys: pytest.CaptureFixture,
        fake_vcs_client: FakeVCSClient,
        review_dry_run_comment_gateway: ReviewDryRunCommentGateway,
):
    fake_vcs_client.responses["get_general_comments"] = [
        ReviewCommentSchema(id="question", body=f"Why? {settings.review.inline_reply_tag}"),
        ReviewCommentSchema(id="reply", body=InlineCommentReplySchema(message="Answer").body_with_tag),
    ]

    await review_dry_run_comment_gateway.clear_inline_replies()

    output = capsys.readouterr().out
    assert "Would delete general inline reply request question" in output
    assert "Would delete general inline reply request reply" not in output
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
async def test_clear_summary_comments_dry_run_no_comments(
        capsys: pytest.CaptureFixture,
        fake_vcs_client: FakeVCSClient,
        review_dry_run_comment_gateway: ReviewDryRunCommentGateway,
):
    """Dry-run: should log and do nothing when no summary comments exist."""
    fake_vcs_client.responses["get_general_comments"] = []

    await review_dry_run_comment_gateway.clear_summary_comments()
    output = capsys.readouterr().out

    assert "[dry-run] No AI summary comments to clear" in output
    assert not any(call[0].startswith("delete_") for call in fake_vcs_client.calls)


@pytest.mark.asyncio
async def test_clear_summary_comments_dry_run_logs_each_comment(
        capsys: pytest.CaptureFixture,
        fake_vcs_client: FakeVCSClient,
        review_dry_run_comment_gateway: ReviewDryRunCommentGateway,
):
    """Dry-run: should log deletion of each summary comment without calling VCS."""
    fake_vcs_client.responses["get_general_comments"] = [
        ReviewCommentSchema(id="10", body=f"{settings.review.summary_tag} First AI summary"),
        ReviewCommentSchema(id="11", body=f"{settings.review.summary_tag} Second AI summary"),
    ]

    await review_dry_run_comment_gateway.clear_summary_comments()
    output = capsys.readouterr().out

    assert "[dry-run] Would clear 2 AI summary comments" in output
    assert "[dry-run] Would delete summary comment 10" in output
    assert "[dry-run] Would delete summary comment 11" in output

    assert not any(call[0].startswith("delete_") for call in fake_vcs_client.calls)


@pytest.mark.asyncio
async def test_clear_summary_comments_dry_run_includes_inline_fallback_comments(
        capsys: pytest.CaptureFixture,
        fake_vcs_client: FakeVCSClient,
        review_dry_run_comment_gateway: ReviewDryRunCommentGateway,
):
    """Dry-run: should preview inline-fallback comments too, matching a real clear."""
    fake_vcs_client.responses["get_general_comments"] = [
        ReviewCommentSchema(id="10", body=f"{settings.review.summary_tag} AI summary"),
        ReviewCommentSchema(id="11", body=f"{settings.review.inline_fallback_tag} AI fallback"),
        ReviewCommentSchema(id="12", body="a human wrote this"),
    ]

    await review_dry_run_comment_gateway.clear_summary_comments()
    output = capsys.readouterr().out

    assert "[dry-run] Would clear 2 AI summary comments" in output
    assert "[dry-run] Would delete summary comment 10" in output
    assert "[dry-run] Would delete summary comment 11" in output
    assert "[dry-run] Would delete summary comment 12" not in output

    assert not any(call[0].startswith("delete_") for call in fake_vcs_client.calls)


@pytest.mark.asyncio
async def test_dry_run_summary_reply_request_cleanup_does_not_delete(
        capsys: pytest.CaptureFixture,
        fake_vcs_client: FakeVCSClient,
        review_dry_run_comment_gateway: ReviewDryRunCommentGateway,
):
    fake_vcs_client.responses["get_general_comments"] = [
        ReviewCommentSchema(id="question", body=f"Which tests? {settings.review.summary_reply_tag}"),
        ReviewCommentSchema(id="reply", body=SummaryCommentReplySchema(text="Answer").body_for_request("t", "q")),
    ]

    await review_dry_run_comment_gateway.clear_summary_replies()

    output = capsys.readouterr().out
    assert "Would delete summary reply request question" in output
    assert "Would delete summary reply request reply" not in output
    assert all(call[0] != "delete_general_comment" for call in fake_vcs_client.calls)


@pytest.mark.asyncio
async def test_finalize_does_not_touch_vcs(
        fake_batching_vcs_client: FakeBatchingVCSClient,
        fake_artifacts_service: FakeArtifactsService,
):
    """Dry run should not publish anything to the VCS, even with a batching client."""
    gateway = ReviewDryRunCommentGateway(vcs=fake_batching_vcs_client, artifacts=fake_artifacts_service)

    await gateway.finalize()

    assert not any(call[0] == "publish_comments" for call in fake_batching_vcs_client.calls)
