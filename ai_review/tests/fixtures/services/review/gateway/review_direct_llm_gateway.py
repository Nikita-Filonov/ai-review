from typing import Any

import pytest

from ai_review.services.review.gateway.review_direct_llm_gateway import ReviewDirectLLMGateway
from ai_review.services.review.gateway.types import ReviewLLMGatewayProtocol
from ai_review.tests.fixtures.services.artifacts import FakeArtifactsService
from ai_review.tests.fixtures.services.cost import FakeCostService
from ai_review.tests.fixtures.services.llm import FakeLLMClient


class FakeReviewDirectLLMGateway(ReviewLLMGatewayProtocol):
    def __init__(self, responses: dict[str, Any] | None = None):
        self.calls: list[tuple[str, dict]] = []
        self.responses = responses or {}

    async def ask(self, prompt: str, prompt_system: str) -> str:
        self.calls.append(("ask", {"prompt": prompt, "prompt_system": prompt_system}))
        return self.responses.get("ask", "FAKE_LLM_RESPONSE")


@pytest.fixture
def fake_review_direct_llm_gateway() -> FakeReviewDirectLLMGateway:
    return FakeReviewDirectLLMGateway()


@pytest.fixture
def fake_review_llm_gateway(fake_review_direct_llm_gateway: FakeReviewDirectLLMGateway) -> FakeReviewDirectLLMGateway:
    return fake_review_direct_llm_gateway


@pytest.fixture
def review_direct_llm_gateway(
        fake_llm_client: FakeLLMClient,
        fake_cost_service: FakeCostService,
        fake_artifacts_service: FakeArtifactsService,
) -> ReviewDirectLLMGateway:
    return ReviewDirectLLMGateway(
        llm=fake_llm_client,
        cost=fake_cost_service,
        artifacts=fake_artifacts_service,
    )
