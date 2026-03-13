from typing import Any

import pytest

from ai_review.services.policy.types import PolicyServiceProtocol


class FakePolicyService(PolicyServiceProtocol):
    def __init__(self, responses: dict[str, Any] | None = None):
        self.calls: list[tuple[str, dict]] = []
        self.responses = responses or {}

    def apply_for_files(self, files: list[str]) -> list[str]:
        self.calls.append(("apply_for_files", {"files": files}))
        return self.responses.get("apply_for_files", files)

    def apply_for_inline_comments(self, comments: list) -> list:
        self.calls.append(("apply_for_inline_comments", {"comments": comments}))
        return self.responses.get("apply_for_inline_comments", comments)

    def apply_for_context_comments(self, comments: list) -> list:
        self.calls.append(("apply_for_context_comments", {"comments": comments}))
        return self.responses.get("apply_for_context_comments", comments)

    def should_review_file(self, file: str) -> bool:
        self.calls.append(("should_review_file", {"file": file}))
        return self.responses.get("should_review_file", True)

    def should_agent_run_command(self, command: str) -> bool:
        self.calls.append(("should_agent_run_command", {"command": command}))
        return self.responses.get("should_agent_run_command", True)


@pytest.fixture
def fake_policy_service() -> FakePolicyService:
    return FakePolicyService()
