from base64 import b64encode

from ai_review.libs.config.vcs.azure_devops import AzureDevOpsTokenType


def build_authorization_header(token: str, token_type: AzureDevOpsTokenType) -> str:
    """
    Build an Authorization header value based on the token type.

    Args:
        token: The API token value (OAuth2 token or PAT)
        token_type: The authentication mode (OAUTH2 or PAT)

    Returns:
        Authorization header value in the format:
        - "Bearer {token}" for OAUTH2
        - "Basic {base64(:{token})}" for PAT

    Note:
        For PAT authentication, Azure DevOps requires the format ":{token}"
        to be base64-encoded (empty username with colon prefix).
    """
    if token_type == AzureDevOpsTokenType.OAUTH2:
        return f"Bearer {token}"
    elif token_type == AzureDevOpsTokenType.PAT:
        # Azure DevOps PAT format: base64 encode ":{token}" (empty username)
        credentials = f":{token}"
        encoded = b64encode(credentials.encode()).decode()
        return f"Basic {encoded}"
    else:
        raise ValueError(f"Unsupported token type: {token_type}")
