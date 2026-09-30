"""Check what's in the database."""
from storage.db import get_connection

with get_connection() as conn:
    rows = conn.execute("SELECT id, title, author, status FROM projects ORDER BY id").fetchall()

print(f"تعداد پروژه‌ها: {len(rows)}\n")
for r in rows:
    print(f"#{r['id']}  {r['title']}  —  {r['author']}  [{r['status']}]")