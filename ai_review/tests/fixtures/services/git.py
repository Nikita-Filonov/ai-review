from typing import Any

import pytest

from ai_review.services.git.types import GitServiceProtocol


class FakeGitService(GitServiceProtocol):
    def __init__(self, responses: dict[str, Any] | None = None) -> None:
        self.calls: list[tuple[str, dict]] = []
        self.responses = responses or {}

    def get_diff(self, base_sha: str, head_sha: str, unified: int = 3) -> str:
        self.calls.append(("get_diff", {"base_sha": base_sha, "head_sha": head_sha, "unified": unified}))
        return self.responses.get("get_diff", "")

    def get_diff_for_file(self, base_sha: str, head_sha: str, file: str, unified: int = 3) -> str:
        self.calls.append(
            (
                "get_diff_for_file",
                {"base_sha": base_sha, "head_sha": head_sha, "file": file, "unified": unified}
            )
        )
        return self.responses.get("get_diff_for_file", "")

    def get_changed_files(self, base_sha: str, head_sha: str) -> list[str]:
        self.calls.append(("get_changed_files", {"base_sha": base_sha, "head_sha": head_sha}))
        return self.responses.get("get_changed_files", [])

    def get_file_at_commit(self, file_path: str, sha: str) -> str | None:
        self.calls.append(("get_file_at_commit", {"file_path": file_path, "sha": sha}))
        return self.responses.get("get_file_at_commit", None)


@pytest.fixture
def fake_git_service() -> FakeGitService:
    return FakeGitService()
