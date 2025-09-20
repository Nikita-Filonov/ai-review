from datetime import datetime

from pydantic import BaseModel, Field


class LLMArtifactSchema(BaseModel):
    id: str
    prompt: str
    response: str | None = None
    timestamp: str = Field(default_factory=datetime.utcnow().isoformat)
    prompt_system: str
