"""Delete all projects. Use with care."""
from storage.db import init_db, get_connection

init_db()
with get_connection() as conn:
    count = conn.execute("SELECT COUNT(*) FROM projects").fetchone()[0]
    conn.execute("DELETE FROM projects")
    conn.commit()
print(f"🗑️ {count} پروژه حذف شد.")