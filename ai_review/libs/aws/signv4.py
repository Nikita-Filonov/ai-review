import hashlib
import hmac
from dataclasses import dataclass
from datetime import datetime
from urllib.parse import urlparse

from ai_review.libs.crypto.sha import sha256_hex, hmac_sha256


# =============================================================================
# Dataclasses — value-objects
# =============================================================================

@dataclass(frozen=True)
class AwsCredentials:
    access_key: str
    secret_key: str
    session_token: str | None = None


@dataclass(frozen=True)
class AwsDate:
    amz: str
    date: str


@dataclass(frozen=True)
class AwsURL:
    host: str
    route: str
    query: str


@dataclass(frozen=True)
class AwsHeaders:
    signed: str
    canonical: str


@dataclass(frozen=True)
class AwsRequest:
    canonical: str


@dataclass(frozen=True)
class AwsSigV4Config:
    region: str
    service: str = "bedrock"


# =============================================================================
# Step 0 — Date and URL
# =============================================================================

def build_aws_date() -> AwsDate:
    """
    Returns AWS date formats:
      amz  = "20250101T120000Z"
      date = "20250101"
    """
    now = datetime.utcnow()
    return AwsDate(
        amz=now.strftime("%Y%m%dT%H%M%SZ"),
        date=now.strftime("%Y%m%d"),
    )


def build_aws_url(url: str) -> AwsURL:
    parsed = urlparse(url)
    return AwsURL(
        host=parsed.netloc,
        route=parsed.path or "/",
        query=parsed.query or ""
    )


# =============================================================================
# Step 1 — Canonical headers + canonical request
# =============================================================================

def build_aws_headers(url: AwsURL, date: AwsDate, credentials: AwsCredentials) -> AwsHeaders:
    signed = ["host", "x-amz-date"]
    canonical = [f"host:{url.host}", f"x-amz-date:{date.amz}"]

    if credentials.session_token:
        signed.append("x-amz-security-token")
        canonical.append(f"x-amz-security-token:{credentials.session_token}")

    return AwsHeaders(
        signed=";".join(signed),
        canonical="\n".join(canonical) + "\n"
    )


def build_aws_request(method: str, url: AwsURL, headers: AwsHeaders, body_hash: str) -> AwsRequest:
    canonical = "\n".join([
        method.upper(),
        url.route,
        url.query,
        headers.canonical,
        headers.signed,
        body_hash,
    ])
    return AwsRequest(canonical=canonical)


# =============================================================================
# Step 2 — String to sign
# =============================================================================

def build_aws_string_to_sign(date: AwsDate, config: AwsSigV4Config, request: AwsRequest) -> str:
    scope = f"{date.date}/{config.region}/{config.service}/aws4_request"
    hashed = sha256_hex(request.canonical)
    return "\n".join(["AWS4-HMAC-SHA256", date.amz, scope, hashed])


# =============================================================================
# Step 3 — Signing key and signature
# =============================================================================

def derive_aws_signing_key(date: AwsDate, config: AwsSigV4Config, credentials: AwsCredentials) -> bytes:
    key = hmac_sha256(f"AWS4{credentials.secret_key}".encode(), date.date)
    key = hmac_sha256(key, config.region)
    key = hmac_sha256(key, config.service)
    return hmac_sha256(key, "aws4_request")


def sign_aws_string(string_to_sign: str, signing_key: bytes) -> str:
    return hmac.new(signing_key, string_to_sign.encode(), hashlib.sha256).hexdigest()


# =============================================================================
# Step 4 — Authorization header
# =============================================================================

def build_aws_authorization(
        date: AwsDate,
        config: AwsSigV4Config,
        headers: AwsHeaders,
        signature: str,
        credentials: AwsCredentials,
) -> str:
    scope = f"{date.date}/{config.region}/{config.service}/aws4_request"
    return (
        "AWS4-HMAC-SHA256 "
        f"Credential={credentials.access_key}/{scope}, "
        f"SignedHeaders={headers.signed}, "
        f"Signature={signature}"
    )


# =============================================================================
# Public API
# =============================================================================

def sign_aws_v4(
        url: str,
        body: str,
        method: str,
        aws_config: AwsSigV4Config,
        aws_credentials: AwsCredentials,
) -> dict[str, str]:
    # Step 0
    aws_url = build_aws_url(url)
    aws_date = build_aws_date()

    # Step 1
    body_hash = sha256_hex(body)
    aws_headers = build_aws_headers(url=aws_url, date=aws_date, credentials=aws_credentials)
    aws_request = build_aws_request(url=aws_url, method=method, headers=aws_headers, body_hash=body_hash)

    # Step 2
    string_to_sign = build_aws_string_to_sign(date=aws_date, config=aws_config, request=aws_request)

    # Step 3
    signing_key = derive_aws_signing_key(date=aws_date, config=aws_config, credentials=aws_credentials)
    signature = sign_aws_string(string_to_sign, signing_key)

    # Step 4
    aws_authorization = build_aws_authorization(
        date=aws_date,
        config=aws_config,
        headers=aws_headers,
        signature=signature,
        credentials=aws_credentials
    )

    # Final headers
    result = {
        "Authorization": aws_authorization,
        "x-amz-date": aws_date.amz,
        "x-amz-content-sha256": body_hash,
    }

    if aws_credentials.session_token:
        result["x-amz-security-token"] = aws_credentials.session_token

    return result
