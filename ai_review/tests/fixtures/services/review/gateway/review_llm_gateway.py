import pytest

from ai_review.services.review.gateway.review_llm_gateway import ReviewLLMGateway
from ai_review.services.review.gateway.types import ReviewLLMGatewayProtocol
from ai_review.tests.fixtures.services.artifacts import FakeArtifactsService
from ai_review.tests.fixtures.services.cost import FakeCostService
from ai_review.tests.fixtures.services.llm import FakeLLMClient


class FakeReviewLLMGateway(ReviewLLMGatewayProtocol):
    def __init__(self):
        self.calls: list[tuple[str, dict]] = []

    async def ask(self, prompt: str, prompt_system: str) -> str:
        self.calls.append(("ask", {"prompt": prompt, "prompt_system": prompt_system}))
        return "FAKE_LLM_RESPONSE"


@pytest.fixture
def fake_review_llm_gateway() -> FakeReviewLLMGateway:
    return FakeReviewLLMGateway()


@pytest.fixture
def review_llm_gateway(
        fake_llm_client: FakeLLMClient,
        fake_cost_service: FakeCostService,
        fake_artifacts_service: FakeArtifactsService,
) -> ReviewLLMGateway:
    return ReviewLLMGateway(
        llm=fake_llm_client,
        cost=fake_cost_service,
        artifacts=fake_artifacts_service,
    )
