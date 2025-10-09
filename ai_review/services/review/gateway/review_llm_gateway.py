from ai_review.libs.logger import get_logger
from ai_review.services.artifacts.types import ArtifactsServiceProtocol
from ai_review.services.cost.types import CostServiceProtocol
from ai_review.services.hook import hook
from ai_review.services.llm.types import LLMClientProtocol
from ai_review.services.review.gateway.types import ReviewLLMGatewayProtocol

logger = get_logger("REVIEW_LLM_GATEWAY")


class ReviewLLMGateway(ReviewLLMGatewayProtocol):
    def __init__(
            self,
            llm: LLMClientProtocol,
            cost: CostServiceProtocol,
            artifacts: ArtifactsServiceProtocol
    ):
        self.llm = llm
        self.cost = cost
        self.artifacts = artifacts

    async def ask(self, prompt: str, prompt_system: str) -> str:
        try:
            await hook.emit_chat_start(prompt, prompt_system)
            result = await self.llm.chat(prompt, prompt_system)
            if not result.text:
                logger.warning(
                    f"LLM returned an empty response (prompt length={len(prompt)} chars)"
                )

            report = self.cost.calculate(result)
            if report:
                logger.info(report.pretty())

            await hook.emit_chat_complete(result, report)
            await self.artifacts.save_llm_interaction(prompt, prompt_system, result.text)

            return result.text
        except Exception as error:
            logger.exception(f"LLM request failed: {error}")
            await hook.emit_chat_error(prompt, prompt_system)
