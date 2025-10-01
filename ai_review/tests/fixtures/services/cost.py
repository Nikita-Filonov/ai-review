import pytest

from ai_review.services.cost.schema import CostReportSchema
from ai_review.services.cost.types import CostServiceProtocol
from ai_review.services.llm.types import ChatResultSchema


class FakeCostService(CostServiceProtocol):
    def __init__(self):
        self.calls: list[tuple[str, dict]] = []
        self.reports: list[CostReportSchema] = []
        self.calculated_results: list[ChatResultSchema] = []

    def calculate(self, result: ChatResultSchema) -> CostReportSchema:
        self.calls.append(("calculate", {"result": result}))
        self.calculated_results.append(result)

        report = CostReportSchema(
            model="fake-model",
            prompt_tokens=result.prompt_tokens or 10,
            completion_tokens=result.completion_tokens or 5,
            input_cost=0.001,
            output_cost=0.002,
            total_cost=0.003,
        )
        self.reports.append(report)
        return report

    def aggregate(self) -> CostReportSchema | None:
        self.calls.append(("aggregate", {}))

        if not self.reports:
            return None

        total_cost = sum(r.total_cost for r in self.reports)
        return CostReportSchema(
            model="fake-model",
            total_cost=total_cost,
            input_cost=0.001 * len(self.reports),
            output_cost=0.002 * len(self.reports),
            prompt_tokens=sum(r.prompt_tokens for r in self.reports),
            completion_tokens=sum(r.completion_tokens for r in self.reports),
        )


@pytest.fixture
def fake_cost_service() -> "FakeCostService":
    return FakeCostService()
