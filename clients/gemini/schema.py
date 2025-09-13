from pydantic import BaseModel, Field, ConfigDict


class GeminiPartSchema(BaseModel):
    text: str


class GeminiUsageSchema(BaseModel):
    total_tokens: int = Field(alias="totalTokenCount")
    prompt_tokens: int = Field(alias="promptTokenCount")
    completion_tokens: int = Field(alias="candidatesTokenCount")


class GeminiContentSchema(BaseModel):
    role: str = "user"
    parts: list[GeminiPartSchema]


class GeminiCandidateSchema(BaseModel):
    content: GeminiContentSchema


class GeminiGenerationConfigSchema(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    temperature: float
    max_output_tokens: int = Field(alias="maxOutputTokens")


class GeminiChatRequestSchema(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    contents: list[GeminiContentSchema]
    generation_config: GeminiGenerationConfigSchema | None = Field(
        alias="generationConfig",
        default=None
    )


class GeminiChatResponseSchema(BaseModel):
    usage: GeminiUsageSchema = Field(alias="usageMetadata")
    candidates: list[GeminiCandidateSchema]

    @property
    def first_text(self) -> str:
        if not self.candidates:
            return ""

        parts = self.candidates[0].content.parts
        return (parts[0].text if parts else "").strip()
