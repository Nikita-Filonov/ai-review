from httpx import Response, Request

from ai_review.clients.bitbucket_cloud.tools import bitbucket_cloud_has_next_page


def make_response(data: dict) -> Response:
    return Response(
        json=data,
        request=Request("GET", "http://bitbucket.test"),
        status_code=200,
    )


def test_bitbucket_cloud_has_next_page_true():
    resp = make_response({"next": "https://api.bitbucket.org/2.0/repositories/test/repo?page=2"})
    assert bitbucket_cloud_has_next_page(resp) is True


def test_bitbucket_cloud_has_next_page_false_none():
    resp = make_response({"next": None})
    assert bitbucket_cloud_has_next_page(resp) is False


def test_bitbucket_cloud_has_next_page_false_missing():
    resp = make_response({})
    assert bitbucket_cloud_has_next_page(resp) is False


def test_bitbucket_cloud_has_next_page_false_empty_string():
    resp = make_response({"next": ""})
    assert bitbucket_cloud_has_next_page(resp) is False
