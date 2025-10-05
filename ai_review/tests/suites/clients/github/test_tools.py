from httpx import Response, Request

from ai_review.clients.github.tools import github_has_next_page


def make_response(headers: dict) -> Response:
    return Response(
        request=Request("GET", "http://test"),
        headers=headers,
        status_code=200,
    )


def test_github_has_next_page_true():
    response = make_response({
        "Link": '<https://api.github.com/resource?page=2>; rel="next", '
                '<https://api.github.com/resource?page=5>; rel="last"'
    })
    assert github_has_next_page(response) is True


def test_github_has_next_page_false_no_next():
    response = make_response({
        "Link": '<https://api.github.com/resource?page=5>; rel="last"'
    })
    assert github_has_next_page(response) is False


def test_github_has_next_page_false_no_header():
    resp = make_response({})
    assert github_has_next_page(resp) is False
