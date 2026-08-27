import pytest
from pydantic import ValidationError

from ai_review.libs.config.agent import AgentConfig


def test_agent_config_defaults() -> None:
    config = AgentConfig()
    assert config.enabled is False
    assert config.max_iterations == 25
    assert config.max_protocol_violations == 2
    assert config.max_total_context_chars == 40_000
    assert config.command_timeout == 10
    assert config.max_command_output_chars == 40_000
    assert len(config.allow_commands) > 0


def test_agent_config_rejects_invalid_limits() -> None:
    with pytest.raises(ValidationError):
        AgentConfig(max_iterations=0)

    with pytest.raises(ValidationError):
        AgentConfig(max_protocol_violations=-1)

    with pytest.raises(ValidationError):
        AgentConfig(max_protocol_violations=101)

    with pytest.raises(ValidationError):
        AgentConfig(command_timeout=0)


@pytest.mark.parametrize("max_protocol_violations", [0, 100])
def test_agent_config_accepts_protocol_violation_boundaries(max_protocol_violations: int) -> None:
    config = AgentConfig(max_protocol_violations=max_protocol_violations)

    assert config.max_protocol_violations == max_protocol_violations


def test_agent_config_default_allow_commands_patterns_are_stable() -> None:
    config = AgentConfig()
    patterns = [pattern.pattern for pattern in config.allow_commands]
    assert patterns == [
        r"^ls(?:\s+.*)?$",
        r"^cat(?:\s+.*)?$",
        r"^rg(?:\s+.*)?$",
        r"^grep(?:\s+.*)?$",
        r"^git\s+(?:status|show|diff|log|rev-parse|ls-files)(?:\s+.*)?$",
    ]


def test_agent_config_default_allow_commands_match_expected_commands() -> None:
    config = AgentConfig()
    allowlist = config.allow_commands

    def is_allowed(command: str) -> bool:
        return any(pattern.fullmatch(command) for pattern in allowlist)

    assert is_allowed("ls")
    assert is_allowed("ls -la")
    assert is_allowed("cat README.md")
    assert is_allowed("rg TODO ai_review")
    assert is_allowed("grep -R foo .")
    assert is_allowed("git status")
    assert is_allowed("git diff --name-only")
    assert is_allowed("git rev-parse HEAD")

    assert not is_allowed("python -c 'print(1)'")
    assert not is_allowed("git checkout main")
    assert not is_allowed("")
