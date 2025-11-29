import hashlib
import hmac
from datetime import datetime

import pytest

from ai_review.libs.aws.signv4 import (
    AwsCredentials,
    AwsDate,
    AwsURL,
    AwsHeaders,
    AwsRequest,
    AwsSigV4Config,
    build_aws_date,
    build_aws_url,
    build_aws_headers,
    build_aws_request,
    build_aws_string_to_sign,
    derive_aws_signing_key,
    sign_aws_string,
    build_aws_authorization,
    sign_aws_v4,
)
from ai_review.libs.crypto.sha import sha256_hex


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

@pytest.fixture
def fixed_date(monkeypatch: pytest.MonkeyPatch) -> AwsDate:
    """Patch datetime.utcnow() so build_aws_date is deterministic."""

    class FixedDatetime(datetime):
        @classmethod
        def utcnow(cls):
            return datetime(2025, 1, 1, 12, 0, 0)

    monkeypatch.setattr("ai_review.libs.aws.signv4.datetime", FixedDatetime)
    return AwsDate(amz="20250101T120000Z", date="20250101")


# ---------------------------------------------------------------------------
# Step 0 — Dates & URLs
# ---------------------------------------------------------------------------

def test_build_aws_date_fixed(fixed_date: AwsDate):
    date = build_aws_date()
    assert date == fixed_date


@pytest.mark.parametrize(
    "url,expected",
    [
        (
                "https://example.com/test/path?a=1",
                AwsURL(host="example.com", route="/test/path", query="a=1")
        ),
        ("https://api.test.com", AwsURL(host="api.test.com", route="/", query="")),
    ]
)
def test_build_aws_url_parsing(url: str, expected: AwsURL):
    assert build_aws_url(url) == expected


# ---------------------------------------------------------------------------
# Step 1 — Headers & canonical request
# ---------------------------------------------------------------------------

def test_build_aws_headers_without_token():
    url = AwsURL(host="example.com", route="/", query="")
    date = AwsDate(amz="20250101T120000Z", date="20250101")
    creds = AwsCredentials(access_key="AK", secret_key="SK")

    headers = build_aws_headers(url, date, creds)

    assert headers.signed == "host;x-amz-date"
    assert headers.canonical == "host:example.com\nx-amz-date:20250101T120000Z\n"


def test_build_aws_headers_with_token():
    url = AwsURL(host="example.com", route="/", query="")
    date = AwsDate(amz="TIME", date="DATE")
    creds = AwsCredentials(access_key="AK", secret_key="SK", session_token="TOKEN123")

    headers = build_aws_headers(url, date, creds)

    assert headers.signed == "host;x-amz-date;x-amz-security-token"
    assert headers.canonical == (
        "host:example.com\n"
        "x-amz-date:TIME\n"
        "x-amz-security-token:TOKEN123\n"
    )


def test_build_aws_request():
    headers = AwsHeaders(
        signed="host;x-amz-date",
        canonical="host:example\nx-amz-date:TIME\n"
    )

    req = build_aws_request(
        method="POST",
        url=AwsURL(host="example", route="/path", query="x=1"),
        headers=headers,
        body_hash="ABCDEF",
    )

    assert req.canonical == (
        "POST\n"
        "/path\n"
        "x=1\n"
        "host:example\nx-amz-date:TIME\n"
        "\n"
        "host;x-amz-date\n"
        "ABCDEF"
    )


# ---------------------------------------------------------------------------
# Step 2 — String to sign
# ---------------------------------------------------------------------------

def test_build_aws_string_to_sign(fixed_date: AwsDate):
    cfg = AwsSigV4Config(region="us-east-1", service="bedrock")
    request = AwsRequest(canonical="TEST-CANONICAL\nSTRING")

    sts = build_aws_string_to_sign(fixed_date, cfg, request)

    expected_hash = sha256_hex("TEST-CANONICAL\nSTRING")

    assert sts == (
        "AWS4-HMAC-SHA256\n"
        "20250101T120000Z\n"
        "20250101/us-east-1/bedrock/aws4_request\n"
        f"{expected_hash}"
    )


# ---------------------------------------------------------------------------
# Step 3 — Signing key & signature
# ---------------------------------------------------------------------------

