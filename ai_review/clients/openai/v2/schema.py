from pydantic import BaseModel


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


class OpenAIResponsesRequestSchema(BaseModel):
    model: str
    input: list[OpenAIInputMessageSchema]
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
