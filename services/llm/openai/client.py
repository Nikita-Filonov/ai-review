from clients.openai.client import get_openai_http_client
from clients.openai.schema import OpenAIChatRequestSchema, OpenAIMessageSchema
from config import settings
from services.llm.types import LLMClient, ChatResult


class OpenAILLMClient(LLMClient):
    def __init__(self):
        self.http_client = get_openai_http_client()

    async def chat(self, prompt: str) -> ChatResult:
        meta = settings.llm.meta
        request = OpenAIChatRequestSchema(
            model=meta.model,
            messages=[OpenAIMessageSchema(role="user", content=prompt)],
            max_tokens=meta.max_tokens,
            temperature=meta.temperature,
        )
        response = await self.http_client.chat(request)
        return ChatResult(
            text=response.first_text,
            total_tokens=response.usage.total_tokens,
            prompt_tokens=response.usage.prompt_tokens,
            completion_tokens=response.usage.completion_tokens,
        )
