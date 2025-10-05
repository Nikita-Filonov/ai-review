from httpx import Response, Request

from ai_review.clients.gitlab.tools import gitlab_has_next_page


def make_response(headers: dict) -> Response:
    return Response(
        request=Request("GET", "http://gitlab.test"),
        headers=headers,
        status_code=200,
    )


def test_gitlab_has_next_page_true():
    resp = make_response({"X-Next-Page": "2"})
    assert gitlab_has_next_page(resp) is True


def test_gitlab_has_next_page_false_empty():
    resp = make_response({"X-Next-Page": ""})
    assert gitlab_has_next_page(resp) is False


def test_gitlab_has_next_page_false_missing():
    resp = make_response({})
    assert gitlab_has_next_page(resp) is False
