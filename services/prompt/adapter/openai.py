from clients.openai.schema import (
    OpenAIMessageSchema,
    OpenAIChatCompletionRequestSchema,
)
from config import settings


def build_openai_chat_request(content: str) -> OpenAIChatCompletionRequestSchema:
    meta = settings.prompt.load_meta()

    return OpenAIChatCompletionRequestSchema(
        model=meta.model,
        messages=[OpenAIMessageSchema(role="user", content=content)],
        max_tokens=meta.max_tokens,
        temperature=meta.temperature,
    )
