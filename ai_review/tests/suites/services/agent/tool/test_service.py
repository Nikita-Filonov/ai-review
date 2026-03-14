import subprocess
from pathlib import Path

import pytest

from ai_review.config import settings
from ai_review.services.agent.tool.service import AgentToolService
from ai_review.tests.fixtures.services.policy import FakePolicyService


@pytest.mark.asyncio
async def test_execute_runs_allowed_command(
        tmp_path: Path,
        agent_tool_service: AgentToolService,
        fake_policy_service: FakePolicyService,
) -> None:
    (tmp_path / "sample.txt").write_text("hello", encoding="utf-8")
    fake_policy_service.responses["should_agent_run_command"] = True

    result = await agent_tool_service.execute("cat sample.txt")

    assert "exit_code: 0" in result
    assert "hello" in result
    assert any(call[0] == "should_agent_run_command" for call in fake_policy_service.calls)


@pytest.mark.asyncio
async def test_execute_blocks_disallowed_command(
        agent_tool_service: AgentToolService,
        fake_policy_service: FakePolicyService,
) -> None:
    fake_policy_service.responses["should_agent_run_command"] = False

    result = await agent_tool_service.execute("cat sample.txt")

    assert "blocked by policy" in result.lower()


@pytest.mark.asyncio
async def test_execute_runs_in_repo_directory(
        tmp_path: Path,
        agent_tool_service: AgentToolService,
        fake_policy_service: FakePolicyService,
) -> None:
    (tmp_path / "visible.txt").write_text("ok", encoding="utf-8")
    fake_policy_service.responses["should_agent_run_command"] = True

    result = await agent_tool_service.execute("ls")

    assert "visible.txt" in result


@pytest.mark.asyncio
async def test_execute_truncates_large_output(
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
        agent_tool_service: AgentToolService,
        fake_policy_service: FakePolicyService,
) -> None:
    huge = "x" * 5_000
    (tmp_path / "big.txt").write_text(huge, encoding="utf-8")
    fake_policy_service.responses["should_agent_run_command"] = True
    monkeypatch.setattr(settings.agent, "max_command_output_chars", 1_000)
    agent_tool_service.max_command_output_chars = 1_000

    result = await agent_tool_service.execute("cat big.txt")

    assert "output truncated" in result


@pytest.mark.asyncio
async def test_execute_rejects_empty_command(agent_tool_service: AgentToolService) -> None:
    result = await agent_tool_service.execute("   ")
    assert "empty command" in result.lower()


@pytest.mark.asyncio
async def test_execute_rejects_none_command(agent_tool_service: AgentToolService) -> None:
    result = await agent_tool_service.execute(None)  # noqa
    assert "empty command" in result.lower()


@pytest.mark.asyncio
async def test_execute_returns_parse_error_for_invalid_shell_syntax(
        agent_tool_service: AgentToolService,
        fake_policy_service: FakePolicyService,
) -> None:
    fake_policy_service.responses["should_agent_run_command"] = True

    result = await agent_tool_service.execute('"unterminated')

    assert "parse error" in result.lower()


@pytest.mark.asyncio
async def test_execute_returns_timeout_error(
        monkeypatch: pytest.MonkeyPatch,
        agent_tool_service: AgentToolService,
        fake_policy_service: FakePolicyService,
) -> None:
    fake_policy_service.responses["should_agent_run_command"] = True

    def _raise_timeout(*args, **kwargs):
        raise subprocess.TimeoutExpired(cmd=["ls"], timeout=0.01)

    monkeypatch.setattr(subprocess, "run", _raise_timeout)
    result = await agent_tool_service.execute("ls")

    assert "timeout" in result.lower()


@pytest.mark.asyncio
async def test_execute_returns_runtime_error(
        monkeypatch: pytest.MonkeyPatch,
        agent_tool_service: AgentToolService,
        fake_policy_service: FakePolicyService,
) -> None:
    fake_policy_service.responses["should_agent_run_command"] = True

    def _raise_runtime_error(*args, **kwargs):
        raise RuntimeError("boom")

    monkeypatch.setattr(subprocess, "run", _raise_runtime_error)
    result = await agent_tool_service.execute("ls")

    assert "failed" in result.lower()


@pytest.mark.asyncio
async def test_execute_captures_non_zero_exit_code(
        tmp_path: Path,
        agent_tool_service: AgentToolService,
        fake_policy_service: FakePolicyService,
) -> None:
    fake_policy_service.responses["should_agent_run_command"] = True

    result = await agent_tool_service.execute("cat nonexistent_file.txt")

    assert "exit_code: 1" in result or "exit_code: 2" in result
    assert "no such file" in result.lower() or "not found" in result.lower()


@pytest.mark.asyncio
async def test_execute_captures_stderr(
        tmp_path: Path,
        agent_tool_service: AgentToolService,
        fake_policy_service: FakePolicyService,
) -> None:
    fake_policy_service.responses["should_agent_run_command"] = True

    result = await agent_tool_service.execute("ls nonexistent_dir")

    assert "stderr:" in result
    assert "no such file" in result.lower() or "not found" in result.lower()
