from app.domain.repositories import RegistrationRepository
from app.infrastructure.postgresql.registration_repository import PostgresqlRegistrationRepository
from app.infrastructure.settings import get_settings
from app.infrastructure.sqlite.registration_repository import SqliteRegistrationRepository


def get_registration_repository() -> RegistrationRepository:
    if get_settings().database_url:
        return PostgresqlRegistrationRepository()
    return SqliteRegistrationRepository()
