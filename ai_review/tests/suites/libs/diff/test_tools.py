import pytest

from ai_review.libs.diff import tools
from ai_review.libs.diff.models import DiffLineType


# ---------- tests: is_source_line ----------

def test_is_source_line_regular_added():
    """Should return True for a normal added line (+content)."""
    assert tools.is_source_line("+foo") is True


def test_is_source_line_regular_removed():
    """Should return True for a normal removed line (-content)."""
    assert tools.is_source_line("-bar") is True


def test_is_source_line_regular_unchanged():
    """Should return True for a normal unchanged line (space prefix)."""
    assert tools.is_source_line(" baz") is True


def test_is_source_line_no_newline_marker():
    """Should return False for the special diff marker line."""
    assert tools.is_source_line(r"\ No newline at end of file") is False


def test_is_source_line_empty_or_headers():
    """Should return False for empty line or diff headers (---/+++)."""
    assert tools.is_source_line("") is False
    assert tools.is_source_line("--- a/file.py") is False
    assert tools.is_source_line("+++ b/file.py") is False


# ---------- tests: get_line_type ----------

def test_get_line_type_added():
    """Should classify '+' prefix as ADDED."""
    assert tools.get_line_type("+foo") == DiffLineType.ADDED


def test_get_line_type_removed():
    """Should classify '-' prefix as REMOVED."""
    assert tools.get_line_type("-bar") == DiffLineType.REMOVED


def test_get_line_type_unchanged():
    """Should classify ' ' prefix as UNCHANGED."""
    assert tools.get_line_type(" baz") == DiffLineType.UNCHANGED


def test_get_line_type_empty_raises():
    """Should raise ValueError if line is empty."""
    with pytest.raises(ValueError):
        tools.get_line_type("")


def test_get_line_type_unknown_prefix_raises():
    """Should raise ValueError if line starts with unknown prefix."""
    with pytest.raises(ValueError):
        tools.get_line_type("@@ -1,2 +1,2 @@")
