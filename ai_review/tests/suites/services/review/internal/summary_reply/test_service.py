import pytest

from ai_review.services.review.internal.summary_reply.schema import SummaryCommentReplySchema
from ai_review.services.review.internal.summary_reply.service import SummaryCommentReplyService


@pytest.mark.parametrize(
    "raw, expected",
    [
        ("Some reply", "Some reply"),
        ("   padded reply   ", "padded reply"),
        ("No reply is needed for the deleted file, but add a test.",
         "No reply is needed for the deleted file, but add a test."),
    ],
)
def test_parse_model_output_normalizes_and_wraps(raw: str | None, expected: str):
    """parse_model_output should normalize input and wrap it into schema."""
    result = SummaryCommentReplyService.parse_model_output(raw)

    assert isinstance(result, SummaryCommentReplySchema)
    assert result.text == expected


@pytest.mark.parametrize("raw", [None, "", " \n\t", "No reply", "No reply.", "  NO REPLY.\n"])
def test_parse_model_output_skips_empty_and_no_reply(raw: str | None):
    assert SummaryCommentReplyService.parse_model_output(raw) is None
