from typing import Any

import pytest

from ai_review.services.llm.types import LLMClientProtocol, ChatResultSchema


class FakeLLMClient(LLMClientProtocol):
    def __init__(self, responses: dict[str, Any] | None = None) -> None:
        self.calls: list[tuple[str, dict]] = []
        self.responses = responses or {}

    async def chat(self, prompt: str, prompt_system: str) -> ChatResultSchema:
        self.calls.append(("chat", {"prompt": prompt, "prompt_system": prompt_system}))

        return ChatResultSchema(
            text=self.responses.get("text", "FAKE_RESPONSE"),
            total_tokens=self.responses.get("total_tokens", 42),
            prompt_tokens=self.responses.get("prompt_tokens", 21),
            completion_tokens=self.responses.get("completion_tokens", 21),
        )


@pytest.fixture
def fake_llm_client() -> FakeLLMClient:
    return FakeLLMClient()
