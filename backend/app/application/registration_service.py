from typing import Any

from app.application.dtos import capacity_to_response, registration_to_response
from app.domain.errors import DuplicateDocumentError, GroupFullError, GroupNotFoundError, RegistrationNotFoundError
from app.domain.groups import GROUP_CAPACITY, get_group
from app.domain.repositories import RegistrationRepository


class RegistrationService:
    def __init__(self, repository: RegistrationRepository) -> None:
        self.repository = repository

    def list_public_groups(self) -> list[dict[str, Any]]:
        return [capacity_to_response(item) for item in self.repository.capacity_summary()]

    def create_public_registration(self, payload: dict[str, Any]) -> dict[str, Any]:
        self._assert_group_exists(payload["group_id"])
        self._assert_document_is_unique(payload["document_number"])
        self._assert_group_has_capacity(payload["group_id"])
        return registration_to_response(self.repository.create(payload))

    def list_registrations(self, filters: dict[str, Any], limit: int, offset: int) -> dict[str, Any]:
        rows, total = self.repository.list(filters, limit, offset)
        return {
            "items": [registration_to_response(row) for row in rows],
            "total": total,
            "limit": limit,
            "offset": offset,
        }

    def export_registrations(self, filters: dict[str, Any]) -> list[dict[str, Any]]:
        rows, _ = self.repository.list(filters, limit=5000, offset=0)
        return [registration_to_response(row) for row in rows]

    def update_registration(self, registration_id: int, payload: dict[str, Any]) -> dict[str, Any]:
        current = self.repository.find_by_id(registration_id)
        if current is None:
            raise RegistrationNotFoundError()

        self._assert_group_exists(payload["group_id"])
        self._assert_document_is_unique(payload["document_number"], exclude_id=registration_id)
        self._assert_group_has_capacity(payload["group_id"], exclude_id=registration_id)
        return registration_to_response(self.repository.update(registration_id, payload))

    def delete_registration(self, registration_id: int) -> None:
        if self.repository.find_by_id(registration_id) is None:
            raise RegistrationNotFoundError()
        self.repository.delete(registration_id)

    def capacity_summary(self) -> list[dict[str, Any]]:
        return [capacity_to_response(item) for item in self.repository.capacity_summary()]

    def _assert_document_is_unique(self, document_number: str, exclude_id: int | None = None) -> None:
        if self.repository.find_by_document(document_number, exclude_id=exclude_id):
            raise DuplicateDocumentError()

    def _assert_group_exists(self, group_id: int) -> None:
        if get_group(group_id) is None:
            raise GroupNotFoundError()

    def _assert_group_has_capacity(self, group_id: int, exclude_id: int | None = None) -> None:
        if self.repository.count_by_group(group_id, exclude_id=exclude_id) >= GROUP_CAPACITY:
            raise GroupFullError()
