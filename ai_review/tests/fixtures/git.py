# ai_review/tests/conftest.py
from typing import Any

import pytest

from ai_review.services.git.types import GitServiceProtocol


class FakeGitService(GitServiceProtocol):
    """Simple fake for GitService used in tests."""

    def __init__(self, responses: dict[str, Any] | None = None) -> None:
        self.responses = responses or {}

    def get_diff(self, base_sha: str, head_sha: str, unified: int = 3) -> str:
        return self.responses.get("get_diff", "")

    def get_diff_for_file(self, base_sha: str, head_sha: str, file: str, unified: int = 3) -> str:
        return self.responses.get("get_diff_for_file", "")

    def get_changed_files(self, base_sha: str, head_sha: str) -> list[str]:
        return self.responses.get("get_changed_files", [])

    def get_file_at_commit(self, file_path: str, sha: str) -> str | None:
        return self.responses.get("get_file_at_commit", None)


@pytest.fixture
def fake_git() -> FakeGitService:
    """Default fake GitService with empty responses."""
    return FakeGitService()
