from ai_review.clients.openai.client import get_openai_http_client
from ai_review.clients.openai.schema import OpenAIChatRequestSchema, OpenAIMessageSchema
from ai_review.config import settings
from ai_review.services.llm.types import LLMClientProtocol, ChatResultSchema


class OpenAILLMClient(LLMClientProtocol):
    def __init__(self):
        self.http_client = get_openai_http_client()

    async def chat(self, prompt: str, prompt_system: str) -> ChatResultSchema:
        meta = settings.llm.meta
        request = OpenAIChatRequestSchema(
            model=meta.model,
            messages=[
                OpenAIMessageSchema(role="system", content=prompt_system),
                OpenAIMessageSchema(role="user", content=prompt),
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
