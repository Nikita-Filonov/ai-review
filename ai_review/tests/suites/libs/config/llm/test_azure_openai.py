import pytest

from ai_review.libs.config.llm.azure_openai import AzureOpenAIMetaConfig


def test_azure_openai_meta_config_defaults():
    meta = AzureOpenAIMetaConfig()
    assert meta.model == "gpt-4o-mini"
    assert meta.max_tokens is None
    assert meta.max_completion_tokens is None
    assert meta.temperature is None


def test_azure_openai_meta_config_accepts_max_completion_tokens():
    meta = AzureOpenAIMetaConfig(max_completion_tokens=1024)
    assert meta.max_completion_tokens == 1024
    assert meta.max_tokens is None


def test_azure_openai_meta_config_inherits_max_tokens():
    meta = AzureOpenAIMetaConfig(max_tokens=800)
    assert meta.max_tokens == 800
    assert meta.max_completion_tokens is None


def test_azure_openai_meta_config_rejects_both_token_fields():
    with pytest.raises(ValueError, match="mutually exclusive"):
        AzureOpenAIMetaConfig(max_tokens=500, max_completion_tokens=1024)


@pytest.mark.parametrize("field", ["max_tokens", "max_completion_tokens"])
def test_azure_openai_meta_config_rejects_zero_token_values(field: str):
    with pytest.raises(ValueError):
        AzureOpenAIMetaConfig(**{field: 0})


@pytest.mark.parametrize("field", ["max_tokens", "max_completion_tokens"])
def test_azure_openai_meta_config_rejects_negative_token_values(field: str):
    with pytest.raises(ValueError):
        AzureOpenAIMetaConfig(**{field: -1})
