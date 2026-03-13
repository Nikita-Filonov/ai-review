from ai_review.libs.text import truncate_text


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
