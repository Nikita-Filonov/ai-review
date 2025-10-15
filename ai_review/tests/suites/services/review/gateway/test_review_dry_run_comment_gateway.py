import pytest

from ai_review.services.review.gateway.review_dry_run_comment_gateway import ReviewDryRunCommentGateway
from ai_review.services.review.internal.inline.schema import InlineCommentSchema, InlineCommentListSchema
from ai_review.services.review.internal.inline_reply.schema import InlineCommentReplySchema
from ai_review.services.review.internal.summary.schema import SummaryCommentSchema
from ai_review.services.review.internal.summary_reply.schema import SummaryCommentReplySchema
from ai_review.tests.fixtures.services.vcs import FakeVCSClient


@pytest.mark.asyncio
async def test_process_inline_reply_dry_run_logs_and_no_vcs_calls(
        capsys: pytest.CaptureFixture,
        fake_vcs_client: FakeVCSClient,
        review_dry_run_comment_gateway: ReviewDryRunCommentGateway
):
    """Dry-run: should log the inline reply but not call VCS."""
    reply = InlineCommentReplySchema(message="AI reply dry-run")
    await review_dry_run_comment_gateway.process_inline_reply("t1", reply)
    output = capsys.readouterr().out

    assert "[dry-run]" in output
    assert "Would create inline reply" in output
    assert not any(call[0].startswith("create_") for call in fake_vcs_client.calls)


@pytest.mark.asyncio
async def test_process_summary_reply_dry_run_logs_and_no_vcs_calls(
        capsys: pytest.CaptureFixture,
        fake_vcs_client: FakeVCSClient,
        review_dry_run_comment_gateway: ReviewDryRunCommentGateway
):
    """Dry-run: should log the summary reply but not call VCS."""
    reply = SummaryCommentReplySchema(text="Dry-run summary reply")
    await review_dry_run_comment_gateway.process_summary_reply("t2", reply)
    output = capsys.readouterr().out

    assert "[dry-run]" in output
    assert "Would create summary reply" in output
    assert not any(call[0].startswith("create_") for call in fake_vcs_client.calls)


@pytest.mark.asyncio
async def test_process_inline_comment_dry_run_logs_and_no_vcs_calls(
        capsys: pytest.CaptureFixture,
        fake_vcs_client: FakeVCSClient,
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


@pytest.mark.asyncio
async def test_process_summary_comment_dry_run_logs_and_no_vcs_calls(
        capsys: pytest.CaptureFixture,
        fake_vcs_client: FakeVCSClient,
        review_dry_run_comment_gateway: ReviewDryRunCommentGateway
):
    """Dry-run: should log summary comment but not send it."""
    comment = SummaryCommentSchema(text="Dry-run summary comment")
    await review_dry_run_comment_gateway.process_summary_comment(comment)
    output = capsys.readouterr().out

    assert "[dry-run]" in output
    assert "Would create summary comment" in output
    assert not any(call[0].startswith("create_") for call in fake_vcs_client.calls)


@pytest.mark.asyncio
async def test_process_inline_comments_iterates_all(
        capsys: pytest.CaptureFixture,
        fake_vcs_client: FakeVCSClient,
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
