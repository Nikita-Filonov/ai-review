import pytest

from ai_review.libs.config.llm.openai import OpenAIMetaConfig


@pytest.mark.parametrize(
    "model, expected",
    [
        ("gpt-5", True),
        ("gpt-5-preview", True),
        ("gpt-4.1", True),
        ("gpt-4.1-mini", True),
        ("gpt-4o", False),
        ("gpt-4o-mini", False),
        ("gpt-3.5-turbo", False),
        ("text-davinci-003", False),
    ],
)
def test_is_v2_model_detection(model: str, expected: bool):
    meta = OpenAIMetaConfig(model=model)
    assert meta.is_v2_model is expected, f"Model {model} expected {expected} but got {meta.is_v2_model}"


def test_is_v2_model_default_false():
    meta = OpenAIMetaConfig()
    assert meta.model == "gpt-4o-mini"
    assert meta.is_v2_model is False
    assert meta.max_tokens is None
