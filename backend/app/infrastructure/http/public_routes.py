from fastapi import APIRouter, Depends

from app.application.registration_service import RegistrationService
from app.domain.errors import DomainError
from app.infrastructure.http.dependencies import domain_error_response, get_registration_service
from app.infrastructure.http.schemas import RegistrationInput

router = APIRouter()


@router.get("/groups")
def list_groups(service: RegistrationService = Depends(get_registration_service)) -> list[dict]:
    return service.list_public_groups()


@router.post("/registrations", status_code=201)
def create_registration(
    payload: RegistrationInput,
    service: RegistrationService = Depends(get_registration_service),
) -> dict:
    try:
        return service.create_public_registration(payload.model_dump())
    except DomainError as error:
        raise domain_error_response(error) from error
