from ai_review.libs.diff.models import FileMode, DiffLineType, DiffFile
from ai_review.libs.diff.parser import DiffParser


# ---------- helpers ----------


def parse_and_get_file(raw_diff: str) -> DiffFile:
    """Helper: parse diff and return the first file."""
    diff = DiffParser.parse(raw_diff)
    assert diff.files, "Expected at least one parsed file"
    return diff.files[0]


# ---------- tests ----------

def test_parse_added_lines_only() -> None:
    """Should correctly parse diff with only added lines."""
    raw_diff = """diff --git a/x b/x
index 0000000..1111111 100644
--- a/x
+++ b/x
@@ -0,0 +1,2 @@
+line1
+line2
"""
    file = parse_and_get_file(raw_diff)

    assert file.mode == FileMode.MODIFIED
    assert file.orig_name == "x"
    assert file.new_name == "x"
    assert len(file.hunks) == 1

    added_lines: list[str] = [
        line.content for line in file.hunks[0].new_range.lines if line.type is DiffLineType.ADDED
    ]
    assert added_lines == ["line1", "line2"]


def test_parse_removed_lines_only() -> None:
    """Should correctly parse diff with only removed lines."""
    raw_diff = """diff --git a/x b/x
index 2222222..3333333 100644
--- a/x
+++ b/x
@@ -1,2 +0,0 @@
-line1
-line2
"""
    file = parse_and_get_file(raw_diff)

    assert file.mode == FileMode.MODIFIED
    removed_lines: list[str] = [
        line.content for line in file.hunks[0].orig_range.lines if line.type is DiffLineType.REMOVED
    ]
    assert removed_lines == ["line1", "line2"]


def test_parse_added_and_removed_lines() -> None:
    """Should parse diff with added, removed and unchanged lines."""
    raw_diff = """diff --git a/x b/x
index 4444444..5555555 100644
--- a/x
+++ b/x
@@ -1,3 +1,3 @@
 line1
-line2
+line2_changed
 line3
"""
    file = parse_and_get_file(raw_diff)
    hunk = file.hunks[0]

    assert [line.content for line in hunk.lines] == [
        "line1",
        "line2",
        "line2_changed",
        "line3",
    ]
    assert hunk.lines[0].type == DiffLineType.UNCHANGED
    assert hunk.lines[1].type == DiffLineType.REMOVED
    assert hunk.lines[2].type == DiffLineType.ADDED
    assert hunk.lines[3].type == DiffLineType.UNCHANGED


def test_parse_new_file_mode() -> None:
    """Should mark file as NEW when old side is /dev/null."""
    raw_diff = """diff --git a/x b/x
new file mode 100644
--- /dev/null
+++ b/x
@@ -0,0 +1,1 @@
+new line
"""
    file = parse_and_get_file(raw_diff)

    assert file.mode == FileMode.NEW
    assert file.new_name == "x"
    assert [line.content for line in file.hunks[0].new_range.lines] == ["new line"]


def test_parse_deleted_file_mode() -> None:
    """Should mark file as DELETED when new side is /dev/null."""
    raw_diff = """diff --git a/x b/x
deleted file mode 100644
--- a/x
+++ /dev/null
@@ -1,1 +0,0 @@
-old line
"""
    file = parse_and_get_file(raw_diff)

    assert file.mode == FileMode.DELETED
    assert file.orig_name == "x"
    assert [line.content for line in file.hunks[0].orig_range.lines] == ["old line"]
