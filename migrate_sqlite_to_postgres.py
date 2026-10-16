import os
import sqlite3

from dotenv import load_dotenv

from database import DB_PATH, get_connection, initialize_database


TABLE_COLUMNS = {
    "conversations": ("id", "title", "created_at"),
    "messages": (
        "id",
        "conversation_id",
        "role",
        "content",
        "created_at",
    ),
    "memories": ("id", "fact", "category", "created_at"),
    "app_preferences": ("key", "value"),
}


def migrate():
    load_dotenv()
    database_url = os.getenv("DATABASE_URL", "").strip()
    if not database_url.startswith(("postgres://", "postgresql://")):
        raise RuntimeError(
            "Set DATABASE_URL to your hosted PostgreSQL connection URL."
        )

    if not DB_PATH.exists():
        raise FileNotFoundError(f"Local database not found: {DB_PATH}")

    initialize_database()

    source = sqlite3.connect(DB_PATH)
    try:
        source.execute("""
            CREATE TABLE IF NOT EXISTS app_preferences (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
        """)
        source.row_factory = sqlite3.Row
        rows_by_table = {
            table: source.execute(
                f"SELECT {', '.join(columns)} FROM {table} "
                f"ORDER BY {columns[0]}"
            ).fetchall()
            for table, columns in TABLE_COLUMNS.items()
        }
    finally:
        source.close()

    with get_connection() as destination:
        for table in TABLE_COLUMNS:
            count = destination.execute(
                f"SELECT COUNT(*) AS row_count FROM {table}"
            ).fetchone()["row_count"]
            if count:
                raise RuntimeError(
                    f"Remote table '{table}' is not empty; migration "
                    "stopped to avoid overwriting existing data."
                )

        with destination.transaction():
            for table, columns in TABLE_COLUMNS.items():
                column_list = ", ".join(columns)
                placeholders = ", ".join("%s" for _ in columns)
                query = (
                    f"INSERT INTO {table} ({column_list}) "
                    f"VALUES ({placeholders})"
                )
                for row in rows_by_table[table]:
                    destination.execute(query, tuple(row))

            for table in TABLE_COLUMNS:
                if "id" in TABLE_COLUMNS[table]:
                    destination.execute(
                        f"""
                        SELECT setval(
                            pg_get_serial_sequence('{table}', 'id'),
                            COALESCE(MAX(id), 1),
                            COUNT(*) > 0
                        )
                        FROM {table}
                        """
                    )

    for table, rows in rows_by_table.items():
        print(f"Migrated {len(rows)} {table} row(s).")


if __name__ == "__main__":
    migrate()
