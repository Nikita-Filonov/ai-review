import pytest

from ai_review.services.review.internal.inline.schema import InlineCommentSchema
from ai_review.tests.fixtures.services.review.gateway.review_comment_gateway import FakeReviewCommentGateway


@pytest.mark.asyncio
async def test_comment_gateway_fake_records_individual_inline_comment() -> None:
    fake = FakeReviewCommentGateway()
    comment = InlineCommentSchema(file="file.py", line=1, message="finding")
    await fake.process_inline_comment(comment)
    assert fake.calls[-1] == ("process_inline_comment", {"comment": comment})
