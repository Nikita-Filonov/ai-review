from base64 import b64decode

from ai_review.clients.azure_devops.auth import build_authorization_header
from ai_review.libs.config.vcs.azure_devops import AzureDevOpsTokenType


def test_build_authorization_header_oauth2():
    """Should return Bearer token format for OAuth2."""
    token = "test-oauth2-token-12345"
    result = build_authorization_header(token, AzureDevOpsTokenType.OAUTH2)
    
    assert result == f"Bearer {token}"


def test_build_authorization_header_pat():
    """Should return Basic auth format with base64-encoded :token for PAT."""
    token = "test-pat-token-67890"
    result = build_authorization_header(token, AzureDevOpsTokenType.PAT)
    
    # Verify format
    assert result.startswith("Basic ")
    
    # Extract and decode the base64 portion
    encoded_part = result.replace("Basic ", "")
    decoded = b64decode(encoded_part).decode()
    
    # Verify it matches the expected format ":token"
    assert decoded == f":{token}"
