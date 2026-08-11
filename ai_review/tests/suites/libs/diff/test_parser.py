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


def test_parse_preserves_standalone_carriage_return_inside_diff_record() -> None:
    """A bare CR belongs to file content and must not create an extra diff line."""
    raw_diff = (
        "diff --git a/x b/x\n"
        "index 0000000..1111111 100644\n"
        "--- a/x\n"
        "+++ b/x\n"
        "@@ -1,1 +1,1 @@\n"
        "-old\r\tКонецЕсли;\n"
        "+new\r\tКонецЕсли;\n"
    )

    hunk = parse_and_get_file(raw_diff).hunks[0]

    assert [line.type for line in hunk.lines] == [
        DiffLineType.REMOVED,
        DiffLineType.ADDED,
    ]
    assert [line.content for line in hunk.lines] == [
        "old\r\tКонецЕсли;",
        "new\r\tКонецЕсли;",
    ]
    assert len(hunk.orig_range.lines) == hunk.orig_range.length == 1
    assert len(hunk.new_range.lines) == hunk.new_range.length == 1


def test_parse_diff_without_file_header() -> None:
    """Should parse a bare unified diff body, as returned by the GitLab changes API."""
    raw_diff = """@@ -1,2 +1,2 @@
-old line
+new line
 kept line
"""
    file = parse_and_get_file(raw_diff)

    assert file.mode == FileMode.MODIFIED
    assert file.orig_name == ""
    assert file.new_name == ""
    assert len(file.hunks) == 1

    hunk = file.hunks[0]
    assert [line.content for line in hunk.lines] == ["old line", "new line", "kept line"]
    assert [line.type for line in hunk.lines] == [
        DiffLineType.REMOVED,
        DiffLineType.ADDED,
        DiffLineType.UNCHANGED,
    ]


def test_parse_multiple_hunks_tracks_independent_line_numbers() -> None:
    """Should number each hunk from its own header, so a shift in one hunk does not leak."""
    raw_diff = """diff --git a/x b/x
index 6666666..7777777 100644
--- a/x
+++ b/x
@@ -80,4 +80,5 @@
 class Store:
     def __init__(self, session):
+        self.cache = {}
     def get(self, key):
         return self.session.get(key)
@@ -126,4 +127,5 @@
 def remove(session, key):
     entry = session.get(key)
-    session.delete(entry)
+    session.mark_deleted(entry)
+    session.flush()
     session.commit()
"""
    file = parse_and_get_file(raw_diff)

    assert len(file.hunks) == 2

    first, second = file.hunks
    assert (first.orig_range.start, first.new_range.start) == (80, 80)
    assert (second.orig_range.start, second.new_range.start) == (126, 127)

    assert file.added_line_numbers() == {82, 129, 130}
    assert file.removed_line_numbers() == {128}

    assert [line.number for line in second.new_range.lines] == [127, 128, 129, 130, 131]
    assert [line.number for line in second.orig_range.lines] == [126, 127, 128, 129]
