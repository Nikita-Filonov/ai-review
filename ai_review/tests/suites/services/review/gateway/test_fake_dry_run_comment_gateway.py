import pytest

from ai_review.services.review.internal.inline.schema import InlineCommentSchema, InlineCommentListSchema
from ai_review.services.review.internal.inline_reply.schema import InlineCommentReplySchema
from ai_review.services.review.internal.summary.schema import SummaryCommentSchema
from ai_review.services.review.internal.summary_reply.schema import SummaryCommentReplySchema
from ai_review.tests.fixtures.services.review.gateway.review_dry_run_comment_gateway import (
    FakeReviewDryRunCommentGateway,
)


@pytest.mark.asyncio
async def test_fake_get_inline_threads_returns_default_data(
    fake_review_dry_run_comment_gateway: FakeReviewDryRunCommentGateway,
) -> None:
    fake = fake_review_dry_run_comment_gateway

    result = await fake.get_inline_threads()

    assert [item.id for item in result] == ["t1"]
    assert fake.calls == [("get_inline_threads", {})]


@pytest.mark.asyncio
async def test_fake_get_summary_threads_returns_default_data(
    fake_review_dry_run_comment_gateway: FakeReviewDryRunCommentGateway,
) -> None:
    fake = fake_review_dry_run_comment_gateway

    result = await fake.get_summary_threads()

    assert [item.id for item in result] == ["t2"]
    assert fake.calls == [("get_summary_threads", {})]


@pytest.mark.asyncio
async def test_fake_get_inline_comments_returns_default_data(
    fake_review_dry_run_comment_gateway: FakeReviewDryRunCommentGateway,
) -> None:
    fake = fake_review_dry_run_comment_gateway

    result = await fake.get_inline_comments()

    assert [item.id for item in result] == ["c1"]
    assert fake.calls == [("get_inline_comments", {})]


@pytest.mark.asyncio
async def test_fake_get_summary_comments_returns_default_data(
    fake_review_dry_run_comment_gateway: FakeReviewDryRunCommentGateway,
) -> None:
    fake = fake_review_dry_run_comment_gateway

    result = await fake.get_summary_comments()

    assert [item.id for item in result] == ["c2"]
    assert fake.calls == [("get_summary_comments", {})]


@pytest.mark.asyncio
async def test_fake_process_inline_reply_records_inputs(
    fake_review_dry_run_comment_gateway: FakeReviewDryRunCommentGateway,
) -> None:
    fake = fake_review_dry_run_comment_gateway
    reply = InlineCommentReplySchema(message="answer")

    await fake.process_inline_reply("t1", reply)

    assert fake.calls == [("process_inline_reply", {"thread_id": "t1", "reply": reply})]


@pytest.mark.asyncio
async def test_fake_process_summary_reply_records_inputs(
    fake_review_dry_run_comment_gateway: FakeReviewDryRunCommentGateway,
) -> None:
    fake = fake_review_dry_run_comment_gateway
    reply = SummaryCommentReplySchema(text="answer")

    await fake.process_summary_reply("t2", reply, request_comment_id="c2")

    assert fake.calls == [
        ("process_summary_reply", {"thread_id": "t2", "reply": reply, "request_comment_id": "c2"})
    ]


@pytest.mark.asyncio
async def test_fake_process_inline_comment_records_inputs(
    fake_review_dry_run_comment_gateway: FakeReviewDryRunCommentGateway,
) -> None:
    fake = fake_review_dry_run_comment_gateway
    comment = InlineCommentSchema(file="file.py", line=10, message="finding")

    await fake.process_inline_comment(comment)

    assert fake.calls == [("process_inline_comment", {"comment": comment})]


@pytest.mark.asyncio
async def test_fake_process_summary_comment_records_inputs(
    fake_review_dry_run_comment_gateway: FakeReviewDryRunCommentGateway,
) -> None:
    fake = fake_review_dry_run_comment_gateway
    comment = SummaryCommentSchema(text="overview")

    await fake.process_summary_comment(comment)

    assert fake.calls == [("process_summary_comment", {"comment": comment})]


@pytest.mark.asyncio
async def test_fake_process_inline_comments_records_each_comment(
    fake_review_dry_run_comment_gateway: FakeReviewDryRunCommentGateway,
) -> None:
    fake = fake_review_dry_run_comment_gateway
    comment = InlineCommentSchema(file="file.py", line=10, message="finding")
    comments = InlineCommentListSchema(root=[comment])

    await fake.process_inline_comments(comments)

    assert fake.calls == [
        ("process_inline_comments", {"comments": comments}),
        ("process_inline_comment", {"comment": comment}),
    ]
