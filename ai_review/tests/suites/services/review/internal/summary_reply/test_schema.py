from ai_review.config import settings
from ai_review.services.review.internal.summary_reply.schema import SummaryCommentReplySchema


def test_body_with_tag_appends_reply_tag(monkeypatch):
    """body_with_tag should append the configured summary reply tag."""
    monkeypatch.setattr(settings.review, "summary_reply_tag", "#ai-summary-reply")
    comment = SummaryCommentReplySchema(text="This is a summary reply")

    result = comment.body_with_tag
    assert result.startswith("This is a summary reply")
    assert result.endswith("\n\n#ai-summary-reply")
    assert "\n\n#ai-summary-reply" in result


def test_inherits_text_normalization_from_parent():
    """SummaryCommentReplySchema should inherit normalization behavior."""
    comment = SummaryCommentReplySchema(text="   spaced summary reply   ")
    assert comment.text == "spaced summary reply"
