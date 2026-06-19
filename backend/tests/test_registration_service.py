from __future__ import annotations

import pytest

from app.application.registration_service import RegistrationService
from app.domain.errors import DuplicateDocumentError, GroupFullError
from app.domain.groups import GROUP_CAPACITY
from app.domain.repositories import RegistrationRepository


class InMemoryRegistrationRepository(RegistrationRepository):
    def __init__(self) -> None:
        self.rows: list[dict] = []
        self.next_id = 1

    def create(self, payload: dict) -> dict:
        row = {
            "id": self.next_id,
            **payload,
            "created_at": "2026-06-19 10:00:00",
            "updated_at": "2026-06-19 10:00:00",
        }
        self.next_id += 1
        self.rows.append(row)
        return row

    def update(self, registration_id: int, payload: dict) -> dict:
        raise NotImplementedError

    def delete(self, registration_id: int) -> None:
        raise NotImplementedError

    def find_by_id(self, registration_id: int) -> dict | None:
        return next((row for row in self.rows if row["id"] == registration_id), None)

    def find_by_document(self, document_number: str, exclude_id: int | None = None) -> dict | None:
        return next(
            (
                row
                for row in self.rows
                if row["document_number"] == document_number and (exclude_id is None or row["id"] != exclude_id)
            ),
            None,
        )

    def count_by_group(self, group_id: int, exclude_id: int | None = None) -> int:
        return len([row for row in self.rows if row["group_id"] == group_id and (exclude_id is None or row["id"] != exclude_id)])

    def list(self, filters: dict, limit: int, offset: int) -> tuple[list[dict], int]:
        return self.rows[offset : offset + limit], len(self.rows)

    def capacity_summary(self) -> list[dict]:
        return []


def valid_payload(document_number: str = "123456", group_id: int = 1) -> dict:
    return {
        "first_name": "Ana",
        "second_name": "",
        "first_last_name": "Perez",
        "second_last_name": "",
        "document_number": document_number,
        "phone": "3001234567",
        "group_id": group_id,
        "interested_courses": ["Curso de Gastronomía Ancestral", "Curso de Tejidos"],
    }


def test_creates_registration_when_document_is_unique_and_group_has_capacity() -> None:
    repository = InMemoryRegistrationRepository()
    service = RegistrationService(repository)

    response = service.create_public_registration(valid_payload())

    assert response["document_number"] == "123456"
    assert response["group_id"] == 1


def test_rejects_duplicate_document() -> None:
    repository = InMemoryRegistrationRepository()
    service = RegistrationService(repository)
    service.create_public_registration(valid_payload())

    with pytest.raises(DuplicateDocumentError):
        service.create_public_registration(valid_payload())


def test_rejects_group_without_capacity() -> None:
    repository = InMemoryRegistrationRepository()
    service = RegistrationService(repository)
    for index in range(GROUP_CAPACITY):
        service.create_public_registration(valid_payload(document_number=str(1000 + index)))

    with pytest.raises(GroupFullError):
        service.create_public_registration(valid_payload(document_number="999999"))
