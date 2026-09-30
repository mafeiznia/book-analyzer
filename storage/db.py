"""SQLite connection + schema initialization."""
import sqlite3
from pathlib import Path

import sys


def _get_data_dir() -> Path:
    """Return the data directory.

    - In dev mode: <project_root>/data
    - In frozen (exe) mode: <exe_dir>/data
    """
    if getattr(sys, "frozen", False):
        base = Path(sys.executable).parent
    else:
        base = Path(__file__).parent.parent
    d = base / "data"
    d.mkdir(parents=True, exist_ok=True)
    return d


DB_PATH = _get_data_dir() / "projects.db"


SCHEMA = """
CREATE TABLE IF NOT EXISTS projects (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    title       TEXT NOT NULL,
    author      TEXT NOT NULL,
    urls        TEXT,
    snippet     TEXT,
    status      TEXT NOT NULL DEFAULT 'draft',
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS analyses (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id          INTEGER NOT NULL,
    version             INTEGER NOT NULL,
    provider            TEXT,
    model               TEXT,
    result_json         TEXT,
    translation_prompt  TEXT,
    sources_used        TEXT,
    tokens_in           INTEGER,
    tokens_out          INTEGER,
    cost_usd            REAL,
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS providers (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT UNIQUE NOT NULL,
    base_url    TEXT,
    env_key     TEXT,
    api_key     TEXT DEFAULT '',
    is_builtin  INTEGER DEFAULT 0,
    is_active   INTEGER DEFAULT 0,
    models      TEXT,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS logs (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id  INTEGER,
    level       TEXT,
    message     TEXT,
    technical   TEXT,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_analyses_project ON analyses(project_id);
CREATE INDEX IF NOT EXISTS idx_logs_project ON logs(project_id);
"""


def get_connection() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db() -> None:
    with get_connection() as conn:
        conn.executescript(SCHEMA)
        conn.commit()
    # Apply migrations after schema creation
    from storage.migrations import run_migrations
    run_migrations()