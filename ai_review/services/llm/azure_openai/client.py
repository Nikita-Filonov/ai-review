from ai_review.clients.azure_openai.client import get_azure_openai_http_client
from ai_review.clients.azure_openai.schema import AzureOpenAIMessage, AzureOpenAIChatRequestSchema
from ai_review.config import settings
from ai_review.services.llm.types import LLMClientProtocol, ChatResultSchema


class AzureOpenAILLMClient(LLMClientProtocol):
    def __init__(self):
        self.http_client = get_azure_openai_http_client()

    async def chat(self, prompt: str, prompt_system: str) -> ChatResultSchema:
        model_name = settings.llm.meta.model.lower()
        use_max_completion_tokens = model_name.startswith("gpt-5")

        max_tokens = settings.llm.meta.max_tokens
        max_completion_tokens = None

        if use_max_completion_tokens:
            max_completion_tokens = (
                settings.llm.meta.max_completion_tokens
                if settings.llm.meta.max_completion_tokens is not None
                else settings.llm.meta.max_tokens
            )
            max_tokens = None

        request = AzureOpenAIChatRequestSchema(
            messages=[
                AzureOpenAIMessage(role="system", content=prompt_system),
                AzureOpenAIMessage(role="user", content=prompt),
            ],
            temperature=settings.llm.meta.temperature,
            max_tokens=max_tokens,
            max_completion_tokens=max_completion_tokens,
        )
        response = await self.http_client.chat(request)
        return ChatResultSchema(
            text=response.first_text,
            total_tokens=response.usage.total_tokens,
            prompt_tokens=response.usage.prompt_tokens,
            completion_tokens=response.usage.completion_tokens,
        )
