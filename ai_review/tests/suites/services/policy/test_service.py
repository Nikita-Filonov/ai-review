import re

import pytest

from ai_review.config import settings
from ai_review.services.policy.service import PolicyService


@pytest.fixture(autouse=True)
def reset_settings(monkeypatch: pytest.MonkeyPatch):
    """Сбрасываем правила перед каждым тестом."""
    monkeypatch.setattr(settings.review, "ignore_changes", [])
    monkeypatch.setattr(settings.review, "allow_changes", [])
    monkeypatch.setattr(settings.review, "max_inline_comments", None)
    monkeypatch.setattr(settings.review, "max_context_comments", None)


# ---------- should_review_file ----------

def test_should_review_skips_if_matches_ignore(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(settings.review, "ignore_changes", ["*.md"])
    assert not PolicyService.should_review_file("README.md")
    assert PolicyService.should_review_file("main.py")


def test_should_review_allows_if_no_allow_rules(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(settings.review, "ignore_changes", [])
    monkeypatch.setattr(settings.review, "allow_changes", [])
    assert PolicyService.should_review_file("file.py")


def test_should_review_allows_if_matches_allow(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(settings.review, "allow_changes", ["src/*.py"])
    assert PolicyService.should_review_file("src/main.py")
    assert not PolicyService.should_review_file("tests/test_main.py")


def test_should_review_skips_if_not_in_allow(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(settings.review, "allow_changes", ["only/*.py"])
    assert not PolicyService.should_review_file("other/file.py")


def test_ignore_has_priority_over_allow(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(settings.review, "ignore_changes", ["*.py"])
    monkeypatch.setattr(settings.review, "allow_changes", ["*.py"])
    assert not PolicyService.should_review_file("main.py")


# ---------- should_agent_run_command ----------

def test_should_agent_run_command_blocks_empty_values() -> None:
    assert not PolicyService.should_agent_run_command("")
    assert not PolicyService.should_agent_run_command("   ")


def test_should_agent_run_command_allows_by_pattern(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings.agent, "allow_commands", [re.compile(r"^ls(?:\s+.*)?$")])
    assert PolicyService.should_agent_run_command("ls")
    assert PolicyService.should_agent_run_command("ls -la")


def test_should_agent_run_command_blocks_non_matching_command(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings.agent, "allow_commands", [re.compile(r"^ls(?:\s+.*)?$")])
    assert not PolicyService.should_agent_run_command("cat README.md")


def test_should_agent_run_command_trims_spaces_before_match(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings.agent, "allow_commands", [re.compile(r"^git\s+status$")])
    assert PolicyService.should_agent_run_command("   git status   ")


# ---------- apply_for_files ----------

def test_apply_for_files_filters(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(settings.review, "ignore_changes", ["*.md"])
    monkeypatch.setattr(settings.review, "allow_changes", ["src/*.py"])

    files = ["README.md", "src/main.py", "tests/test_main.py"]
    allowed = PolicyService.apply_for_files(files)

    assert allowed == ["src/main.py"]


# ---------- apply_for_inline_comments ----------

def test_apply_for_inline_comments_with_limit(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(settings.review, "max_inline_comments", 2)
    comments = ["c1", "c2", "c3"]
    limited = PolicyService.apply_for_inline_comments(comments)
    assert limited == ["c1", "c2"]


def test_apply_for_inline_comments_without_limit(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(settings.review, "max_inline_comments", None)
    comments = ["c1", "c2", "c3"]
    limited = PolicyService.apply_for_inline_comments(comments)
    assert limited == comments


def test_apply_for_inline_comments_when_fewer_than_limit(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(settings.review, "max_inline_comments", 5)
    comments = ["c1", "c2"]
    limited = PolicyService.apply_for_inline_comments(comments)
    assert limited == comments


# ---------- apply_for_context_comments ----------

def test_apply_for_context_comments_with_limit(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(settings.review, "max_context_comments", 1)
    comments = ["c1", "c2"]
    limited = PolicyService.apply_for_context_comments(comments)
    assert limited == ["c1"]


def test_apply_for_context_comments_without_limit(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(settings.review, "max_context_comments", None)
    comments = ["c1", "c2", "c3"]
    limited = PolicyService.apply_for_context_comments(comments)
    assert limited == comments
