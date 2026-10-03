from pathlib import Path

import pytest

from ai_review.libs.config.llm.base import LLMConfigBase
from ai_review.libs.constants.llm_provider import LLMProvider


def test_llm_config_prefers_explicit_pricing_file(tmp_path: Path) -> None:
    pricing = tmp_path / "pricing.yaml"
    pricing.write_text("demo:\n  input: 0.1\n  output: 0.2\n", encoding="utf-8")
    config = LLMConfigBase(provider=LLMProvider.OPENAI, pricing_file=pricing)
    assert config.pricing_file_or_default == pricing
    assert config.load_pricing()["demo"].output == 0.2


@pytest.mark.parametrize(
    ("model", "input_per_million", "output_per_million"),
    [
        ("gpt-4.1", 2.00, 8.00),
        ("gpt-5.6-sol", 4.00, 20.00),
        ("gemini-2.5-flash", 0.30, 2.50),
        ("gemini-3.1-pro-preview", 2.00, 12.00),
        ("gemini-3.5-flash", 1.50, 9.00),
        ("claude-sonnet-4-6", 3.00, 15.00),
        ("claude-sonnet-5", 2.00, 10.00),
    ],
)
def test_builtin_pricing_is_per_token(
        model: str,
        input_per_million: float,
        output_per_million: float,
) -> None:
    pricing = LLMConfigBase(provider=LLMProvider.OPENAI).load_pricing()[model]

    assert pricing.input * 1_000_000 == pytest.approx(input_per_million)
    assert pricing.output * 1_000_000 == pytest.approx(output_per_million)
