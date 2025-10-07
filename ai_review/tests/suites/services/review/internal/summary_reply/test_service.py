import pytest

from ai_review.services.review.internal.summary_reply.schema import SummaryCommentReplySchema
from ai_review.services.review.internal.summary_reply.service import SummaryCommentReplyService


@pytest.mark.parametrize(
    "raw, expected",
    [
        ("Some reply", "Some reply"),
        ("   padded reply   ", "padded reply"),
        ("", ""),
        (None, ""),
    ],
)
def test_parse_model_output_normalizes_and_wraps(raw: str | None, expected: str):
    """parse_model_output should normalize input and wrap it into schema."""
    result = SummaryCommentReplyService.parse_model_output(raw)

    assert isinstance(result, SummaryCommentReplySchema)
    assert result.text == expected
