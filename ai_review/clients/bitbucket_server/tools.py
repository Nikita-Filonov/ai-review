from httpx import Response


def bitbucket_server_has_next_page(response: Response) -> bool:
    data = response.json()
    return not data.get("isLastPage", True)
