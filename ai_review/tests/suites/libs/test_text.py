import pytest

from ai_review.libs.text import contains_tag, truncate_text


@pytest.mark.parametrize(
    ("text", "tag", "expected"),
    [
        ("#ai-review-inline", "#ai-review-inline", True),
        ("Reply\n\n#ai-review-inline", "#ai-review-inline", True),
        ("Please explain (#ai-review-inline-reply).", "#ai-review-inline-reply", True),
        ("#ai-review-inline-reply", "#ai-review-inline", False),
        ("#ai-review-inline-fallback", "#ai-review-inline", False),
        ("#ai-review-inline-reply-extra", "#ai-review-inline-reply", False),
        ("#ai-review-inline-reply_extra", "#ai-review-inline-reply", False),
        ("prefix#ai-review-inline", "#ai-review-inline", False),
        ("##ai-review-inline", "#ai-review-inline", False),
        ("#AI-REVIEW-INLINE", "#ai-review-inline", False),
        ("Please reply <review.reply+>", "<review.reply+>", True),
        ("Please reply <reviewXreplyyyy>", "<review.reply+>", False),
        ("Please reply", "", False),
        ("", "#ai-review-inline", False),
    ],
)
def test_contains_tag(text: str, tag: str, expected: bool):
    assert contains_tag(text, tag) is expected


def test_truncate_text_returns_original_when_shorter_than_limit():
    text = "hello"
    result = truncate_text(text=text, limit=10)
    assert result == "hello"


def test_truncate_text_returns_original_when_equal_to_limit():
    text = "exact"
    result = truncate_text(text=text, limit=5)
    assert result == "exact"


def test_truncate_text_adds_suffix_when_text_is_longer_than_limit():
    text = "abcdefghij"
    result = truncate_text(text=text, limit=4)
    expected = "abcd\n\n... output truncated (6 chars omitted)"
    assert result == expected


def test_truncate_text_with_zero_limit_keeps_only_suffix():
    text = "hello"
    result = truncate_text(text=text, limit=0)
    expected = "\n\n... output truncated (5 chars omitted)"
    assert result == expected
