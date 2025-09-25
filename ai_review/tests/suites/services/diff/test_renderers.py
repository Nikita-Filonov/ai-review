# ai_review/tests/services/diff/test_renderers.py

import pytest

from ai_review.libs.diff.models import (
    DiffFile,
    DiffHunk,
    DiffRange,
    DiffLine,
    DiffLineType,
    FileMode,
)
from ai_review.services.diff import renderers, tools


# ---------- fixtures ----------

@pytest.fixture
def sample_diff_file() -> DiffFile:
    """
    Build a synthetic DiffFile with one hunk that simulates:

    Original file:
      1: keep A       (UNCHANGED)
      2: remove me    (REMOVED)
      3: keep B       (UNCHANGED)

    New file:
      1: keep A       (UNCHANGED)
      2: keep B       (UNCHANGED)
      3: added me     (ADDED)

    The hunk.lines sequence (like in unified diff) is:
      UNCHANGED("keep A"),
      REMOVED("remove me"),
      UNCHANGED("keep B"),
      ADDED("added me")
    """
    # unified view for hunk.lines
    line_u1 = DiffLine(DiffLineType.UNCHANGED, number=None, content="keep A", position=1)
    line_r2 = DiffLine(DiffLineType.REMOVED, number=None, content="remove me", position=2)
    line_u2 = DiffLine(DiffLineType.UNCHANGED, number=None, content="keep B", position=3)
    line_a3 = DiffLine(DiffLineType.ADDED, number=None, content="added me", position=4)

    # original and new ranges with numbering
    orig_u1 = DiffLine(DiffLineType.UNCHANGED, number=1, content="keep A", position=1)
    orig_r2 = DiffLine(DiffLineType.REMOVED, number=2, content="remove me", position=2)
    orig_u3 = DiffLine(DiffLineType.UNCHANGED, number=3, content="keep B", position=3)

    new_u1 = DiffLine(DiffLineType.UNCHANGED, number=1, content="keep A", position=1)
    new_u2 = DiffLine(DiffLineType.UNCHANGED, number=2, content="keep B", position=2)
    new_a3 = DiffLine(DiffLineType.ADDED, number=3, content="added me", position=3)

    hunk = DiffHunk(
        header="",
        orig_range=DiffRange(start=1, length=3, lines=[orig_u1, orig_r2, orig_u3]),
        new_range=DiffRange(start=1, length=3, lines=[new_u1, new_u2, new_a3]),
        lines=[line_u1, line_r2, line_u2, line_a3],
    )

    return DiffFile(
        header="diff --git a/x b/x",
        mode=FileMode.MODIFIED,
        orig_name="a/x",
        new_name="b/x",
        hunks=[hunk],
    )


@pytest.fixture(autouse=True)
def patch_marker(monkeypatch: pytest.MonkeyPatch) -> None:
    """Patch marker_for_line to use simple markers (# added / # removed)."""

    def fake_marker(line_type=None, *, added: bool = False, removed: bool = False) -> str:
        if added or line_type is DiffLineType.ADDED:
            return " # added"
        if removed or line_type is DiffLineType.REMOVED:
            return " # removed"
        return ""

    monkeypatch.setattr(tools, "marker_for_line", fake_marker)


# ---------- tests: FULL FILE ----------

def test_build_full_file_current(monkeypatch: pytest.MonkeyPatch, sample_diff_file: DiffFile) -> None:
    monkeypatch.setattr(
        "ai_review.services.diff.renderers.read_snapshot",
        lambda *_, **__: "keep A\nkeep B\nadded me",
    )
    out = renderers.build_full_file_current(sample_diff_file, "x", head_sha="HEAD")
    assert out == "1: keep A\n2: keep B\n3: added me # added"


def test_build_full_file_previous(monkeypatch: pytest.MonkeyPatch, sample_diff_file: DiffFile) -> None:
    monkeypatch.setattr(
        "ai_review.services.diff.renderers.read_snapshot",
        lambda *_, **__: "keep A\nremove me\nkeep B",
    )
    out = renderers.build_full_file_previous(sample_diff_file, "x", base_sha="BASE")
    assert out == "1: keep A\n2: remove me # removed\n3: keep B"


def test_build_full_file_diff(sample_diff_file: DiffFile) -> None:
    out = renderers.build_full_file_diff(sample_diff_file)
    assert out == (
        " 1: keep A\n"
        "-2: remove me # removed\n"
        " 2: keep B\n"
        "+3: added me # added"
    )


# ---------- tests: ONLY_* ----------

def test_build_only_added(sample_diff_file: DiffFile) -> None:
    """
    Should render only added lines.
    """
    out = renderers.build_only_added(sample_diff_file)
    assert out == "+3: added me # added"


def test_build_only_removed(sample_diff_file: DiffFile) -> None:
    """
    Should render only removed lines.
    """
    out = renderers.build_only_removed(sample_diff_file)
    assert out == "-2: remove me # removed"


def test_build_added_and_removed(sample_diff_file: DiffFile) -> None:
    """
    Should render both removed and added lines, in hunk order.
    """
    out = renderers.build_added_and_removed(sample_diff_file)
    assert out == "-2: remove me # removed\n+3: added me # added"


# ---------- tests: *_WITH_CONTEXT ----------

def test_build_only_added_with_context(sample_diff_file: DiffFile) -> None:
    """
    Should render added lines plus unchanged context lines within ±1.
    """
    out = renderers.build_only_added_with_context(sample_diff_file, context=1)
    assert out == " 2: keep B\n+3: added me # added"


def test_build_only_removed_with_context(sample_diff_file: DiffFile) -> None:
    """
    Should render removed lines plus unchanged context lines within ±1.
    """
    out = renderers.build_only_removed_with_context(sample_diff_file, context=1)
    assert out == " 1: keep A\n-2: remove me # removed\n 2: keep B"


def test_build_added_and_removed_with_context(sample_diff_file: DiffFile) -> None:
    """
    Should render both added and removed lines, plus unchanged context within ±1.
    """
    out = renderers.build_added_and_removed_with_context(sample_diff_file, context=1)
    assert out == (
        " 1: keep A\n"
        "-2: remove me # removed\n"
        " 2: keep B\n"
        "+3: added me # added"
    )


def test_build_full_file_diff_empty_file() -> None:
    """
    Should handle new empty file (mode=NEW, no hunks).
    """
    file = DiffFile(
        header="diff --git a/LICENSE b/LICENSE",
        mode=FileMode.NEW,
        orig_name="",
        new_name="LICENSE",
        hunks=[],
    )
    out = renderers.build_full_file_diff(file)
    assert "New empty file: LICENSE" in out or "No matching lines" in out


def test_build_full_file_diff_none() -> None:
    """
    Should handle case when diff target is None.
    """
    out = renderers.build_full_file_diff(None)
    assert "Diff target not found" in out or out == ""
