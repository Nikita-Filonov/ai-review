from pathlib import Path

from ai_review.libs.config.llm.base import LLMConfigBase
from ai_review.libs.constants.llm_provider import LLMProvider


def test_llm_config_prefers_explicit_pricing_file(tmp_path: Path) -> None:
    pricing = tmp_path / "pricing.yaml"
    pricing.write_text("demo:\n  input: 0.1\n  output: 0.2\n", encoding="utf-8")
    config = LLMConfigBase(provider=LLMProvider.OPENAI, pricing_file=pricing)
    assert config.pricing_file_or_default == pricing
    assert config.load_pricing()["demo"].output == 0.2
