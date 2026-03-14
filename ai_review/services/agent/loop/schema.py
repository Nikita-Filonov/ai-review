import json
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field, model_validator, field_validator


class AgentAction(StrEnum):
    FINAL = "FINAL"
    TOOL_CALL = "TOOL_CALL"

    @property
    def is_final(self) -> bool:
        return self == self.FINAL


class AgentStepSchema(BaseModel):
    action: AgentAction
    command: str | None = None
    content: str | None = None

    @model_validator(mode="after")
    def validate_shape(self):
        if self.action == AgentAction.TOOL_CALL:
            if not (self.command or "").strip():
                raise ValueError("command is required for TOOL_CALL")
            if self.content is not None:
                raise ValueError("content must be omitted for TOOL_CALL")

        if self.action == AgentAction.FINAL and not self.content:
            raise ValueError("content is required for FINAL")

        return self

    @field_validator("command", "content")
    def normalize_fields(cls, value: str) -> str:
        return (value or "").strip()

    @field_validator("content", mode="before")
    def normalize_content_to_str(cls, value: Any) -> str | None:
        if value is None or isinstance(value, str):
            return value
        return json.dumps(value, ensure_ascii=False)


class AgentTraceSchema(BaseModel):
    step: AgentStepSchema
    warning: str | None = None
    iteration: int
    raw_output: str
    tool_output: str | None = None
    total_tokens: int | None = None
    prompt_tokens: int | None = None
    completion_tokens: int | None = None

    @field_validator("warning", "raw_output", "tool_output")
    def normalize_fields(cls, value: str) -> str:
        return (value or "").strip()


class AgentLoopResultSchema(BaseModel):
    traces: list[AgentTraceSchema] = Field(default_factory=list)
    final_text: str
    stop_reason: str

    @property
    def total_tokens(self) -> int:
        return sum((trace.total_tokens or 0) for trace in self.traces)

    @property
    def prompt_tokens(self) -> int:
        return sum((trace.prompt_tokens or 0) for trace in self.traces)

    @property
    def completion_tokens(self) -> int:
        return sum((trace.completion_tokens or 0) for trace in self.traces)
