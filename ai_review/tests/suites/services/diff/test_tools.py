# ai_review/tests/services/diff/test_tools.py
from pathlib import Path

import pytest

from ai_review.libs.diff.models import Diff, DiffFile, DiffHunk, DiffRange, DiffLineType, FileMode
from ai_review.services.diff import tools
from ai_review.tests.fixtures.services.git import FakeGitService


# ---------- normalize_file_path ----------

@pytest.mark.parametrize(
    ("inp", "expected"),
    [
        ("", ""),
        ("./foo/bar.py", "foo/bar.py"),
        ("a/foo.py", "foo.py"),
        ("b\\foo.py", "foo.py"),
        ("plain.py", "plain.py"),
    ],
)
def test_normalize_file_path_variants(inp: str, expected: str) -> None:
    assert tools.normalize_file_path(inp) == expected


# ---------- find_diff_file ----------

def make_dummy_file(orig: str = "a/x.py", new: str = "b/x.py") -> DiffFile:
    hunk = DiffHunk(
        header="",
        orig_range=DiffRange(1, 0, []),
        new_range=DiffRange(1, 0, []),
        lines=[],
    )
    return DiffFile(header="hdr", mode=FileMode.MODIFIED, orig_name=orig, new_name=new, hunks=[hunk])


def test_find_diff_file_found_by_newname() -> None:
    f = make_dummy_file(new="b/test.py")
    diff = Diff(files=[f], raw="raw")
    assert tools.find_diff_file(diff, "test.py") is f


def test_find_diff_file_found_by_orig_name() -> None:
    f = make_dummy_file(orig="a/old.py")
    diff = Diff(files=[f], raw="raw")
    assert tools.find_diff_file(diff, "old.py") is f


def test_find_diff_file_not_found_returns_none() -> None:
    diff = Diff(files=[make_dummy_file()], raw="raw")
    assert tools.find_diff_file(diff, "not_exist.py") is None


# ---------- read_snapshot ----------

def test_read_snapshot_prefers_git(monkeypatch: pytest.MonkeyPatch, fake_git_service: FakeGitService) -> None:
    fake_git_service.responses["get_file_at_commit"] = "from git"
    monkeypatch.setattr(tools, "GitService", lambda: fake_git_service)

    assert tools.read_snapshot("foo.py", head_sha="HEAD") == "from git"


def test_read_snapshot_fallback_to_filesystem(
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
        fake_git_service: FakeGitService,
) -> None:
    file = tmp_path / "file.txt"
    file.write_text("hello")

    fake_git_service.responses["get_file_at_commit"] = None
    monkeypatch.setattr(tools, "GitService", lambda: fake_git_service)

    result = tools.read_snapshot(str(file))
    assert result == "hello"


def test_read_snapshot_returns_none_if_missing(
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
        fake_git_service: FakeGitService,
) -> None:
    fake_git_service.responses["get_file_at_commit"] = None
    monkeypatch.setattr(tools, "GitService", lambda: fake_git_service)

    assert tools.read_snapshot(str(tmp_path / "nope.txt")) is None


# ---------- marker_for_line ----------

def test_marker_for_line_added(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(tools.settings.review, "review_added_marker", "# A")
    assert "# A" in tools.marker_for_line(DiffLineType.ADDED)
    assert "# A" in tools.marker_for_line(added=True)


def test_marker_for_line_removed(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(tools.settings.review, "review_removed_marker", "# R")
    assert "# R" in tools.marker_for_line(DiffLineType.REMOVED)
    assert "# R" in tools.marker_for_line(removed=True)


def test_marker_for_line_empty(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(tools.settings.review, "review_added_marker", "# A")
    monkeypatch.setattr(tools.settings.review, "review_removed_marker", "# R")
    assert tools.marker_for_line() == ""
