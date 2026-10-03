import pytest

from ai_review.config import settings
from ai_review.services.review.internal.inline_reply.schema import InlineCommentReplySchema
from ai_review.services.review.internal.inline_reply.tools import INLINE_REPLY_MARKER


def test_message_is_trimmed_by_validator():
    """Message should be stripped of leading/trailing whitespace."""
    schema = InlineCommentReplySchema(message="   fix this issue   ")
    assert schema.message == "fix this issue"


def test_body_without_suggestion():
    """Body should contain only message when no suggestion is provided."""
    schema = InlineCommentReplySchema(message="Use f-string")
    assert schema.body == "Use f-string"
    assert "```suggestion" not in schema.body


def test_body_with_suggestion():
    """Body should include formatted suggestion block when suggestion is present."""
    schema = InlineCommentReplySchema(
        message="Replace concatenation with f-string",
        suggestion='print(f"Hello {name}")'
    )
    expected = (
        "Replace concatenation with f-string\n\n"
        "```suggestion\nprint(f\"Hello {name}\")\n```"
    )
    assert schema.body == expected


def test_body_with_tag(monkeypatch: pytest.MonkeyPatch):
    """Replies carry the generated-comment marker, not the request tag."""
    monkeypatch.setattr(settings.review, "inline_tag", "#ai-result")
    monkeypatch.setattr(settings.review, "inline_reply_tag", "#request-reply")
    schema = InlineCommentReplySchema(message="Looks good")
    result = schema.body_with_tag
    assert result == f"Looks good\n\n#ai-result\n\n{INLINE_REPLY_MARKER}"
    assert "#request-reply" not in result
    assert "#ai-result" not in schema.body


def test_body_with_tag_and_suggestion(monkeypatch: pytest.MonkeyPatch):
    """body_with_tag should include both suggestion and tag."""
    monkeypatch.setattr(settings.review, "inline_tag", "#ai-result")
    schema = InlineCommentReplySchema(
        message="Simplify condition",
        suggestion="if x:"
    )
    result = schema.body_with_tag
    assert "```suggestion" in result
    assert result.endswith(f"\n\n#ai-result\n\n{INLINE_REPLY_MARKER}")


def test_message_cannot_be_empty():
    """Empty message should raise validation error (min_length=1)."""
    with pytest.raises(ValueError):
        InlineCommentReplySchema(message="")
