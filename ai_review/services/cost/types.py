from typing import Protocol

from ai_review.services.cost.schema import CostReportSchema
from ai_review.services.llm.types import ChatResultSchema


class CostServiceProtocol(Protocol):
    def calculate(self, result: ChatResultSchema) -> CostReportSchema | None:
        ...

    def aggregate(self) -> CostReportSchema | None:
        ...
