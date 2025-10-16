from pydantic import BaseModel, Field, ConfigDict


class GeminiPartSchema(BaseModel):
    text: str


class GeminiUsageSchema(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    prompt_token_count: int = Field(alias="promptTokenCount")
    total_tokens_count: int | None = Field(default=None, alias="totalTokenCount")
    candidates_token_count: int | None = Field(default=None, alias="candidatesTokenCount")
    output_thoughts_token_count: int | None = Field(default=None, alias="outputThoughtsTokenCount")

    @property
    def total_tokens(self) -> int:
        if self.total_tokens_count is not None:
            return self.total_tokens_count

        return (
                (self.prompt_token_count or 0)
                + (self.candidates_token_count or 0)
                + (self.output_thoughts_token_count or 0)
        )

    @property
    def prompt_tokens(self) -> int:
        return self.prompt_token_count

    @property
    def completion_tokens(self) -> int | None:
        return self.candidates_token_count or self.output_thoughts_token_count


class GeminiContentSchema(BaseModel):
    role: str = "user"
    parts: list[GeminiPartSchema] | None = None


class GeminiCandidateSchema(BaseModel):
    content: GeminiContentSchema


class GeminiGenerationConfigSchema(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    temperature: float | None = None
    max_output_tokens: int | None = Field(alias="maxOutputTokens", default=None)


class GeminiChatRequestSchema(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    contents: list[GeminiContentSchema]
    generation_config: GeminiGenerationConfigSchema | None = Field(
        alias="generationConfig",
        default=None
    )
    system_instruction: GeminiContentSchema | None = Field(
        alias="systemInstruction",
        default=None
    )


class GeminiChatResponseSchema(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    usage: GeminiUsageSchema = Field(alias="usageMetadata")
    candidates: list[GeminiCandidateSchema]

    @property
    def first_text(self) -> str:
        if not self.candidates:
            return ""

        parts = self.candidates[0].content.parts or []
        return (parts[0].text if parts else "").strip()
