import pytest
from httpx import AsyncClient
from pydantic import HttpUrl, SecretStr, ValidationError

from ai_review.clients.azure_devops.client import get_azure_devops_http_client, AzureDevOpsHTTPClient
from ai_review.clients.azure_devops.pr.client import AzureDevOpsPullRequestsHTTPClient
from ai_review.config import settings
from ai_review.libs.config.vcs.azure_devops import (
    AzureDevOpsHTTPClientConfig,
    AzureDevOpsPipelineConfig,
    AzureDevOpsTokenType
)
from ai_review.libs.config.vcs.base import AzureDevOpsVCSConfig
from ai_review.libs.constants.vcs_provider import VCSProvider


@pytest.mark.usefixtures("azure_devops_http_client_config")
def test_get_azure_devops_http_client_builds_ok():
    azure_devops_http_client = get_azure_devops_http_client()

    assert isinstance(azure_devops_http_client, AzureDevOpsHTTPClient)
    assert isinstance(azure_devops_http_client.pr, AzureDevOpsPullRequestsHTTPClient)
    assert isinstance(azure_devops_http_client.pr.client, AsyncClient)


def test_config_default_token_type_is_oauth2():
    """Should default to OAUTH2 when api_token_type is not specified."""
    config = AzureDevOpsHTTPClientConfig(
        api_url=HttpUrl("https://dev.azure.com/org"),
        api_token=SecretStr("test-token")
    )
    
    assert config.token_type == AzureDevOpsTokenType.OAUTH2


def test_config_accepts_valid_token_types():
    """Should accept both 'oauth2' and 'pat' as valid token types."""
    # Test oauth2
    config_oauth = AzureDevOpsHTTPClientConfig(
        api_url=HttpUrl("https://dev.azure.com/org"),
        api_token=SecretStr("test-token"),
        api_token_type=AzureDevOpsTokenType.OAUTH2
    )
    assert config_oauth.token_type == AzureDevOpsTokenType.OAUTH2
    
    # Test pat
    config_pat = AzureDevOpsHTTPClientConfig(
        api_url=HttpUrl("https://dev.azure.com/org"),
        api_token=SecretStr("test-token"),
        api_token_type=AzureDevOpsTokenType.PAT
    )
    assert config_pat.token_type == AzureDevOpsTokenType.PAT


def test_config_rejects_invalid_token_type():
    """Should raise ValidationError for invalid api_token_type values."""
    invalid_values = ["bearer", "basic", "foo"]
    
    for invalid_value in invalid_values:
        with pytest.raises(ValidationError) as exc_info:
            AzureDevOpsHTTPClientConfig(
                api_url=HttpUrl("https://dev.azure.com/org"),
                api_token=SecretStr("test-token"),
                api_token_type=invalid_value
            )
        
        # Verify error message contains useful information
        error_message = str(exc_info.value)
        assert "token_type" in error_message.lower()


def test_client_builds_with_oauth2_token_type(monkeypatch: pytest.MonkeyPatch):
    """Should successfully build HTTP client with oauth2 token type."""
    fake_config = AzureDevOpsVCSConfig(
        provider=VCSProvider.AZURE_DEVOPS,
        pipeline=AzureDevOpsPipelineConfig(
            organization="org",
            project="proj",
            repository_id="repo123",
            pull_request_id=5,
            iteration_id=7,
        ),
        http_client=AzureDevOpsHTTPClientConfig(
            timeout=10,
            api_url=HttpUrl("https://dev.azure.com/org"),
            api_token=SecretStr("fake-oauth-token"),
            api_token_type=AzureDevOpsTokenType.OAUTH2
        )
    )
    monkeypatch.setattr(settings, "vcs", fake_config)
    
    client = get_azure_devops_http_client()
    
    assert isinstance(client, AzureDevOpsHTTPClient)
    assert isinstance(client.pr.client, AsyncClient)
    
    # Verify authorization header format
    auth_header = client.pr.client.headers.get("Authorization")
    assert auth_header is not None
    assert auth_header.startswith("Bearer ")


def test_client_builds_with_pat_token_type(monkeypatch: pytest.MonkeyPatch):
    """Should successfully build HTTP client with pat token type."""
    fake_config = AzureDevOpsVCSConfig(
        provider=VCSProvider.AZURE_DEVOPS,
        pipeline=AzureDevOpsPipelineConfig(
            organization="org",
            project="proj",
            repository_id="repo123",
            pull_request_id=5,
            iteration_id=7,
        ),
        http_client=AzureDevOpsHTTPClientConfig(
            timeout=10,
            api_url=HttpUrl("https://dev.azure.com/org"),
            api_token=SecretStr("fake-pat-token"),
            api_token_type=AzureDevOpsTokenType.PAT
        )
    )
    monkeypatch.setattr(settings, "vcs", fake_config)
    
    client = get_azure_devops_http_client()
    
    assert isinstance(client, AzureDevOpsHTTPClient)
    assert isinstance(client.pr.client, AsyncClient)
    
    # Verify authorization header format
    auth_header = client.pr.client.headers.get("Authorization")
    assert auth_header is not None
    assert auth_header.startswith("Basic ")
