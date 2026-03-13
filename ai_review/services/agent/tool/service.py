import shlex
import subprocess
from pathlib import Path

from ai_review.config import settings
from ai_review.libs.logger import get_logger
from ai_review.libs.text import truncate_text
from ai_review.services.agent.tool.types import AgentToolServiceProtocol
from ai_review.services.policy.types import PolicyServiceProtocol

logger = get_logger("AGENT_TOOL_SERVICE")


class AgentToolService(AgentToolServiceProtocol):
    def __init__(
            self,
            policy: PolicyServiceProtocol,
            repo_dir: Path = Path(".")
    ):
        self.policy = policy
        self.repo_root = repo_dir.resolve()

        self.command_timeout = settings.agent.command_timeout
        self.max_command_output_chars = settings.agent.max_command_output_chars

    async def execute(self, command: str) -> str:
        command = (command or "").strip()
        command_preview = f"{self.repo_root}#{command}"

        if not command:
            logger.warning("Agent command rejected: empty command")
            return "Agent command rejected: empty command"

        if not self.policy.should_agent_run_command(command):
            logger.warning(f"Agent command blocked by policy: {command}")
            return f"Agent command blocked by policy: {command}"

        try:
            argv = shlex.split(command)
        except ValueError as error:
            logger.warning(f"Agent command parse error: {command} | {error}")
            return f"Agent command parse error: {command} | {error}"
        if not argv:
            logger.warning(f"Agent command rejected after parsing: {command}")
            return f"Agent command rejected after parsing: {command}"

        logger.debug(f"Running agent command: {command_preview}, timeout={self.command_timeout}s")
        try:
            result = subprocess.run(
                argv,
                cwd=self.repo_root,
                check=False,
                errors="replace",
                timeout=self.command_timeout,
                encoding="utf-8",
                capture_output=True,
            )
        except subprocess.TimeoutExpired:
            logger.warning(f"Agent command timeout: {command_preview}, timeout={self.command_timeout}s")
            return f"Agent command timeout: {command_preview}, timeout={self.command_timeout}s"
        except Exception as error:
            logger.exception(f"Agent command failed: {command_preview}:{error}")
            return f"Agent command failed: {command_preview}:{error}"

        stdout = result.stdout or ""
        stderr = result.stderr or ""
        logger.debug(
            f"Agent command finished: {command_preview}, exit_code={result.returncode}, "
            f"stdout_chars={len(stdout)}, stderr_chars={len(stderr)}"
        )

        output = (
            f"command: {command}\n"
            f"exit_code: {result.returncode}\n"
            f"stdout: {stdout}\n"
            f"stderr: {stderr}"
        )
        truncated = len(output) > self.max_command_output_chars
        if truncated:
            logger.debug(
                "Agent command output truncated: "
                f"{command}, payload_chars={len(output)}, limit={self.max_command_output_chars}"
            )

        return truncate_text(text=output, limit=self.max_command_output_chars)
