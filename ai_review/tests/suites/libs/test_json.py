import pytest

from ai_review.libs.json import sanitize_json_string


@pytest.mark.parametrize(
    ("actual", "expected"),
    [
        ("hello world", "hello world"),
        ("line1\nline2", "line1\\nline2"),
        ("foo\rbar", "foo\\rbar"),
        ("a\tb", "a\\tb"),
        ("abc\0def", "abc\\u0000def"),
        ("x\n\ry\t\0z", "x\\n\\ry\\t\\u0000z"),
    ],
)
def test_sanitize_basic_cases(actual: str, expected: str) -> None:
    assert sanitize_json_string(actual) == expected


def test_sanitize_multiple_control_chars() -> None:
    raw = "A\nB\rC\tD\0E"
    result = sanitize_json_string(raw)
    assert result == "A\\nB\\rC\\tD\\u0000E"


def test_sanitize_idempotent() -> None:
    raw = "foo\nbar"
    once = sanitize_json_string(raw)
    twice = sanitize_json_string(once)
    assert once == twice


def test_sanitize_empty_string() -> None:
    assert sanitize_json_string("") == ""


def test_sanitize_only_control_chars() -> None:
    raw = "\n\r\t\0"
    result = sanitize_json_string(raw)
    assert result == "\\n\\r\\t\\u0000"
