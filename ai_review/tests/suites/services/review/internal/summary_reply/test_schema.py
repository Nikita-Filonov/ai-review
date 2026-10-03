from ai_review.config import settings
from ai_review.services.review.internal.summary_reply.schema import SummaryCommentReplySchema


def test_body_for_request_marks_generated_reply_and_references_question(monkeypatch):
    monkeypatch.setattr(settings.review, "summary_tag", "#ai-summary")
    comment = SummaryCommentReplySchema(text="This is a summary reply")

    assert comment.body_for_request("thread-1", 42) == (
        "This is a summary reply\n\n#ai-summary\n\n"
        "<!-- ai-review:summary-reply thread=thread-1 comment=42 -->"
    )


def test_inherits_text_normalization_from_parent():
    """SummaryCommentReplySchema should inherit normalization behavior."""
    comment = SummaryCommentReplySchema(text="   spaced summary reply   ")
    assert comment.text == "spaced summary reply"
