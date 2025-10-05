from httpx import Response


def gitlab_has_next_page(response: Response) -> bool:
    return bool(response.headers.get("X-Next-Page"))
