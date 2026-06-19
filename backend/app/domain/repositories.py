from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class RegistrationRepository(ABC):
    @abstractmethod
    def create(self, payload: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def update(self, registration_id: int, payload: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def delete(self, registration_id: int) -> None:
        raise NotImplementedError

    @abstractmethod
    def find_by_id(self, registration_id: int) -> dict[str, Any] | None:
        raise NotImplementedError

    @abstractmethod
    def find_by_document(self, document_number: str, exclude_id: int | None = None) -> dict[str, Any] | None:
        raise NotImplementedError

    @abstractmethod
    def count_by_group(self, group_id: int, exclude_id: int | None = None) -> int:
        raise NotImplementedError

    @abstractmethod
    def list(self, filters: dict[str, Any], limit: int, offset: int) -> tuple[list[dict[str, Any]], int]:
        raise NotImplementedError

    @abstractmethod
    def capacity_summary(self) -> list[dict[str, Any]]:
        raise NotImplementedError
