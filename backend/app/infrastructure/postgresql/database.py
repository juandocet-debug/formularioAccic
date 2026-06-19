from psycopg import connect
from psycopg.rows import dict_row

from app.infrastructure.settings import get_settings


def get_connection():
    settings = get_settings()
    if not settings.database_url:
        raise RuntimeError("DATABASE_URL no esta configurado.")
    return connect(settings.database_url, row_factory=dict_row)


def initialize_postgresql_database() -> None:
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS registrations (
                    id BIGSERIAL PRIMARY KEY,
                    first_name TEXT NOT NULL,
                    second_name TEXT,
                    first_last_name TEXT NOT NULL,
                    second_last_name TEXT,
                    document_number TEXT NOT NULL UNIQUE,
                    phone TEXT NOT NULL,
                    group_id INTEGER NOT NULL,
                    interested_courses TEXT NOT NULL DEFAULT '[]',
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                )
                """
            )
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_registrations_group_id ON registrations(group_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_registrations_created_at ON registrations(created_at)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_registrations_names ON registrations(first_name, first_last_name)")
            cursor.execute(
                """
                DO $$
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1
                        FROM information_schema.columns
                        WHERE table_name = 'registrations'
                        AND column_name = 'interested_courses'
                    ) THEN
                        ALTER TABLE registrations ADD COLUMN interested_courses TEXT NOT NULL DEFAULT '[]';
                    END IF;
                END $$;
                """
            )
