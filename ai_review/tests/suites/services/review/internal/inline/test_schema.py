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


def test_side_is_unset_by_default():
    """ai-review's own review path emits bare line numbers, so no side is claimed."""
    assert InlineCommentSchema(file="a.py", line=1, message="msg").side is None


def test_side_can_be_declared():
    """A caller that resolved the line against the diff carries the side it found."""
    assert InlineCommentSchema(file="a.py", line=1, message="msg", side="old").side == "old"


def test_fallback_body_marks_a_comment_on_the_old_side():
    """The fallback is read by a human, who would otherwise look up the wrong line."""
    comment = InlineCommentSchema(file="a.py", line=42, message="deleted the guard", side="old")

    assert comment.fallback_body.startswith("**a.py:42 (old side)** — deleted the guard")


def test_fallback_body_is_unchanged_for_the_new_side():
    """Only the old side needs the marker, so the usual output must not change."""
    for side in (None, "new"):
        comment = InlineCommentSchema(file="a.py", line=42, message="missing check", side=side)
        assert comment.fallback_body == "**a.py:42** — missing check"


def test_dedup_key_differs_on_side():
    """The two sides of one line number are two different lines, not a duplicate."""
    old_side = InlineCommentSchema(file="a.py", line=1, message="msg", side="old")
    new_side = InlineCommentSchema(file="a.py", line=1, message="msg", side="new")

    assert old_side.dedup_key != new_side.dedup_key
    assert len(InlineCommentListSchema(root=[old_side, new_side]).dedupe().root) == 2


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
