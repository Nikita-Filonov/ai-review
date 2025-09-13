from clients.gemini.client import get_gemini_http_client
from clients.gemini.schema import (
    GeminiPartSchema,
    GeminiContentSchema,
    GeminiChatRequestSchema,
    GeminiGenerationConfigSchema,
)
from config import settings
from services.llm.types import LLMClient, ChatResult


class GeminiLLMClient(LLMClient):
    def __init__(self):
        self.http_client = get_gemini_http_client()

    async def chat(self, prompt: str) -> ChatResult:
        request = GeminiChatRequestSchema(
            contents=[GeminiContentSchema(parts=[GeminiPartSchema(text=prompt)])],
            generation_config=GeminiGenerationConfigSchema(
                temperature=settings.llm.meta.temperature,
                max_output_tokens=settings.llm.meta.max_tokens,
            ),
        )
        response = await self.http_client.chat(request)
        return ChatResult(
            text=response.first_text,
            total_tokens=response.usage.total_tokens,
            prompt_tokens=response.usage.prompt_tokens,
            completion_tokens=response.usage.completion_tokens,
        )
