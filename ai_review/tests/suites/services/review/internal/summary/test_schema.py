from ai_review.config import settings
from ai_review.services.review.internal.summary.schema import SummaryCommentSchema


def test_normalize_text_strips_whitespace():
    comment = SummaryCommentSchema(text="   some summary   ")
    assert comment.text == "some summary"


def test_normalize_text_empty_becomes_empty_string():
    comment = SummaryCommentSchema(text="     ")
    assert comment.text == ""


def test_body_with_tag_appends_tag(monkeypatch):
    monkeypatch.setattr(settings.review, "summary_tag", "#ai-summary")
    comment = SummaryCommentSchema(text="Review passed")
    body = comment.body_with_tag
    assert body.startswith("Review passed")
    assert body.endswith("\n\n#ai-summary")
    assert "\n\n#ai-summary" in body
