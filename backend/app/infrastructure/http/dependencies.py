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


def login_rate_limit(request: Request) -> None:
    import time

    ip = request.client.host if request.client else "unknown"
    now = time.time()
    attempts = [item for item in LOGIN_ATTEMPTS.get(ip, []) if now - item < 300]
    if len(attempts) >= 8:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Demasiados intentos. Intenta mas tarde.")
    attempts.append(now)
    LOGIN_ATTEMPTS[ip] = attempts
