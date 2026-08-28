import pytest

from ai_review.libs.diff.models import (
    DiffLine,
    DiffLineType,
    DiffRange,
    DiffHunk,
    DiffFile,
    Diff,
    FileMode,
    DiffLinePosition,
)
from ai_review.libs.diff.parser import DiffParser

TWO_HUNK_DIFF = """@@ -80,4 +80,5 @@
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

DELETION_DIFF = """@@ -1,5 +1,2 @@
 alpha
-beta
-gamma
-delta
 epsilon
"""


# ---------- fixtures ----------

@pytest.fixture
def diff_file_modified() -> DiffFile:
    """
    Create a DiffFile with a single hunk containing:
      - one unchanged line "A"
      - one removed line "X"
      - one unchanged line "B"
      - one added line "Y"
    """
    orig_lines = [
        DiffLine(DiffLineType.UNCHANGED, 1, "A", 1),
        DiffLine(DiffLineType.REMOVED, 2, "X", 2),
        DiffLine(DiffLineType.UNCHANGED, 3, "B", 3),
    ]
    new_lines = [
        DiffLine(DiffLineType.UNCHANGED, 1, "A", 1),
        DiffLine(DiffLineType.UNCHANGED, 2, "B", 2),
        DiffLine(DiffLineType.ADDED, 3, "Y", 3),
    ]

    hunk = DiffHunk(
        header="test hunk",
        orig_range=DiffRange(start=1, length=3, lines=orig_lines),
        new_range=DiffRange(start=1, length=3, lines=new_lines),
        lines=[*orig_lines, new_lines[-1]],
    )

    return DiffFile(
        header="diff --git a/file b/file",
        mode=FileMode.MODIFIED,
        orig_name="a/file",
        new_name="b/file",
        hunks=[hunk],
    )


@pytest.fixture
def diff_with_modified_file(diff_file_modified: DiffFile) -> Diff:
    """Return a Diff object containing a single modified file."""
    return Diff(files=[diff_file_modified], raw="raw-diff-here")


@pytest.fixture
def two_hunk_file() -> DiffFile:
    """Two hunks where the first inserts a line, so the second is shifted by one."""
    return DiffParser.parse(TWO_HUNK_DIFF).files[0]


@pytest.fixture
def deletion_file() -> DiffFile:
    """A hunk that only deletes, so old line numbers run ahead of new ones."""
    return DiffParser.parse(DELETION_DIFF).files[0]


# ---------- tests ----------

def test_added_and_removed_lines(diff_file_modified: DiffFile) -> None:
    """added_new_lines/removed_old_lines should return correct DiffLine objects."""
    added = [line.content for line in diff_file_modified.added_new_lines()]
    removed = [line.content for line in diff_file_modified.removed_old_lines()]

    assert added == ["Y"]
    assert removed == ["X"]


def test_added_and_removed_line_numbers(diff_file_modified: DiffFile) -> None:
    """added_line_numbers/removed_line_numbers should return correct sets of numbers."""
    assert diff_file_modified.added_line_numbers() == {3}
    assert diff_file_modified.removed_line_numbers() == {2}


def test_diff_summary(diff_with_modified_file: Diff) -> None:
    """Diff.summary should include file mode, file name, and hunk info."""
    summary = diff_with_modified_file.summary()

    assert "MODIFIED b/file" in summary
    assert "Hunk: test hunk" in summary
    assert "(4 lines)" in summary  # total lines in hunk.lines


def test_changed_lines_and_files(diff_with_modified_file: Diff) -> None:
    """changed_lines should map added line numbers; changed_files should list modified files."""
    changed = diff_with_modified_file.changed_lines()
    files = diff_with_modified_file.changed_files()

    assert changed == {"b/file": [3]}
    assert files == ["b/file"]


def test_line_positions_pairs_every_line_of_every_hunk(two_hunk_file: DiffFile) -> None:
    """line_positions should pair old and new numbers for each line, hunk by hunk."""
    positions = two_hunk_file.line_positions()

    assert [(position.old_line, position.new_line) for position in positions] == [
        (80, 80),  # class Store:
        (81, 81),  # def __init__(self, session):
        (None, 82),  # + self.cache = {}
        (82, 83),  # def get(self, key):
        (83, 84),  # return self.session.get(key)
        (126, 127),  # def remove(session, key):
        (127, 128),  # entry = session.get(key)
        (128, None),  # - session.delete(entry)
        (None, 129),  # + session.mark_deleted(entry)
        (None, 130),  # + session.flush()
        (129, 131),  # session.commit()
    ]


def test_find_line_position_for_added_line(two_hunk_file: DiffFile) -> None:
    """An added line has a new number and no old number."""
    position = two_hunk_file.find_line_position(82)

    assert position is not None
    assert position.type is DiffLineType.ADDED
    assert (position.old_line, position.new_line) == (None, 82)


def test_find_line_position_for_context_line(two_hunk_file: DiffFile) -> None:
    """A context line carries both numbers, which is what GitLab needs to resolve it."""
    position = two_hunk_file.find_line_position(84)

    assert position is not None
    assert position.type is DiffLineType.UNCHANGED
    assert (position.old_line, position.new_line) == (83, 84)


def test_find_line_position_across_hunks_accounts_for_shift(two_hunk_file: DiffFile) -> None:
    """A context line in a later hunk keeps the offset introduced by an earlier one."""
    position = two_hunk_file.find_line_position(131)

    assert position is not None
    assert position.type is DiffLineType.UNCHANGED
    assert (position.old_line, position.new_line) == (129, 131)


def test_find_line_position_for_removed_line(deletion_file: DiffFile) -> None:
    """A number that matches no new line is resolved against removed old lines."""
    position = deletion_file.find_line_position(3)

    assert position is not None
    assert position.type is DiffLineType.REMOVED
    assert (position.old_line, position.new_line) == (3, None)


def test_find_line_position_prefers_the_new_side(deletion_file: DiffFile) -> None:
    """When a number is valid on both sides, the new side wins."""
    position = deletion_file.find_line_position(2)

    assert position is not None
    assert position.type is DiffLineType.UNCHANGED
    assert (position.old_line, position.new_line) == (5, 2)


def test_find_line_position_with_the_old_side_resolves_the_removed_line(deletion_file: DiffFile) -> None:
    """An explicit old side must beat the new-first guess, or the comment mis-anchors.

    Old line 2 is the removed `beta`, and new line 2 is the surviving `epsilon`.
    Without a side the new side wins, which puts a comment about a deleted line
    onto an unrelated line of code.
    """
    position = deletion_file.find_line_position(2, side="old")

    assert position is not None
    assert position.type is DiffLineType.REMOVED
    assert (position.old_line, position.new_line) == (2, None)


def test_find_line_position_with_the_old_side_resolves_a_context_line_by_its_old_number(
        deletion_file: DiffFile,
) -> None:
    """A context line addressed on the old side still yields both numbers, which GitLab needs."""
    position = deletion_file.find_line_position(5, side="old")

    assert position is not None
    assert position.type is DiffLineType.UNCHANGED
    assert (position.old_line, position.new_line) == (5, 2)


def test_find_line_position_with_the_old_side_ignores_the_new_side_entirely(two_hunk_file: DiffFile) -> None:
    """The ambiguity from the shift of an earlier hunk is resolved by the declared side.

    Old line 128 is the removed `session.delete(entry)` while new line 128 is the
    surviving `entry = session.get(key)`.
    """
    position = two_hunk_file.find_line_position(128, side="old")

    assert position is not None
    assert position.type is DiffLineType.REMOVED
    assert (position.old_line, position.new_line) == (128, None)

    assert two_hunk_file.find_line_position(128) == DiffLinePosition(DiffLineType.UNCHANGED, 127, 128)


def test_find_line_position_with_the_new_side_never_falls_back_to_the_old_one(deletion_file: DiffFile) -> None:
    """A number declared as new-file must not be silently reinterpreted as an old one."""
    assert deletion_file.find_line_position(2, side="new") == DiffLinePosition(DiffLineType.UNCHANGED, 5, 2)
    assert deletion_file.find_line_position(3, side="new") is None


def test_find_line_position_with_a_side_returns_none_for_an_unknown_line(deletion_file: DiffFile) -> None:
    """A declared side does not invent a position for a line outside every hunk."""
    assert deletion_file.find_line_position(500, side="old") is None
    assert deletion_file.find_line_position(500, side="new") is None


def test_find_line_position_returns_none_for_unknown_line(two_hunk_file: DiffFile) -> None:
    """A line outside every hunk cannot be resolved."""
    assert two_hunk_file.find_line_position(500) is None


def test_find_line_position_returns_none_without_hunks() -> None:
    """A file with no hunks resolves nothing."""
    file = DiffFile(header="", mode=FileMode.MODIFIED, orig_name="x", new_name="x", hunks=[])

    assert file.line_positions() == []
    assert file.find_line_position(1) is None


def test_changed_files_skips_deleted(diff_file_modified: DiffFile) -> None:
    """Files with mode=DELETED should not appear in changed_files or changed_lines."""
    deleted_file = DiffFile(
        header="diff --git a/deleted b/deleted",
        mode=FileMode.DELETED,
        orig_name="a/deleted",
        new_name="b/deleted",
        hunks=[],
    )
    diff = Diff(files=[diff_file_modified, deleted_file], raw="raw")

    assert "b/deleted" not in diff.changed_files()
    assert "b/deleted" not in diff.changed_lines()
