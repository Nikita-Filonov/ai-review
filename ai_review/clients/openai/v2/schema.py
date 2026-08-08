from typing import Literal

from pydantic import BaseModel, ConfigDict


class OpenAIResponseUsageSchema(BaseModel):
    total_tokens: int
    input_tokens: int
    output_tokens: int


class OpenAIInputMessageSchema(BaseModel):
    role: str
    content: str


class OpenAIResponseContentSchema(BaseModel):
    type: str
    text: str | None = None


class OpenAIResponseOutputSchema(BaseModel):
    type: str
    role: str | None = None
    content: list[OpenAIResponseContentSchema] | None = None


class OpenAIReasoningSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    effort: Literal[
        "none",
        "minimal",
        "low",
        "medium",
        "high",
        "xhigh",
        "max",
    ] | None = None
    summary: Literal["auto", "concise", "detailed"] | None = None
    context: Literal["auto", "current_turn", "all_turns"] | None = None
    mode: Literal["standard", "pro"] | None = None
    generate_summary: Literal["auto", "concise", "detailed"] | None = None


class OpenAIResponsesRequestSchema(BaseModel):
    model: str
    input: list[OpenAIInputMessageSchema]
    stream: bool = False
    reasoning: OpenAIReasoningSchema | None = None
    temperature: float | None = None
    instructions: str | None = None
    max_output_tokens: int | None = None


class OpenAIResponsesResponseSchema(BaseModel):
    usage: OpenAIResponseUsageSchema
    output: list[OpenAIResponseOutputSchema]

    @property
    def first_text(self) -> str:
        results: list[str] = []
        for block in self.output:
            if block.type == "message" and block.content:
                for content in block.content:
                    if content.type == "output_text" and content.text:
                        results.append(content.text)

        return "".join(results).strip()
