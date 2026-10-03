import pytest

from ai_review.libs.json import extract_json_objects, sanitize_json_string


@pytest.mark.parametrize(
    ("actual", "expected"),
    [
        ("hello world", "hello world"),
        ("line1\nline2", "line1\\nline2"),
        ("foo\rbar", "foo\\rbar"),
        ("a\tb", "a\\tb"),
        ("abc\0def", "abc\\u0000def"),
        ("x\n\ry\t\0z", "x\\n\\ry\\t\\u0000z"),
        ("\n\r\t\0", "\\n\\r\\t\\u0000"),
        ("", "")
    ],
)
def test_sanitize_basic_cases(actual: str, expected: str) -> None:
    assert sanitize_json_string(actual) == expected


def test_sanitize_idempotent() -> None:
    raw = "foo\nbar"
    once = sanitize_json_string(raw)
    twice = sanitize_json_string(once)
    assert once == twice


def test_extract_json_objects_from_surrounding_text() -> None:
    raw = 'reasoning {not json} {"action":"TOOL_CALL","command":"cat {file}.py"} trailing'

    assert extract_json_objects(raw) == [
        '{"action":"TOOL_CALL","command":"cat {file}.py"}',
    ]


def test_extract_json_objects_returns_complete_top_level_objects() -> None:
    raw = '{"outer":{"value":1}} and {"second":2}'

    assert extract_json_objects(raw) == [
        '{"outer":{"value":1}}',
        '{"second":2}',
    ]


def test_extract_json_objects_returns_empty_list_without_complete_object() -> None:
    assert extract_json_objects('text {"incomplete": true') == []
