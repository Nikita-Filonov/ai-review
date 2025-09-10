from pydantic import BaseModel


class OpenAIMessageSchema(BaseModel):
    role: str
    content: str


class OpenAIChoiceSchema(BaseModel):
    message: OpenAIMessageSchema


class OpenAIChatCompletionRequestSchema(BaseModel):
    model: str
    messages: list[OpenAIMessageSchema]
    max_tokens: int = 800
    temperature: float = 0.3


class OpenAIChatCompletionResponseSchema(BaseModel):
    choices: list[OpenAIChoiceSchema]
