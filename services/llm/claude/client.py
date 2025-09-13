from clients.claude.client import get_claude_http_client
from clients.claude.schema import ClaudeChatRequestSchema, ClaudeMessageSchema
from config import settings
from services.llm.types import LLMClient, ChatResult


class ClaudeLLMClient(LLMClient):
    def __init__(self):
        self.http_client = get_claude_http_client()

    async def chat(self, prompt: str) -> ChatResult:
        meta = settings.llm.meta
        request = ClaudeChatRequestSchema(
            model=meta.model,
            messages=[ClaudeMessageSchema(role="user", content=prompt)],
            max_tokens=meta.max_tokens,
            temperature=meta.temperature,
        )
        response = await self.http_client.chat(request)
        return ChatResult(
            text=response.first_text,
            total_tokens=response.usage.total_tokens,
            prompt_tokens=response.usage.input_tokens,
            completion_tokens=response.usage.output_tokens,
        )
