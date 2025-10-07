import pytest

from ai_review.services.review.gateway.types import ReviewLLMGatewayProtocol


class FakeReviewLLMGateway(ReviewLLMGatewayProtocol):
    def __init__(self):
        self.calls: list[tuple[str, dict]] = []

    async def ask(self, prompt: str, prompt_system: str) -> str:
        self.calls.append(("ask", {"prompt": prompt, "prompt_system": prompt_system}))
        return "FAKE_LLM_RESPONSE"


@pytest.fixture
def fake_review_llm_gateway() -> FakeReviewLLMGateway:
    return FakeReviewLLMGateway()
