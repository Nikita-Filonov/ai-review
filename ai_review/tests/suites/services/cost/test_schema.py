import pytest

from ai_review.services.cost.schema import CostReportSchema


# ---------- tests: PERCENTAGE CALCULATIONS ----------

def test_percent_calculations() -> None:
    """
    Should correctly calculate prompt and completion percent based on total cost.
    """
    report = CostReportSchema(
        model="gpt-4",
        prompt_tokens=1000,
        completion_tokens=500,
        input_cost=0.02,
        output_cost=0.03,
        total_cost=0.05,
    )

    assert pytest.approx(report.prompt_percent, 0.1) == 40.0
    assert pytest.approx(report.completion_percent, 0.1) == 60.0


def test_percent_zero_total_cost() -> None:
    """
    Should handle total_cost=0 without division errors and return 0%.
    """
    report = CostReportSchema(
        model="gpt-4o-mini",
        prompt_tokens=100,
        completion_tokens=50,
        input_cost=0.01,
        output_cost=0.01,
        total_cost=0.0,
    )

    assert report.prompt_percent == 0.0
    assert report.completion_percent == 0.0


# ---------- tests: PRETTY LINES ----------

def test_pretty_prompt_line_format() -> None:
    """
    Should render a formatted line for prompt tokens and cost.
    """
    report = CostReportSchema(
        model="gpt-4",
        prompt_tokens=1234,
        completion_tokens=0,
        input_cost=0.012345,
        output_cost=0.0,
        total_cost=0.012345,
    )
    out = report.pretty_prompt_line

    assert "- Prompt tokens:" in out
    assert "1234" in out
    assert "USD" in out
    assert "(" in out
    assert ")" in out


def test_pretty_completion_line_format() -> None:
    """
    Should render a formatted line for completion tokens and cost.
    """
    report = CostReportSchema(
        model="gpt-4",
        prompt_tokens=0,
        completion_tokens=567,
        input_cost=0.0,
        output_cost=0.06789,
        total_cost=0.06789,
    )
    out = report.pretty_completion_line

    assert "- Completion tokens:" in out
    assert "567" in out
    assert "USD" in out


def test_pretty_total_line_format() -> None:
    """
    Should render a formatted total cost line.
    """
    report = CostReportSchema(
        model="gpt-4",
        prompt_tokens=0,
        completion_tokens=0,
        input_cost=0.0,
        output_cost=0.0,
        total_cost=1.234567,
    )
    out = report.pretty_total_line

    assert "- Total:" in out
    assert "USD" in out
    assert "1.234567" in out


# ---------- tests: MULTILINE OUTPUT ----------

def test_pretty_multiline_output() -> None:
    """
    Should produce a full formatted cost report with all parts.
    """
    report = CostReportSchema(
        model="gpt-4o-mini",
        prompt_tokens=200,
        completion_tokens=100,
        input_cost=0.002,
        output_cost=0.001,
        total_cost=0.003,
    )

    out = report.pretty()

    assert out.startswith("\n💰 Estimated Cost for `gpt-4o-mini`")
    assert "- Prompt tokens:" in out
    assert "- Completion tokens:" in out
    assert "- Total:" in out
    assert out.count("\n") >= 4
