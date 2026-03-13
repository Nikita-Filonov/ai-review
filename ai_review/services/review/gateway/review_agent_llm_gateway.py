from ai_review.libs.logger import get_logger
from ai_review.services.agent.loop.types import AgentLoopServiceProtocol
from ai_review.services.artifacts.types import ArtifactsServiceProtocol
from ai_review.services.cost.types import CostServiceProtocol
from ai_review.services.llm.types import LLMClientProtocol
from ai_review.services.review.gateway.types import ReviewLLMGatewayProtocol

logger = get_logger("REVIEW_AGENT_LLM_GATEWAY")


class ReviewAgentLLMGateway(ReviewLLMGatewayProtocol):
    def __init__(
            self,
            llm: LLMClientProtocol,
            cost: CostServiceProtocol,
            artifacts: ArtifactsServiceProtocol,
            agent_loop: AgentLoopServiceProtocol,
            fallback_gateway: ReviewLLMGatewayProtocol,
    ):
        self.llm = llm
        self.cost = cost
        self.artifacts = artifacts
        self.agent_loop = agent_loop
        self.fallback_gateway = fallback_gateway

    async def ask(self, prompt: str, prompt_system: str) -> str:
        try:
            loop_result = await self.agent_loop.run(
                prompt=prompt,
                prompt_system=prompt_system,
            )
            await self.artifacts.save_llm(
                prompt=prompt,
                response=loop_result.final_text,
                cost_report=None,
                prompt_system=prompt_system,
            )
            return loop_result.final_text
        except Exception as error:
            logger.exception(f"Agent mode failed, falling back to direct chat: {error}")
            return await self.fallback_gateway.ask(prompt, prompt_system)
