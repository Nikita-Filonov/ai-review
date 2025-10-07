import pytest

from ai_review.config import settings
from ai_review.services.review.internal.inline.schema import (
    InlineCommentSchema,
    InlineCommentListSchema,
)


def test_normalize_file_and_message():
    comment = InlineCommentSchema(file=" \\src\\main.py ", line=10, message="  fix bug  ")
    assert comment.file == "src/main.py"
    assert comment.message == "fix bug"


def test_body_without_suggestion():
    comment = InlineCommentSchema(file="a.py", line=1, message="use f-string")
    assert comment.body == "use f-string"
    assert settings.review.inline_tag not in comment.body


def test_body_with_suggestion():
    comment = InlineCommentSchema(
        file="a.py",
        line=2,
        message="replace concatenation with f-string",
        suggestion='print(f"Hello {name}")',
    )
    expected = (
        "replace concatenation with f-string\n\n"
        "```suggestion\nprint(f\"Hello {name}\")\n```"
    )
    assert comment.body == expected


def test_body_with_tag(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(settings.review, "inline_tag", "#ai-inline")
    comment = InlineCommentSchema(file="a.py", line=3, message="something")
    assert comment.body_with_tag.endswith("\n\n#ai-inline")
    assert settings.review.inline_tag not in comment.body


def test_fallback_body(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(settings.review, "inline_tag", "#ai-inline")
    comment = InlineCommentSchema(file="a.py", line=42, message="missing check")
    assert comment.fallback_body.startswith("**a.py:42** — missing check")


def test_dedup_key_differs_on_message_and_suggestion():
    c1 = InlineCommentSchema(file="a.py", line=1, message="msg one")
    c2 = InlineCommentSchema(file="a.py", line=1, message="msg one", suggestion="x = 1")
    assert c1.dedup_key != c2.dedup_key


def test_list_dedupe_removes_duplicates():
    c1 = InlineCommentSchema(file="a.py", line=1, message="msg one")
    c2 = InlineCommentSchema(file="a.py", line=1, message="msg one")
    c3 = InlineCommentSchema(file="a.py", line=2, message="msg two")

    comment_list = InlineCommentListSchema(root=[c1, c2, c3])
    comment_list = comment_list.dedupe()

    assert len(comment_list.root) == 2
    dedup_messages = [c.message for c in comment_list.root]
    assert "msg one" in dedup_messages
    assert "msg two" in dedup_messages
