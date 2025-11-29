import hashlib
import hmac


def hmac_sha256(key: bytes, data: str) -> bytes:
    return hmac.new(key, data.encode("utf-8"), hashlib.sha256).digest()


def hmac_sha256_hex(key: bytes, data: str) -> str:
    return hmac.new(key, data.encode("utf-8"), hashlib.sha256).hexdigest()


def sha256_hex(data: str) -> str:
    return hashlib.sha256(data.encode("utf-8")).hexdigest()
