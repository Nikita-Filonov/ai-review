from ai_review.clients.azure_openai.client import get_azure_openai_http_client
from ai_review.clients.azure_openai.schema import (
    AzureOpenAIChatRequestSchema,
    AzureOpenAIMessageSchema
)
from ai_review.config import settings
from ai_review.services.llm.types import LLMClientProtocol, ChatResultSchema


class AzureOpenAILLMClient(LLMClientProtocol):
    def __init__(self):
        self.meta = settings.llm.meta
        self.http_client = get_azure_openai_http_client()

    async def chat(self, prompt: str, prompt_system: str) -> ChatResultSchema:
        request = AzureOpenAIChatRequestSchema(
            messages=[
                AzureOpenAIMessageSchema(role="system", content=prompt_system),
                AzureOpenAIMessageSchema(role="user", content=prompt),
            ],
            max_tokens=self.meta.max_tokens,
            temperature=self.meta.temperature,
        )
        response = await self.http_client.chat(request)
        return ChatResultSchema(
            text=response.first_text,
            total_tokens=response.usage.total_tokens,
            prompt_tokens=response.usage.prompt_tokens,
            completion_tokens=response.usage.completion_tokens,
        )

