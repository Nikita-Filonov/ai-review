from typing import Any

import pytest

from ai_review.services.review.gateway.review_agent_llm_gateway import ReviewAgentLLMGateway
from ai_review.services.review.gateway.types import ReviewLLMGatewayProtocol
from ai_review.tests.fixtures.services.agent.loop import FakeAgentLoopService
from ai_review.tests.fixtures.services.artifacts import FakeArtifactsService
from ai_review.tests.fixtures.services.cost import FakeCostService
from ai_review.tests.fixtures.services.llm import FakeLLMClient


class FakeFallbackReviewLLMGateway(ReviewLLMGatewayProtocol):
    def __init__(self, responses: dict[str, Any] | None = None):
        self.calls: list[tuple[str, dict]] = []
        self.responses = responses or {}

    async def ask(self, prompt: str, prompt_system: str) -> str:
        self.calls.append(("ask", {"prompt": prompt, "prompt_system": prompt_system}))
        return self.responses.get("ask", "ONE_SHOT_RESPONSE")


@pytest.fixture
def fake_fallback_review_llm_gateway() -> FakeFallbackReviewLLMGateway:
    return FakeFallbackReviewLLMGateway()


@pytest.fixture
def review_agent_llm_gateway(
        fake_llm_client: FakeLLMClient,
        fake_cost_service: FakeCostService,
        fake_artifacts_service: FakeArtifactsService,
        fake_agent_loop_service: FakeAgentLoopService,
        fake_fallback_review_llm_gateway: FakeFallbackReviewLLMGateway,
) -> ReviewAgentLLMGateway:
    return ReviewAgentLLMGateway(
        llm=fake_llm_client,
        cost=fake_cost_service,
        artifacts=fake_artifacts_service,
        agent_loop=fake_agent_loop_service,
        fallback_gateway=fake_fallback_review_llm_gateway,
    )
