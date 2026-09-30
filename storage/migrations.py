"""Simple DB migrations — safe to run at each startup."""
from storage.db import get_connection


def _column_exists(conn, table: str, column: str) -> bool:
    rows = conn.execute(f"PRAGMA table_info({table})").fetchall()
    return any(r["name"] == column for r in rows)


def run_migrations() -> None:
    """Apply all pending migrations. Idempotent."""
    with get_connection() as conn:
        # Migration 001: add api_key column to providers
        if not _column_exists(conn, "providers", "api_key"):
            conn.execute("ALTER TABLE providers ADD COLUMN api_key TEXT DEFAULT ''")
            conn.commit()

        # Migration 002: add model column to projects
        if not _column_exists(conn, "projects", "model"):
            conn.execute("ALTER TABLE projects ADD COLUMN model TEXT DEFAULT ''")
            conn.commit()

        # Migration 003: add provider column to projects
        if not _column_exists(conn, "projects", "provider"):
            conn.execute("ALTER TABLE projects ADD COLUMN provider TEXT DEFAULT ''")
            conn.commit()