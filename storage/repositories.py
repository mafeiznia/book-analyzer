"""CRUD operations for projects."""
import json
from datetime import datetime

from storage.db import get_connection


def create_project(
    title: str,
    author: str,
    urls: str = "",
    snippet: str = "",
    model: str = "",
    provider: str = "",
) -> int:
    """Create a new project, return its id."""
    now = datetime.now().isoformat(timespec="seconds")
    with get_connection() as conn:
        cur = conn.execute(
            """INSERT INTO projects
               (title, author, urls, snippet, status, model, provider, created_at, updated_at)
               VALUES (?, ?, ?, ?, 'draft', ?, ?, ?, ?)""",
            (title, author, urls, snippet, model, provider, now, now),
        )
        conn.commit()
        return cur.lastrowid


def list_projects(search: str = "") -> list[dict]:
    """Return all projects, newest first. Optional search on title/author."""
    with get_connection() as conn:
        if search.strip():
            like = f"%{search.strip()}%"
            rows = conn.execute(
                """SELECT * FROM projects
                   WHERE title LIKE ? OR author LIKE ?
                   ORDER BY updated_at DESC""",
                (like, like),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM projects ORDER BY updated_at DESC"
            ).fetchall()
    return [dict(r) for r in rows]


def get_project(project_id: int) -> dict | None:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM projects WHERE id=?", (project_id,)
        ).fetchone()
    return dict(row) if row else None


def update_project(project_id: int, **fields) -> None:
    """Update given fields + refresh updated_at."""
    if not fields:
        return
    fields["updated_at"] = datetime.now().isoformat(timespec="seconds")
    cols = ", ".join(f"{k}=?" for k in fields)
    values = list(fields.values()) + [project_id]
    with get_connection() as conn:
        conn.execute(f"UPDATE projects SET {cols} WHERE id=?", values)
        conn.commit()


def set_status(project_id: int, status: str) -> None:
    update_project(project_id, status=status)


def delete_project(project_id: int) -> None:
    """Delete project (analyses cascaded via FK)."""
    with get_connection() as conn:
        conn.execute("DELETE FROM projects WHERE id=?", (project_id,))
        conn.commit()


def count_projects() -> int:
    with get_connection() as conn:
        return conn.execute("SELECT COUNT(*) FROM projects").fetchone()[0]
        
        import json
        
def serialize_urls(urls: list[str]) -> str:
    """Convert list of URLs to JSON string for storage."""
    cleaned = [u.strip() for u in urls if u.strip()]
    return json.dumps(cleaned, ensure_ascii=False)


def parse_urls(raw: str | None) -> list[str]:
    """Parse stored JSON string back to list of URLs."""
    if not raw:
        return []
    try:
        data = json.loads(raw)
        return data if isinstance(data, list) else []
    except Exception:
        return []        


def serialize_urls(urls: list[str]) -> str:
    """Convert list of URLs to JSON string for storage."""
    cleaned = [u.strip() for u in urls if u.strip()]
    return json.dumps(cleaned, ensure_ascii=False)


def parse_urls(raw: str | None) -> list[str]:
    """Parse stored JSON string back to list of URLs."""
    if not raw:
        return []
    try:
        data = json.loads(raw)
        return data if isinstance(data, list) else []
    except Exception:
        return []
        
def next_analysis_version(project_id: int) -> int:
    """Return the next version number for a project's analyses."""
    with get_connection() as conn:
        row = conn.execute(
            "SELECT MAX(version) AS v FROM analyses WHERE project_id=?",
            (project_id,),
        ).fetchone()
    return (row["v"] or 0) + 1


def save_analysis(
    project_id: int,
    provider: str,
    model: str,
    result_json: str,
    translation_prompt: str = "",
    sources_used: str = "",
    tokens_in: int = 0,
    tokens_out: int = 0,
    cost_usd: float = 0.0,
) -> int:
    """Save a new analysis version for a project. Returns analysis id."""
    version = next_analysis_version(project_id)
    with get_connection() as conn:
        cur = conn.execute(
            """INSERT INTO analyses
               (project_id, version, provider, model, result_json,
                translation_prompt, sources_used, tokens_in, tokens_out, cost_usd)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                project_id, version, provider, model, result_json,
                translation_prompt, sources_used, tokens_in, tokens_out, cost_usd,
            ),
        )
        conn.commit()
        return cur.lastrowid


def get_latest_analysis(project_id: int) -> dict | None:
    """Return the most recent analysis for a project."""
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM analyses WHERE project_id=? ORDER BY version DESC LIMIT 1",
            (project_id,),
        ).fetchone()
    return dict(row) if row else None


def list_analyses(project_id: int) -> list[dict]:
    """Return all analyses for a project, newest first."""
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM analyses WHERE project_id=? ORDER BY version DESC",
            (project_id,),
        ).fetchall()
    return [dict(r) for r in rows]        