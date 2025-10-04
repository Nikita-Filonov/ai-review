from pydantic import BaseModel, Field


class LLMMetaConfig(BaseModel):
    model: str
    max_tokens: int = Field(default=5000, ge=1)
    temperature: float = Field(default=0.3, ge=0.0, le=2.0)
