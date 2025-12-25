import pytest

from ai_review.config import settings
from ai_review.services.review.internal.policy.service import ReviewPolicyService


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
    assert not ReviewPolicyService.should_review_file("README.md")
    assert ReviewPolicyService.should_review_file("main.py")


def test_should_review_allows_if_no_allow_rules(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(settings.review, "ignore_changes", [])
    monkeypatch.setattr(settings.review, "allow_changes", [])
    assert ReviewPolicyService.should_review_file("file.py")


def test_should_review_allows_if_matches_allow(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(settings.review, "allow_changes", ["src/*.py"])
    assert ReviewPolicyService.should_review_file("src/main.py")
    assert not ReviewPolicyService.should_review_file("tests/test_main.py")


def test_should_review_skips_if_not_in_allow(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(settings.review, "allow_changes", ["only/*.py"])
    assert not ReviewPolicyService.should_review_file("other/file.py")


def test_ignore_has_priority_over_allow(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(settings.review, "ignore_changes", ["*.py"])
    monkeypatch.setattr(settings.review, "allow_changes", ["*.py"])
    assert not ReviewPolicyService.should_review_file("main.py")


# ---------- apply_for_files ----------

def test_apply_for_files_filters(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(settings.review, "ignore_changes", ["*.md"])
    monkeypatch.setattr(settings.review, "allow_changes", ["src/*.py"])

    files = ["README.md", "src/main.py", "tests/test_main.py"]
    allowed = ReviewPolicyService.apply_for_files(files)

    assert allowed == ["src/main.py"]


# ---------- apply_for_inline_comments ----------

def test_apply_for_inline_comments_with_limit(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(settings.review, "max_inline_comments", 2)
    comments = ["c1", "c2", "c3"]
    limited = ReviewPolicyService.apply_for_inline_comments(comments)
    assert limited == ["c1", "c2"]


def test_apply_for_inline_comments_without_limit(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(settings.review, "max_inline_comments", None)
    comments = ["c1", "c2", "c3"]
    limited = ReviewPolicyService.apply_for_inline_comments(comments)
    assert limited == comments


def test_apply_for_inline_comments_when_fewer_than_limit(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(settings.review, "max_inline_comments", 5)
    comments = ["c1", "c2"]
    limited = ReviewPolicyService.apply_for_inline_comments(comments)
    assert limited == comments


# ---------- apply_for_context_comments ----------

def test_apply_for_context_comments_with_limit(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(settings.review, "max_context_comments", 1)
    comments = ["c1", "c2"]
    limited = ReviewPolicyService.apply_for_context_comments(comments)
    assert limited == ["c1"]


def test_apply_for_context_comments_without_limit(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(settings.review, "max_context_comments", None)
    comments = ["c1", "c2", "c3"]
    limited = ReviewPolicyService.apply_for_context_comments(comments)
    assert limited == comments
