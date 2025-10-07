from datetime import datetime, UTC

from pydantic import BaseModel, Field


class LLMArtifactSchema(BaseModel):
    id: str
    prompt: str
    response: str | None = None
    timestamp: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())
    prompt_system: str
