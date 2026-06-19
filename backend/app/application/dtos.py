import json
from typing import Any

from app.domain.groups import GROUP_CAPACITY, get_group


def registration_to_response(row: dict[str, Any]) -> dict[str, Any]:
    group = get_group(int(row["group_id"]))
    return {
        "id": row["id"],
        "first_name": row["first_name"],
        "second_name": row["second_name"],
        "first_last_name": row["first_last_name"],
        "second_last_name": row["second_last_name"],
        "document_number": row["document_number"],
        "phone": row["phone"],
        "group_id": row["group_id"],
        "interested_courses": _parse_courses(row.get("interested_courses")),
        "group_name": group.name if group else "",
        "place": group.place if group else "",
        "days": group.days if group else "",
        "schedule": group.schedule if group else "",
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }


def _parse_courses(value: str | list[str] | None) -> list[str]:
    if not value:
        return []
    if isinstance(value, list):
        return value
    try:
        parsed = json.loads(value)
        return parsed if isinstance(parsed, list) else []
    except json.JSONDecodeError:
        return []


def capacity_to_response(item: dict[str, Any]) -> dict[str, Any]:
    available = GROUP_CAPACITY - int(item["registered_count"])
    return {
        **item,
        "capacity": GROUP_CAPACITY,
        "available": max(available, 0),
        "is_full": available <= 0,
    }
