from ai_review.config import settings
from ai_review.libs.logger import get_logger
from ai_review.services.cost.schema import CostReportSchema
from ai_review.services.cost.types import CostServiceProtocol
from ai_review.services.llm.types import ChatResultSchema

logger = get_logger("COST_SERVICE")


class CostService(CostServiceProtocol):
    def __init__(self):
        self.pricing = settings.llm.load_pricing()
        self.reports: list[CostReportSchema] = []

    def calculate(self, result: ChatResultSchema) -> CostReportSchema | None:
        if (result.prompt_tokens is None) or (result.completion_tokens is None):
            return None

        model = settings.llm.meta.model
        pricing = self.pricing.get(model)
        if not pricing:
            logger.warning(f"No pricing found for {model=}, skipping cost calculation")
            return None

        input_cost = result.prompt_tokens * pricing.input
        output_cost = result.completion_tokens * pricing.output
        total_cost = input_cost + output_cost

        report = CostReportSchema(
            model=settings.llm.meta.model,
            total_cost=total_cost,
            input_cost=input_cost,
            output_cost=output_cost,
            prompt_tokens=result.prompt_tokens,
            completion_tokens=result.completion_tokens,
        )

        self.reports.append(report)
        return report

    def aggregate(self) -> CostReportSchema | None:
        if not self.reports:
            return None

        model = self.reports[0].model
        total_cost = sum(report.total_cost for report in self.reports)
        input_cost = sum(report.input_cost for report in self.reports)
        output_cost = sum(report.output_cost for report in self.reports)
        prompt_tokens = sum(report.prompt_tokens for report in self.reports)
        completion_tokens = sum(report.completion_tokens for report in self.reports)

        return CostReportSchema(
            model=model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            input_cost=input_cost,
            output_cost=output_cost,
            total_cost=total_cost,
        )