def test_derive_aws_signing_key():
    date = AwsDate(amz="TIME", date="20250101")
    cfg = AwsSigV4Config(region="us-east-1", service="bedrock")
    creds = AwsCredentials(access_key="AK", secret_key="SECRETKEY")

    # Expected calculation:
    # key1 = HMAC("AWS4SECRETKEY", date)
    # key2 = HMAC(key1, region)
    # key3 = HMAC(key2, service)
    # key4 = HMAC(key3, "aws4_request")

    k1 = hmac.new(b"AWS4SECRETKEY", b"20250101", hashlib.sha256).digest()
    k2 = hmac.new(k1, b"us-east-1", hashlib.sha256).digest()
    k3 = hmac.new(k2, b"bedrock", hashlib.sha256).digest()
    expected = hmac.new(k3, b"aws4_request", hashlib.sha256).digest()

    assert derive_aws_signing_key(date, cfg, creds) == expected


def test_sign_aws_string():
    signing_key = b"abcdef" * 5
    string = "HELLO"

    expected = hmac.new(signing_key, string.encode(), hashlib.sha256).hexdigest()
    assert sign_aws_string(string, signing_key) == expected


# ---------------------------------------------------------------------------
# Step 4 — Authorization header
# ---------------------------------------------------------------------------

def test_build_aws_authorization():
    date = AwsDate(amz="AMZ", date="DATE")
    cfg = AwsSigV4Config(region="us-east-1", service="bedrock")
    headers = AwsHeaders(signed="host;x-amz-date", canonical="irrelevant")
    creds = AwsCredentials(access_key="AKID", secret_key="SK")

    auth = build_aws_authorization(
        date=date,
        config=cfg,
        headers=headers,
        signature="SIGN123",
        credentials=creds,
    )

    assert auth == (
        "AWS4-HMAC-SHA256 "
        "Credential=AKID/DATE/us-east-1/bedrock/aws4_request, "
        "SignedHeaders=host;x-amz-date, "
        "Signature=SIGN123"
    )


# ---------------------------------------------------------------------------
# Full API — sign_aws_v4
# ---------------------------------------------------------------------------

def test_sign_aws_v4_basic(monkeypatch: pytest.MonkeyPatch):
    """Validates final output has all headers with correct formatting."""

    # Fix date
    monkeypatch.setattr(
        "ai_review.libs.aws.signv4.build_aws_date",
        lambda: AwsDate(amz="20250101T120000Z", date="20250101"),
    )

    cfg = AwsSigV4Config(region="us-east-1", service="bedrock")
    creds = AwsCredentials(access_key="AKID", secret_key="SECRET")

    result = sign_aws_v4(
        url="https://bedrock-runtime.us-east-1.amazonaws.com/model/test-model/invoke",
        body='{"a":1}',
        method="POST",
        aws_config=cfg,
        aws_credentials=creds,
    )

    # Required fields
    assert "Authorization" in result
    assert "x-amz-date" in result
    assert "x-amz-content-sha256" in result

    # Date must match patched one
    assert result["x-amz-date"] == "20250101T120000Z"

    # Body SHA
    assert result["x-amz-content-sha256"] == sha256_hex('{"a":1}')

    # Authorization header should contain expected substrings
    auth = result["Authorization"]
    assert auth.startswith("AWS4-HMAC-SHA256 ")
    assert "Credential=AKID/20250101/us-east-1/bedrock/aws4_request" in auth
    assert "SignedHeaders=host;x-amz-date" in auth
    assert "Signature=" in auth


def test_sign_aws_v4_includes_session_token(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(
        "ai_review.libs.aws.signv4.build_aws_date",
        lambda: AwsDate(amz="AMZDATE", date="DATE"),
    )

    cfg = AwsSigV4Config(region="us-east-1")
    creds = AwsCredentials(
        access_key="AK",
        secret_key="SK",
        session_token="TOKEN123"
    )

    result = sign_aws_v4(
        url="https://example.com/abc",
        body="{}",
        method="POST",
        aws_config=cfg,
        aws_credentials=creds,
    )

    assert result["x-amz-security-token"] == "TOKEN123"
