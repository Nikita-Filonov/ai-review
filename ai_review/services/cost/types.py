from typing import Protocol

from ai_review.services.cost.schema import CostReportSchema, CalculateCostSchema


class CostServiceProtocol(Protocol):
    def calculate(self, result: CalculateCostSchema) -> CostReportSchema | None:
        ...

    def aggregate(self) -> CostReportSchema | None:
        ...
