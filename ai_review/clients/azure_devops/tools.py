from httpx import Response

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
