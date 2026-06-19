import sqlite3
from pathlib import Path

from app.infrastructure.settings import get_settings


def get_connection() -> sqlite3.Connection:
    settings = get_settings()
    db_path = Path(settings.database_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def initialize_sqlite_database() -> None:
    with get_connection() as connection:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS registrations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name TEXT NOT NULL,
                second_name TEXT,
                first_last_name TEXT NOT NULL,
                second_last_name TEXT,
                document_number TEXT NOT NULL UNIQUE,
                phone TEXT NOT NULL,
                group_id INTEGER NOT NULL,
                interested_courses TEXT NOT NULL DEFAULT '[]',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE INDEX IF NOT EXISTS idx_registrations_group_id ON registrations(group_id);
            CREATE INDEX IF NOT EXISTS idx_registrations_created_at ON registrations(created_at);
            CREATE INDEX IF NOT EXISTS idx_registrations_names ON registrations(first_name, first_last_name);
            """
        )
        columns = {row["name"] for row in connection.execute("PRAGMA table_info(registrations)").fetchall()}
        if "interested_courses" not in columns:
            connection.execute("ALTER TABLE registrations ADD COLUMN interested_courses TEXT NOT NULL DEFAULT '[]'")
