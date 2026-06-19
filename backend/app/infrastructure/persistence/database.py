from app.infrastructure.postgresql.database import initialize_postgresql_database
from app.infrastructure.settings import get_settings
from app.infrastructure.sqlite.database import initialize_sqlite_database


def initialize_database() -> None:
    settings = get_settings()
    if settings.database_url:
        initialize_postgresql_database()
        return
    initialize_sqlite_database()
