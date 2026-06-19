from fastapi import APIRouter, Depends, Query
from fastapi.responses import Response

from app.application.registration_service import RegistrationService
from app.domain.errors import DomainError
from app.infrastructure.http.dependencies import domain_error_response, get_registration_service, require_admin
from app.infrastructure.http.exporters import build_excel, build_pdf
from app.infrastructure.http.schemas import RegistrationInput

router = APIRouter(dependencies=[Depends(require_admin)])


def read_filters(
    group_id: int | None = Query(default=None),
    place: str | None = Query(default=None),
    date: str | None = Query(default=None),
    name: str | None = Query(default=None),
    document: str | None = Query(default=None),
    capacity_status: str | None = Query(default=None),
) -> dict:
    return {
        "group_id": group_id,
        "place": place,
        "date": date,
        "name": name,
        "document": document,
        "capacity_status": capacity_status,
    }


@router.get("/registrations")
def list_registrations(
    filters: dict = Depends(read_filters),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    service: RegistrationService = Depends(get_registration_service),
) -> dict:
    return service.list_registrations(filters, limit, offset)


@router.get("/capacity")
def capacity(service: RegistrationService = Depends(get_registration_service)) -> list[dict]:
    return service.capacity_summary()


@router.put("/registrations/{registration_id}")
def update_registration(
    registration_id: int,
    payload: RegistrationInput,
    service: RegistrationService = Depends(get_registration_service),
) -> dict:
    try:
        return service.update_registration(registration_id, payload.model_dump())
    except DomainError as error:
        raise domain_error_response(error) from error


@router.delete("/registrations/{registration_id}", status_code=204)
def delete_registration(registration_id: int, service: RegistrationService = Depends(get_registration_service)) -> None:
    try:
        service.delete_registration(registration_id)
    except DomainError as error:
        raise domain_error_response(error) from error


@router.get("/exports/excel")
def export_excel(
    filters: dict = Depends(read_filters),
    service: RegistrationService = Depends(get_registration_service),
) -> Response:
    content = build_excel(service.export_registrations(filters))
    return Response(
        content=content,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": 'attachment; filename="respuestas_formulario_asic.xlsx"'},
    )


@router.get("/exports/pdf")
def export_pdf(
    filters: dict = Depends(read_filters),
    service: RegistrationService = Depends(get_registration_service),
) -> Response:
    content = build_pdf(service.export_registrations(filters))
    return Response(
        content=content,
        media_type="application/pdf",
        headers={"Content-Disposition": 'attachment; filename="respuestas_formulario_asic.pdf"'},
    )
