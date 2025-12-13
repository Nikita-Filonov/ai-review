from httpx import Response

from ai_review.config import settings
from ai_review.libs.config.vcs.azure_devops import AzureDevOpsTokenType
from ai_review.libs.http.authentication.basic import build_basic_credentials
from ai_review.libs.logger import get_logger

logger = get_logger("AZURE_DEVOPS_TOOLS")


def azure_devops_extract_continuation_token(response: Response) -> str | None:
    try:
        data = response.json()
        tokens = data.get("continuationToken", [])
        logger.debug("Continuation token extracted from JSON body")
        return tokens[0]
    except Exception as error:
        logger.warning(f"Failed to parse continuation token from JSON body: {error!r}")

    token = response.headers.get("x-ms-continuationtoken")
    if token:
        logger.debug("Continuation token extracted from response headers")
        return token

    logger.debug("No continuation token found in response")
    return None


def build_azure_devops_headers() -> dict[str, str]:
    token_type = settings.vcs.http_client.api_token_type
    token_value = settings.vcs.http_client.api_token_value

    match token_type:
        case AzureDevOpsTokenType.OAUTH2:
            return {"Authorization": f"Bearer {token_value}"}

        case AzureDevOpsTokenType.PAT:
            return {"Authorization": f"Basic {build_basic_credentials(token_value)}"}

    raise ValueError(f"Unsupported Azure DevOps token type: {token_type}")
