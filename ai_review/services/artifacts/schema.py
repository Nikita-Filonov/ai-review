from datetime import datetime, timezone

from pydantic import BaseModel, Field


class LLMArtifactSchema(BaseModel):
    id: str
    prompt: str
    response: str | None = None
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    prompt_system: str
