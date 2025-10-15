from httpx import Response


def gitea_has_next_page(response: Response) -> bool:
    link_header = response.headers.get("Link")
    return link_header is not None and 'rel="next"' in link_header
