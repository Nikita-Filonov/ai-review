from ai_review.clients.ollama.client import get_ollama_http_client
from ai_review.clients.ollama.schema import OllamaChatRequestSchema, OllamaMessageSchema, OllamaOptionsSchema
from ai_review.config import settings
from ai_review.services.llm.types import LLMClientProtocol, ChatResultSchema


class OllamaLLMClient(LLMClientProtocol):
    def __init__(self):
        self.http_client = get_ollama_http_client()

    async def chat(self, prompt: str, prompt_system: str) -> ChatResultSchema:
        meta = settings.llm.meta
        request = OllamaChatRequestSchema(
            model=meta.model,
            options=OllamaOptionsSchema(
                stop=meta.stop,
                seed=meta.seed,
                top_p=meta.top_p,
                num_ctx=meta.num_ctx,
                temperature=meta.temperature,
                num_predict=meta.max_tokens,
                repeat_penalty=meta.repeat_penalty,
            ),
            messages=[
                OllamaMessageSchema(role="system", content=prompt_system),
                OllamaMessageSchema(role="user", content=prompt),
            ],
        )
        response = await self.http_client.chat(request)
        return ChatResultSchema(
            text=response.first_text,
            total_tokens=response.usage.total_tokens if response.usage else None,
            prompt_tokens=response.usage.prompt_tokens if response.usage else None,
            completion_tokens=response.usage.completion_tokens if response.usage else None,
        )
