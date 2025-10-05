from httpx import Response


def bitbucket_has_next_page(response: Response) -> bool:
    data = response.json()
    return bool(data.get("next"))
