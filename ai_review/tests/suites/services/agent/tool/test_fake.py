import pytest

from ai_review.tests.fixtures.services.agent.tool import FakeAgentToolService


@pytest.mark.asyncio
async def test_agent_tool_fake_exposes_failure() -> None:
    tool = FakeAgentToolService(responses={"raise": True})
    with pytest.raises(RuntimeError, match="tool failed"):
        await tool.execute("git status")
    assert tool.calls == [("execute", {"command": "git status"})]
