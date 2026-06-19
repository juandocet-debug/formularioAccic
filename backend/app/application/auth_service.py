import hmac

from app.domain.errors import InvalidCredentialsError
from app.infrastructure.security.jwt_service import create_access_token
from app.infrastructure.settings import get_settings


class AuthService:
    def login(self, username: str, password: str) -> dict[str, str | int]:
        settings = get_settings()
        valid_username = hmac.compare_digest(username, settings.admin_username)
        valid_password = hmac.compare_digest(password, settings.admin_password)
        if not (valid_username and valid_password):
            raise InvalidCredentialsError()

        token = create_access_token({"sub": username, "role": "super_admin"})
        return {"access_token": token, "token_type": "bearer", "expires_minutes": settings.jwt_expires_minutes}
