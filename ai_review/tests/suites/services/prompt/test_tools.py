from ai_review.services.diff.schema import DiffFileSchema
from ai_review.services.prompt.tools import format_file, normalize_prompt, format_files, format_thread
from ai_review.services.vcs.types import ReviewThreadSchema, ReviewCommentSchema, UserSchema, ThreadKind


# ---------- format_file ----------

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


def test_format_file_handles_whitespace_filename():
    diff = DiffFileSchema(file="   spaced.py  ", diff="+ print('x')")
    result = format_file(diff)
    assert "# File:    spaced.py  " in result


# ---------- format_files ----------

def test_format_files_combines_multiple_diffs():
    diffs = [
        DiffFileSchema(file="a.py", diff="+ foo"),
        DiffFileSchema(file="b.py", diff="- bar"),
    ]
    result = format_files(diffs)

    assert "# File: a.py" in result
    assert "# File: b.py" in result
    assert "+ foo" in result
    assert "- bar" in result
    assert "\n\n# File: b.py" in result


def test_format_files_empty_list():
    result = format_files([])
    assert result == ""


# ---------- format_thread ----------

def test_format_thread_with_multiple_comments():
    thread = ReviewThreadSchema(
        id="t1",
        kind=ThreadKind.INLINE,
        comments=[
            ReviewCommentSchema(
                id=1, body="Looks good", author=UserSchema(name="Alice")
            ),
            ReviewCommentSchema(
                id=2, body="Maybe refactor?", author=UserSchema(username="bob")
            ),
        ],
    )
    result = format_thread(thread)

    assert "- Alice: Looks good" in result
    assert "- bob: Maybe refactor?" in result
    assert "\n\n- bob" in result


def test_format_thread_ignores_empty_bodies():
    thread = ReviewThreadSchema(
        id="t2",
        kind=ThreadKind.SUMMARY,
        comments=[
            ReviewCommentSchema(id=1, body="", author=UserSchema(name="Alice")),
            ReviewCommentSchema(id=2, body="", author=UserSchema(username="bob")),
        ],
    )
    result = format_thread(thread)
    assert result == "No comments in thread." or result == ""


def test_format_thread_handles_empty_comments_list():
    thread = ReviewThreadSchema(id="t3", kind=ThreadKind.SUMMARY, comments=[])
    result = format_thread(thread)
    assert result == "No comments in thread."


def test_format_thread_fallback_to_user_when_no_name_or_username():
    thread = ReviewThreadSchema(
        id="t4",
        kind=ThreadKind.INLINE,
        comments=[
            ReviewCommentSchema(id=1, body="Anon feedback", author=UserSchema())
        ],
    )
    result = format_thread(thread)
    assert "- User: Anon feedback" in result


# ---------- normalize_prompt ----------

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
