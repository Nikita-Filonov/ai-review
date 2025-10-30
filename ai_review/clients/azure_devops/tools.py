from httpx import Response


def azure_devops_has_next_page(response: Response) -> bool:
    """
    Azure DevOps uses continuation tokens for pagination.
    Check if there's a continuation token in the response headers.
    """
    return "x-ms-continuationtoken" in response.headers

