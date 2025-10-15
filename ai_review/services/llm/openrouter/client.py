from ai_review.clients.openrouter.client import get_openrouter_http_client
from ai_review.clients.openrouter.schema import (
    OpenRouterMessageSchema,
    OpenRouterChatRequestSchema,
)
from ai_review.config import settings
from ai_review.services.llm.types import LLMClientProtocol, ChatResultSchema


class OpenRouterLLMClient(LLMClientProtocol):
    def __init__(self):
        self.http_client = get_openrouter_http_client()

    async def chat(self, prompt: str, prompt_system: str) -> ChatResultSchema:
        meta = settings.llm.meta
        request = OpenRouterChatRequestSchema(
            model=meta.model,
            messages=[
                OpenRouterMessageSchema(role="system", content=prompt_system),
                OpenRouterMessageSchema(role="user", content=prompt),
            ],
            max_tokens=meta.max_tokens,
            temperature=meta.temperature,
        )
        response = await self.http_client.chat(request)
        return ChatResultSchema(
            text=response.first_text,
            total_tokens=response.usage.total_tokens,
            prompt_tokens=response.usage.prompt_tokens,
            completion_tokens=response.usage.completion_tokens,
        )
