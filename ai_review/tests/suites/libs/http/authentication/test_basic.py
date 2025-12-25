import base64

from ai_review.libs.http.authentication.basic import build_basic_credentials


def test_build_basic_credentials_encodes_token_with_empty_username():
    token = "my-secret-token"

    result = build_basic_credentials(token)

    expected = base64.b64encode(f":{token}".encode("utf-8")).decode("ascii")
    assert result == expected


def test_build_basic_credentials_result_is_ascii_string():
    token = "token-123"

    result = build_basic_credentials(token)

    # Basic auth header value must be ASCII
    result.encode("ascii")  # should not raise


def test_build_basic_credentials_with_empty_token():
    token = ""

    result = build_basic_credentials(token)

    expected = base64.b64encode(b":").decode("ascii")
    assert result == expected
