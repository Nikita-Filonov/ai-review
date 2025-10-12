from httpx import Response, Request

from ai_review.clients.gitea.tools import gitea_has_next_page


def make_response(headers: dict) -> Response:
    return Response(
        request=Request("GET", "http://gitea.test"),
        headers=headers,
        status_code=200,
    )


def test_gitea_has_next_page_true():
    resp = make_response({"Link": '<https://gitea.test?page=2>; rel="next"'})
    assert gitea_has_next_page(resp) is True


def test_gitea_has_next_page_false_empty():
    resp = make_response({"Link": ""})
    assert gitea_has_next_page(resp) is False


def test_gitea_has_next_page_false_missing():
    resp = make_response({})
    assert gitea_has_next_page(resp) is False
