from __future__ import annotations

import json
from typing import Any

from app.domain.groups import GROUP_CAPACITY, TRAINING_GROUPS
from app.domain.repositories import RegistrationRepository
from app.infrastructure.sqlite.database import get_connection


class SqliteRegistrationRepository(RegistrationRepository):
    def create(self, payload: dict[str, Any]) -> dict[str, Any]:
        with get_connection() as connection:
            cursor = connection.execute(
                """
                INSERT INTO registrations (
                    first_name, second_name, first_last_name, second_last_name,
                    document_number, phone, group_id, interested_courses
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    payload["first_name"],
                    payload.get("second_name"),
                    payload["first_last_name"],
                    payload.get("second_last_name"),
                    payload["document_number"],
                    payload["phone"],
                    payload["group_id"],
                    json.dumps(payload.get("interested_courses", []), ensure_ascii=True),
                ),
            )
            registration_id = int(cursor.lastrowid)
            connection.commit()
            return self.find_by_id(registration_id) or {}

    def update(self, registration_id: int, payload: dict[str, Any]) -> dict[str, Any]:
        with get_connection() as connection:
            connection.execute(
                """
                UPDATE registrations
                SET first_name = ?, second_name = ?, first_last_name = ?, second_last_name = ?,
                    document_number = ?, phone = ?, group_id = ?, interested_courses = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (
                    payload["first_name"],
                    payload.get("second_name"),
                    payload["first_last_name"],
                    payload.get("second_last_name"),
                    payload["document_number"],
                    payload["phone"],
                    payload["group_id"],
                    json.dumps(payload.get("interested_courses", []), ensure_ascii=True),
                    registration_id,
                ),
            )
        return self.find_by_id(registration_id) or {}

    def delete(self, registration_id: int) -> None:
        with get_connection() as connection:
            connection.execute("DELETE FROM registrations WHERE id = ?", (registration_id,))

    def find_by_id(self, registration_id: int) -> dict[str, Any] | None:
        with get_connection() as connection:
            row = connection.execute("SELECT * FROM registrations WHERE id = ?", (registration_id,)).fetchone()
            return dict(row) if row else None

    def find_by_document(self, document_number: str, exclude_id: int | None = None) -> dict[str, Any] | None:
        query = "SELECT * FROM registrations WHERE document_number = ?"
        params: list[Any] = [document_number]
        if exclude_id is not None:
            query += " AND id != ?"
            params.append(exclude_id)

        with get_connection() as connection:
            row = connection.execute(query, params).fetchone()
            return dict(row) if row else None

    def count_by_group(self, group_id: int, exclude_id: int | None = None) -> int:
        query = "SELECT COUNT(*) AS total FROM registrations WHERE group_id = ?"
        params: list[Any] = [group_id]
        if exclude_id is not None:
            query += " AND id != ?"
            params.append(exclude_id)

        with get_connection() as connection:
            row = connection.execute(query, params).fetchone()
            return int(row["total"])

    def list(self, filters: dict[str, Any], limit: int, offset: int) -> tuple[list[dict[str, Any]], int]:
        where, params = self._build_filters(filters)
        safe_limit = min(max(limit, 1), 200)
        safe_offset = max(offset, 0)

        with get_connection() as connection:
            total_row = connection.execute(f"SELECT COUNT(*) AS total FROM registrations {where}", params).fetchone()
            rows = connection.execute(
                f"""
                SELECT id, first_name, second_name, first_last_name, second_last_name,
                       document_number, phone, group_id, interested_courses, created_at, updated_at
                FROM registrations
                {where}
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?
                """,
                [*params, safe_limit, safe_offset],
            ).fetchall()
        return [dict(row) for row in rows], int(total_row["total"])

    def capacity_summary(self) -> list[dict[str, Any]]:
        with get_connection() as connection:
            counts = {
                int(row["group_id"]): int(row["registered_count"])
                for row in connection.execute(
                    "SELECT group_id, COUNT(*) AS registered_count FROM registrations GROUP BY group_id"
                ).fetchall()
            }

        return [
            {
                "group_id": group.id,
                "group_name": group.name,
                "place": group.place,
                "days": group.days,
                "schedule": group.schedule,
                "registered_count": counts.get(group.id, 0),
            }
            for group in TRAINING_GROUPS
        ]

    def _build_filters(self, filters: dict[str, Any]) -> tuple[str, list[Any]]:
        clauses: list[str] = []
        params: list[Any] = []

        if filters.get("group_id"):
            clauses.append("group_id = ?")
            params.append(filters["group_id"])
        if filters.get("place"):
            matching_ids = [group.id for group in TRAINING_GROUPS if filters["place"].lower() in group.place.lower()]
            if not matching_ids:
                clauses.append("1 = 0")
            else:
                clauses.append(f"group_id IN ({','.join(['?'] * len(matching_ids))})")
                params.extend(matching_ids)
        if filters.get("capacity_status"):
            ids_by_status = self._group_ids_by_capacity_status(filters["capacity_status"])
            if ids_by_status is not None:
                if not ids_by_status:
                    clauses.append("1 = 0")
                else:
                    clauses.append(f"group_id IN ({','.join(['?'] * len(ids_by_status))})")
                    params.extend(ids_by_status)
        if filters.get("document"):
            clauses.append("document_number LIKE ?")
            params.append(f"%{filters['document']}%")
        if filters.get("name"):
            clauses.append("(first_name || ' ' || IFNULL(second_name, '') || ' ' || first_last_name || ' ' || IFNULL(second_last_name, '')) LIKE ?")
            params.append(f"%{filters['name']}%")
        if filters.get("date"):
            clauses.append("DATE(created_at) = DATE(?)")
            params.append(filters["date"])

        where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        return where, params

    def _group_ids_by_capacity_status(self, status: str) -> list[int] | None:
        normalized = status.lower().strip()
        if normalized not in {"full", "available"}:
            return None

        with get_connection() as connection:
            counts = {
                int(row["group_id"]): int(row["registered_count"])
                for row in connection.execute(
                    "SELECT group_id, COUNT(*) AS registered_count FROM registrations GROUP BY group_id"
                ).fetchall()
            }

        if normalized == "full":
            return [group.id for group in TRAINING_GROUPS if counts.get(group.id, 0) >= GROUP_CAPACITY]
        return [group.id for group in TRAINING_GROUPS if counts.get(group.id, 0) < GROUP_CAPACITY]
