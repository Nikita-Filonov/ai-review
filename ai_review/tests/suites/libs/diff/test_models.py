import pytest

from ai_review.libs.diff.models import (
    DiffLine,
    DiffLineType,
    DiffRange,
    DiffHunk,
    DiffFile,
    Diff,
    FileMode,
)


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
