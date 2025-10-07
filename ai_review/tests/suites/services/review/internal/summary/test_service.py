import pytest

from ai_review.services.review.internal.summary.schema import SummaryCommentSchema
from ai_review.services.review.internal.summary.service import SummaryCommentService


@pytest.mark.parametrize(
    "raw, expected",
    [
        ("Some summary", "Some summary"),
        ("   padded summary   ", "padded summary"),
        ("", ""),
        (None, ""),
    ]
)
def test_parse_model_output_normalizes_and_wraps(raw: str | None, expected: str):
    result = SummaryCommentService.parse_model_output(raw)
    assert isinstance(result, SummaryCommentSchema)
    assert result.text == expected
