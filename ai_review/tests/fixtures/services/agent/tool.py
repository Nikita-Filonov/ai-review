from pathlib import Path
from typing import Any

import pytest

from ai_review.services.agent.tool.service import AgentToolService
from ai_review.services.agent.tool.types import AgentToolServiceProtocol
from ai_review.tests.fixtures.services.policy import FakePolicyService


class FakeAgentToolService(AgentToolServiceProtocol):
    def __init__(self, responses: dict[str, Any] | None = None):
        self.calls: list[tuple[str, dict]] = []
        self.responses = responses or {}

    async def execute(self, command: str) -> str:
        self.calls.append(("execute", {"command": command}))
        if self.responses.get("raise"):
            raise RuntimeError("tool failed")

        return self.responses.get("execute", "AGENT_TOOL_RESULT")


@pytest.fixture
def agent_tool_service(tmp_path: Path, fake_policy_service: FakePolicyService) -> AgentToolService:
    return AgentToolService(policy=fake_policy_service, repo_dir=tmp_path)


@pytest.fixture
def fake_agent_tool_service() -> FakeAgentToolService:
    return FakeAgentToolService()
