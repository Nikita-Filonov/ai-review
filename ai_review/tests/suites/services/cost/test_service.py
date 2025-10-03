import pytest

from ai_review.libs.config.llm.base import LLMPricingConfig, LLMConfigBase
from ai_review.services.cost.schema import CostReportSchema
from ai_review.services.cost.service import CostService
from ai_review.services.llm.types import ChatResultSchema


# ---------- fixtures ----------

@pytest.fixture(autouse=True)
def fake_pricing(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(
        LLMConfigBase,
        "load_pricing",
        lambda self: {"gpt-4-test": LLMPricingConfig(input=0.000001, output=0.000002)}
    )
    monkeypatch.setattr("ai_review.config.settings.llm.meta.model", "gpt-4-test")


@pytest.fixture
def cost_service() -> CostService:
    return CostService()


@pytest.fixture
def sample_result() -> ChatResultSchema:
    return ChatResultSchema(text="result", prompt_tokens=1000, completion_tokens=500)


# ---------- tests: CALCULATE ----------

def test_calculate_basic(cost_service: CostService, sample_result: ChatResultSchema) -> None:
    """
    Should correctly calculate input/output/total cost and return report.
    """
    report = cost_service.calculate(sample_result)

    assert isinstance(report, CostReportSchema)
    assert report.model == "gpt-4-test"
    assert pytest.approx(report.input_cost, 1e-8) == 0.001
    assert pytest.approx(report.output_cost, 1e-8) == 0.001
    assert pytest.approx(report.total_cost, 1e-8) == 0.002

    assert len(cost_service.reports) == 1


def test_calculate_missing_tokens(cost_service: CostService) -> None:
    """
    Should return None if prompt_tokens or completion_tokens is None.
    """
    result = ChatResultSchema(text="result", prompt_tokens=None, completion_tokens=123)
    assert cost_service.calculate(result) is None

    result = ChatResultSchema(text="result", prompt_tokens=100, completion_tokens=None)
    assert cost_service.calculate(result) is None


def test_calculate_no_pricing(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Should return None and log warning if pricing not found.
    """
    monkeypatch.setattr("ai_review.config.settings.llm.meta.model", "unknown-model")
    monkeypatch.setattr(LLMConfigBase, "load_pricing", lambda self: {})

    service = CostService()
    result = ChatResultSchema(text="result", prompt_tokens=10, completion_tokens=5)
    out = service.calculate(result)

    assert out is None
    assert service.reports == []


# ---------- tests: AGGREGATE ----------

def test_aggregate_empty(cost_service: CostService) -> None:
    """
    Should return None when no reports exist.
    """
    assert cost_service.aggregate() is None


def test_aggregate_combines_multiple_reports(cost_service: CostService, sample_result: ChatResultSchema) -> None:
    """
    Should combine multiple cost reports into a single aggregated summary.
    """
    cost_service.calculate(sample_result)
    cost_service.calculate(sample_result)

    agg = cost_service.aggregate()
    assert isinstance(agg, CostReportSchema)

    assert agg.prompt_tokens == 2000
    assert agg.completion_tokens == 1000
    assert pytest.approx(agg.input_cost, 1e-8) == 0.002
    assert pytest.approx(agg.output_cost, 1e-8) == 0.002
    assert pytest.approx(agg.total_cost, 1e-8) == 0.004

    assert agg.model == "gpt-4-test"
