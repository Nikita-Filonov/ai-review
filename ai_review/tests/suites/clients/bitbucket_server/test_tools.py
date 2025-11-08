import json

from httpx import Response, Request

from ai_review.clients.bitbucket_server.tools import bitbucket_server_has_next_page


def make_response(data: dict) -> Response:
    """Helper to create a fake HTTPX Response with given JSON data."""
    return Response(
        status_code=200,
        content=json.dumps(data).encode(),
        request=Request("GET", "http://bitbucket-server.test"),
    )


def test_bitbucket_server_has_next_page_true_when_not_last():
    """Should return True if isLastPage=False (i.e., more pages exist)."""
    resp = make_response({"isLastPage": False})
    assert bitbucket_server_has_next_page(resp) is True


def test_bitbucket_server_has_next_page_false_when_last_page():
    """Should return False if isLastPage=True (last page reached)."""
    resp = make_response({"isLastPage": True})
    assert bitbucket_server_has_next_page(resp) is False


def test_bitbucket_server_has_next_page_false_when_missing():
    """Should default to False if isLastPage key is missing (treated as last page)."""
    resp = make_response({})
    assert bitbucket_server_has_next_page(resp) is False


def test_bitbucket_server_has_next_page_false_when_invalid_type():
    """Should handle invalid non-bool values gracefully."""
    resp = make_response({"isLastPage": "not-a-bool"})
    assert bitbucket_server_has_next_page(resp) is False
