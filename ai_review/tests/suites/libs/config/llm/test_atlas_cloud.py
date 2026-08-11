from pydantic import SecretStr, TypeAdapter

from ai_review.libs.config.llm.atlas_cloud import (
    AtlasCloudHTTPClientConfig,
    AtlasCloudMetaConfig,
)
from ai_review.libs.config.llm.base import AtlasCloudLLMConfig, LLMConfig


def test_atlas_cloud_defaults():
    meta = AtlasCloudMetaConfig()
    http_client = AtlasCloudHTTPClientConfig(api_token=SecretStr("token"))

    assert meta.model == "qwen/qwen3.8-max"
    assert str(http_client.api_url) == "https://api.atlascloud.ai/v1"


def test_atlas_cloud_discriminated_config():
    config = TypeAdapter(LLMConfig).validate_python(
        {
            "provider": "ATLAS_CLOUD",
            "http_client": {"api_token": "token"},
        }
    )

    assert isinstance(config, AtlasCloudLLMConfig)
    assert config.meta.model == "qwen/qwen3.8-max"
    assert config.http_client.api_token_value == "token"
