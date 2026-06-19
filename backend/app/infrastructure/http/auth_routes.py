from fastapi import APIRouter, Depends

from app.application.auth_service import AuthService
from app.domain.errors import DomainError
from app.infrastructure.http.dependencies import domain_error_response, login_rate_limit
from app.infrastructure.http.schemas import LoginInput

router = APIRouter()


@router.post("/login")
def login(payload: LoginInput, _: None = Depends(login_rate_limit)) -> dict:
    try:
        return AuthService().login(payload.username, payload.password)
    except DomainError as error:
        raise domain_error_response(error) from error
