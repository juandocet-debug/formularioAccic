import base64
import hashlib
import hmac
import json
import time
from typing import Any

from fastapi import HTTPException, status

from app.infrastructure.settings import get_settings


def _base64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _base64url_decode(data: str) -> bytes:
    padding = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + padding)


def create_access_token(payload: dict[str, Any]) -> str:
    settings = get_settings()
    now = int(time.time())
    body = {**payload, "iat": now, "exp": now + settings.jwt_expires_minutes * 60}
    header = {"alg": "HS256", "typ": "JWT"}
    signing_input = ".".join(
        [
            _base64url_encode(json.dumps(header, separators=(",", ":")).encode()),
            _base64url_encode(json.dumps(body, separators=(",", ":")).encode()),
        ]
    )
    signature = hmac.new(settings.jwt_secret.encode(), signing_input.encode(), hashlib.sha256).digest()
    return f"{signing_input}.{_base64url_encode(signature)}"


def verify_access_token(token: str) -> dict[str, Any]:
    settings = get_settings()
    try:
        header_part, payload_part, signature_part = token.split(".")
        signing_input = f"{header_part}.{payload_part}"
        expected = hmac.new(settings.jwt_secret.encode(), signing_input.encode(), hashlib.sha256).digest()
        received = _base64url_decode(signature_part)
        if not hmac.compare_digest(expected, received):
            raise ValueError("Invalid signature")
        payload = json.loads(_base64url_decode(payload_part))
        if int(payload.get("exp", 0)) < int(time.time()):
            raise ValueError("Expired token")
        if payload.get("role") != "super_admin":
            raise ValueError("Invalid role")
        return payload
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token invalido o expirado") from exc
