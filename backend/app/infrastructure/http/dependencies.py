from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.application.registration_service import RegistrationService
from app.domain.errors import DomainError
from app.infrastructure.persistence.repository_factory import get_registration_repository
from app.infrastructure.security.jwt_service import verify_access_token


bearer = HTTPBearer()


def get_registration_service() -> RegistrationService:
    return RegistrationService(get_registration_repository())


def require_admin(credentials: HTTPAuthorizationCredentials = Depends(bearer)) -> dict:
    return verify_access_token(credentials.credentials)


def domain_error_response(error: DomainError) -> HTTPException:
    return HTTPException(status_code=error.status_code, detail=error.message)


LOGIN_ATTEMPTS: dict[str, list[float]] = {}
PUBLIC_REGISTRATION_ATTEMPTS: dict[str, list[float]] = {}


def _client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for", "")
    if forwarded:
        return forwarded.split(",", 1)[0].strip()
    return request.client.host if request.client else "unknown"


def login_rate_limit(request: Request) -> None:
    import time

    ip = _client_ip(request)
    now = time.time()
    attempts = [item for item in LOGIN_ATTEMPTS.get(ip, []) if now - item < 300]
    if len(attempts) >= 8:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Demasiados intentos. Intenta mas tarde.")
    attempts.append(now)
    LOGIN_ATTEMPTS[ip] = attempts


def public_registration_rate_limit(request: Request) -> None:
    """Limits automated floods while allowing normal community registration sessions."""
    import time

    ip = _client_ip(request)
    now = time.time()
    attempts = [item for item in PUBLIC_REGISTRATION_ATTEMPTS.get(ip, []) if now - item < 600]
    if len(attempts) >= 60:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Se alcanzaron demasiados envios desde esta conexion. Intenta de nuevo en unos minutos.",
        )
    attempts.append(now)
    PUBLIC_REGISTRATION_ATTEMPTS[ip] = attempts
