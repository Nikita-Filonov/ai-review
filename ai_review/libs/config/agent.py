import re

from pydantic import BaseModel, Field


class AgentConfig(BaseModel):
    enabled: bool = False
    max_iterations: int = Field(default=25, ge=1, le=100)
    allow_commands: list[re.Pattern[str]] = Field(
        default_factory=lambda: [
            re.compile(r"^ls(?:\s+.*)?$"),
            re.compile(r"^cat(?:\s+.*)?$"),
            re.compile(r"^rg(?:\s+.*)?$"),
            re.compile(r"^grep(?:\s+.*)?$"),
            re.compile(r"^git\s+(?:status|show|diff|log|rev-parse|ls-files)(?:\s+.*)?$"),
        ]
    )
    command_timeout: int = Field(default=10, ge=1, le=120)
    max_total_context_chars: int = Field(default=40_000, ge=1_000, le=500_000)
    max_command_output_chars: int = Field(default=40_000, ge=1_000, le=500_000)
