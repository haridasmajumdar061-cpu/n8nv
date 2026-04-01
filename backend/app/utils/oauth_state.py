import base64
import hashlib
import hmac
import json
import secrets
import time


def _b64url_encode(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).decode("utf-8").rstrip("=")


def _b64url_decode(raw: str) -> bytes:
    padding = "=" * (-len(raw) % 4)
    return base64.urlsafe_b64decode(raw + padding)


def encode_oauth_state(provider: str, user_id: int, secret_key: str, ttl_seconds: int = 600) -> str:
    now = int(time.time())
    payload = {
        "p": provider,
        "u": user_id,
        "iat": now,
        "exp": now + ttl_seconds,
        "n": secrets.token_urlsafe(8),
    }
    body = _b64url_encode(json.dumps(payload, separators=(",", ":")).encode("utf-8"))
    signature = hmac.new(secret_key.encode("utf-8"), body.encode("utf-8"), hashlib.sha256).digest()
    return f"{body}.{_b64url_encode(signature)}"


def decode_oauth_state(state: str, secret_key: str) -> tuple[str, int]:
    try:
        body, sent_signature = state.split(".", 1)
    except ValueError as exc:
        raise ValueError("Malformed OAuth state") from exc

    expected_signature = hmac.new(
        secret_key.encode("utf-8"),
        body.encode("utf-8"),
        hashlib.sha256,
    ).digest()
    expected_signature_b64 = _b64url_encode(expected_signature)
    if not hmac.compare_digest(sent_signature, expected_signature_b64):
        raise ValueError("Invalid OAuth state signature")

    payload_raw = _b64url_decode(body)
    payload = json.loads(payload_raw.decode("utf-8"))
    if int(time.time()) > int(payload["exp"]):
        raise ValueError("Expired OAuth state")

    provider = str(payload["p"])
    user_id = int(payload["u"])
    return provider, user_id
