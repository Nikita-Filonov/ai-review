from ai_review.services.diff.schema import DiffFileSchema
from ai_review.services.prompt.tools import format_file, normalize_prompt


def test_format_file_basic():
    diff = DiffFileSchema(file="main.py", diff="+ print('hello')")
    result = format_file(diff)
    assert result == "# File: main.py\n+ print('hello')\n"


def test_format_file_empty_diff():
    diff = DiffFileSchema(file="empty.py", diff="")
    result = format_file(diff)
    assert result == "# File: empty.py\n\n"


def test_format_file_multiline_diff():
    diff = DiffFileSchema(
        file="utils/helpers.py",
        diff="- old line\n+ new line\n+ another line"
    )
    result = format_file(diff)
    expected = (
        "# File: utils/helpers.py\n"
        "- old line\n"
        "+ new line\n"
        "+ another line\n"
    )
    assert result == expected


def test_format_file_filename_with_path():
    diff = DiffFileSchema(file="src/app/models/user.py", diff="+ class User:")
    result = format_file(diff)
    assert result.startswith("# File: src/app/models/user.py\n")
    assert result.endswith("+ class User:\n")


def test_trailing_spaces_are_removed():
    text = "hello   \nworld\t\t"
    result = normalize_prompt(text)
    assert result == "hello\nworld"


def test_multiple_empty_lines_collapsed():
    text = "line1\n\n\n\nline2"
    result = normalize_prompt(text)
    assert result == "line1\n\nline2"


def test_leading_and_trailing_whitespace_removed():
    text = "\n\n   hello\nworld   \n\n"
    result = normalize_prompt(text)
    assert result == "hello\nworld"


def test_internal_spaces_preserved():
    text = "foo    bar\nbaz\t\tqux"
    result = normalize_prompt(text)
    assert result == "foo    bar\nbaz\t\tqux"


def test_only_whitespace_string():
    text = "   \n   \n"
    result = normalize_prompt(text)
    assert result == ""


def test_no_changes_when_already_clean():
    text = "line1\nline2"
    result = normalize_prompt(text)
    assert result == text
