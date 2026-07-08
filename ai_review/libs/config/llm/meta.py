from pydantic import BaseModel, Field


class LLMMetaConfig(BaseModel):
    model: str
    max_tokens: int | None = Field(default=None, ge=1)
    temperature: float | None = Field(default=None, ge=0.0, le=2.0)
