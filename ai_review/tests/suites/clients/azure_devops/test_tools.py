import base64

import pytest
from httpx import Response, Request

from ai_review import config
from ai_review.clients.azure_devops.tools import azure_devops_extract_continuation_token, build_azure_devops_headers
from ai_review.libs.config.vcs.azure_devops import AzureDevOpsTokenType


def make_response(
        json_data: dict | None = None,
        headers: dict | None = None,
        text_data: str | None = None,
) -> Response:
    """Helper to build httpx.Response with either JSON or raw text body."""
    request = Request("GET", "http://azure.test")

    if json_data is not None:
        return Response(status_code=200, json=json_data, request=request, headers=headers or {})

    content = text_data.encode() if text_data else b""
    return Response(status_code=200, content=content, request=request, headers=headers or {})


def test_extract_token_from_json_body():
    """Should extract continuation token from JSON body list."""
    response = make_response({"continuationToken": ["abc123"]})
    token = azure_devops_extract_continuation_token(response)
    assert token == "abc123"


def test_extract_token_from_json_body_empty_list():
    """Should return None if continuationToken list is empty."""
    response = make_response({"continuationToken": []})
    token = azure_devops_extract_continuation_token(response)
    assert token is None


def test_extract_token_from_headers_when_json_invalid():
    """Should fallback to headers when JSON parsing fails."""
    response = make_response(text_data="{invalid_json}", headers={"x-ms-continuationtoken": "xyz789"})
    token = azure_devops_extract_continuation_token(response)
    assert token == "xyz789"


def test_extract_token_from_headers_when_json_valid_but_no_token():
    """Should fallback to header when no token found in JSON body."""
    response = make_response({"some": "data"}, headers={"x-ms-continuationtoken": "token123"})
    token = azure_devops_extract_continuation_token(response)
    assert token == "token123"


def test_no_token_anywhere_returns_none():
    """Should return None when neither JSON nor headers contain a token."""
    response = make_response({"no": "token"})
    token = azure_devops_extract_continuation_token(response)
    assert token is None


def test_invalid_json_no_header_returns_none():
    """Should handle invalid JSON gracefully and return None if header missing."""
    response = make_response(text_data="not json", headers={})
    token = azure_devops_extract_continuation_token(response)
    assert token is None


@pytest.mark.usefixtures("azure_devops_http_client_config")
def test_build_headers_oauth2(monkeypatch: pytest.MonkeyPatch):
    """Should build Bearer Authorization header for OAUTH2 token type."""
    monkeypatch.setattr(
        config.settings.vcs.http_client,
        "api_token_type",
        AzureDevOpsTokenType.OAUTH2
    )

    headers = build_azure_devops_headers()
    assert headers == {"Authorization": "Bearer fake-token"}


@pytest.mark.usefixtures("azure_devops_http_client_config")
def test_build_headers_pat(monkeypatch: pytest.MonkeyPatch):
    """Should build Basic Authorization header for PAT token type."""
    monkeypatch.setattr(
        config.settings.vcs.http_client,
        "api_token_type",
        AzureDevOpsTokenType.PAT
    )

    headers = build_azure_devops_headers()
    expected_credentials = base64.b64encode(b":fake-token").decode("ascii")
    assert headers == {"Authorization": f"Basic {expected_credentials}"}


@pytest.mark.usefixtures("azure_devops_http_client_config")
def test_build_headers_unsupported_token_type_raises(monkeypatch: pytest.MonkeyPatch):
    """Should raise ValueError for unsupported credentials mode."""
    monkeypatch.setattr(config.settings.vcs.http_client, "api_token_type", "fake")

    with pytest.raises(ValueError, match="Unsupported Azure DevOps token type"):
        build_azure_devops_headers()
