import subprocess

import pytest

from ai_review.config import settings
from ai_review.services.git.service import GitService


def test_get_renamed_files_returns_rename_only_paths(
        monkeypatch: pytest.MonkeyPatch,
        git_service: GitService,
) -> None:
    def fake_run_git(*args: str) -> str:
        assert args == (
            "diff",
            "--name-only",
            "--diff-filter=R",
            "--find-renames=100%",
            "-z",
            "BASE",
            "HEAD",
        )
        return "new.py\0nested/renamed.py\0"

    monkeypatch.setattr(git_service, "run_git", fake_run_git)

    assert git_service.get_renamed_files("BASE", "HEAD") == ["new.py", "nested/renamed.py"]


def test_get_renamed_files_returns_empty_list(
        monkeypatch: pytest.MonkeyPatch,
        git_service: GitService,
) -> None:
    monkeypatch.setattr(git_service, "run_git", lambda *args: "")

    assert git_service.get_renamed_files("BASE", "HEAD") == []


def test_get_diff_for_file_skips_pure_rename(
        monkeypatch: pytest.MonkeyPatch,
        git_service: GitService,
) -> None:
    monkeypatch.setattr(settings.review, "ignore_pure_renames", True)

    calls: list[tuple[str, ...]] = []

    def fake_run_git(*args: str) -> str:
        calls.append(args)
        if "--diff-filter=R" in args:
            return "new.py\0"
        return "REAL_DIFF"

    monkeypatch.setattr(git_service, "run_git", fake_run_git)

    assert git_service.get_diff_for_file("BASE", "HEAD", "new.py") == ""
    assert len(calls) == 1


def test_get_diff_for_file_keeps_regular_file(
        monkeypatch: pytest.MonkeyPatch,
        git_service: GitService,
) -> None:
    monkeypatch.setattr(settings.review, "ignore_pure_renames", True)

    def fake_run_git(*args: str) -> str:
        if "--diff-filter=R" in args:
            return ""
        return "REAL_DIFF"

    monkeypatch.setattr(git_service, "run_git", fake_run_git)

    assert git_service.get_diff_for_file("BASE", "HEAD", "new.py") == "REAL_DIFF"


def test_get_diff_for_file_keeps_file_when_other_file_was_renamed(
        monkeypatch: pytest.MonkeyPatch,
        git_service: GitService,
) -> None:
    monkeypatch.setattr(settings.review, "ignore_pure_renames", True)

    calls: list[tuple[str, ...]] = []

    def fake_run_git(*args: str) -> str:
        calls.append(args)
        if "--diff-filter=R" in args:
            return "renamed.py\0"
        return "REAL_DIFF"

    monkeypatch.setattr(git_service, "run_git", fake_run_git)

    assert git_service.get_diff_for_file("BASE", "HEAD", "changed.py") == "REAL_DIFF"
    assert calls[-1] == ("diff", "--unified=3", "BASE", "HEAD", "--", "changed.py")


def test_get_diff_for_file_respects_ignore_pure_renames_flag(
        monkeypatch: pytest.MonkeyPatch,
        git_service: GitService,
) -> None:
    monkeypatch.setattr(settings.review, "ignore_pure_renames", False)

    def fake_run_git(*args: str) -> str:
        assert "--diff-filter=R" not in args
        return "REAL_DIFF"

    monkeypatch.setattr(git_service, "run_git", fake_run_git)

    assert git_service.get_diff_for_file("BASE", "HEAD", "new.py") == "REAL_DIFF"


def test_get_diff_for_file_uses_custom_unified_context(
        monkeypatch: pytest.MonkeyPatch,
        git_service: GitService,
) -> None:
    monkeypatch.setattr(settings.review, "ignore_pure_renames", False)

    calls: list[tuple[str, ...]] = []

    def fake_run_git(*args: str) -> str:
        calls.append(args)
        return "REAL_DIFF"

    monkeypatch.setattr(git_service, "run_git", fake_run_git)

    assert git_service.get_diff_for_file("BASE", "HEAD", "file.py", unified=10) == "REAL_DIFF"
    assert calls == [("diff", "--unified=10", "BASE", "HEAD", "--", "file.py")]


def test_get_diff_for_file_skips_empty_filename(
        monkeypatch: pytest.MonkeyPatch,
        git_service: GitService,
) -> None:
    def fail_run_git(*args: str) -> str:
        raise AssertionError("git should not be called for empty filename")

    monkeypatch.setattr(git_service, "run_git", fail_run_git)

    assert git_service.get_diff_for_file("BASE", "HEAD", "") == ""


def test_get_diff_uses_unified_context(
        monkeypatch: pytest.MonkeyPatch,
        git_service: GitService,
) -> None:
    def fake_run_git(*args: str) -> str:
        assert args == ("diff", "--unified=7", "BASE", "HEAD")
        return "RAW_DIFF"

    monkeypatch.setattr(git_service, "run_git", fake_run_git)

    assert git_service.get_diff("BASE", "HEAD", unified=7) == "RAW_DIFF"


def test_get_changed_files_strips_empty_lines(
        monkeypatch: pytest.MonkeyPatch,
        git_service: GitService,
) -> None:
    monkeypatch.setattr(git_service, "run_git", lambda *args: "one.py\n\n two.py \n")

    assert git_service.get_changed_files("BASE", "HEAD") == ["one.py", "two.py"]


def test_get_file_at_commit_returns_file_content(
        monkeypatch: pytest.MonkeyPatch,
        git_service: GitService,
) -> None:
    def fake_run_git(*args: str) -> str:
        assert args == ("show", "HEAD:path/to/file.py")
        return "content"

    monkeypatch.setattr(git_service, "run_git", fake_run_git)

    assert git_service.get_file_at_commit("path/to/file.py", "HEAD") == "content"


def test_get_file_at_commit_skips_empty_path(
        monkeypatch: pytest.MonkeyPatch,
        git_service: GitService,
) -> None:
    def fail_run_git(*args: str) -> str:
        raise AssertionError("git should not be called for empty file path")

    monkeypatch.setattr(git_service, "run_git", fail_run_git)

    assert git_service.get_file_at_commit("", "HEAD") is None


def test_get_file_at_commit_returns_none_when_file_missing(
        monkeypatch: pytest.MonkeyPatch,
        git_service: GitService,
) -> None:
    def fake_run_git(*args: str) -> str:
        raise subprocess.CalledProcessError(
            returncode=128,
            cmd=["git", *args],
            stderr="fatal: path not found",
        )

    monkeypatch.setattr(git_service, "run_git", fake_run_git)

    assert git_service.get_file_at_commit("missing.py", "HEAD") is None
