import hashlib
import hmac

import pytest

from ai_review.libs.crypto.sha import hmac_sha256, hmac_sha256_hex, sha256_hex


# ---------- hmac_sha256 ----------

@pytest.mark.parametrize(
    "key,data",
    [
        (b"secret", "hello"),
        (b"key123", "test-data"),
        (b"", "empty-key"),
        (b"secret", ""),
    ],
)
def test_hmac_sha256_matches_python_hashlib(key, data):
    expected = hmac.new(key, data.encode("utf-8"), hashlib.sha256).digest()
    assert hmac_sha256(key, data) == expected


def test_hmac_sha256_returns_bytes():
    result = hmac_sha256(b"secret", "msg")
    assert isinstance(result, bytes)
    assert len(result) == 32  # SHA-256 digest length


# ---------- hmac_sha256_hex ----------

@pytest.mark.parametrize(
    "key,data",
    [
        (b"secret", "hello"),
        (b"key123", "test"),
        (b"", "123"),
        (b"abc", ""),
    ],
)
def test_hmac_sha256_hex_matches_python_hashlib(key, data):
    expected = hmac.new(key, data.encode("utf-8"), hashlib.sha256).hexdigest()
    assert hmac_sha256_hex(key, data) == expected


def test_hmac_sha256_hex_is_hex_string():
    result = hmac_sha256_hex(b"secret", "hello")
    assert isinstance(result, str)
    assert all(c in "0123456789abcdef" for c in result)
    assert len(result) == 64


# ---------- sha256_hex ----------

@pytest.mark.parametrize(
    "data,expected",
    [
        ("hello", hashlib.sha256(b"hello").hexdigest()),
        ("", hashlib.sha256(b"").hexdigest()),
        ("123456", hashlib.sha256(b"123456").hexdigest()),
        ("Привет", hashlib.sha256("Привет".encode()).hexdigest()),
    ],
)
def test_sha256_hex_matches_hashlib(data, expected):
    assert sha256_hex(data) == expected


def test_sha256_hex_returns_correct_length():
    assert len(sha256_hex("test")) == 64


def test_sha256_hex_is_pure_and_deterministic():
    assert sha256_hex("abc") == sha256_hex("abc")
    assert sha256_hex("abc") != sha256_hex("abcd")
