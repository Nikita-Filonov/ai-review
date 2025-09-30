from ai_review.clients.claude.client import get_claude_http_client
from ai_review.clients.claude.schema import ClaudeChatRequestSchema, ClaudeMessageSchema
from ai_review.config import settings
from ai_review.services.llm.types import LLMClientProtocol, ChatResultSchema


class ClaudeLLMClient(LLMClientProtocol):
    def __init__(self):
        self.http_client = get_claude_http_client()

    async def chat(self, prompt: str, prompt_system: str) -> ChatResultSchema:
        meta = settings.llm.meta
        request = ClaudeChatRequestSchema(
            model=meta.model,
            system=prompt_system,
            messages=[ClaudeMessageSchema(role="user", content=prompt)],
            max_tokens=meta.max_tokens,
            temperature=meta.temperature,
        )
        response = await self.http_client.chat(request)
        return ChatResultSchema(
            text=response.first_text,
            total_tokens=response.usage.total_tokens,
            prompt_tokens=response.usage.input_tokens,
            completion_tokens=response.usage.output_tokens,
        )
