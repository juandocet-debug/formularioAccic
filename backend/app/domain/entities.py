from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Registration:
    id: int
    first_name: str
    second_name: str | None
    first_last_name: str
    second_last_name: str | None
    document_number: str
    phone: str
    group_id: int
    created_at: datetime
    updated_at: datetime
