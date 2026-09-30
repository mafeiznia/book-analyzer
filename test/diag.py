"""Diagnostic — show DB state, then add 2 test projects."""
from storage.db import init_db, get_connection
from storage import repositories as repo

init_db()

# --- Before ---
print("=== BEFORE ===")
with get_connection() as conn:
    rows = conn.execute("SELECT id, title, author FROM projects ORDER BY id").fetchall()
print(f"تعداد: {len(rows)}")
for r in rows:
    print(f"  #{r['id']}: {r['title']} — {r['author']}")

# --- Insert ---
print("\n=== INSERTING ===")
p1 = repo.create_project("1984", "George Orwell", '["https://example.com/1984"]', "test snippet 1")
print(f"  ✅ ساخته شد: #{p1} (1984)")
p2 = repo.create_project("Brave New World", "Aldous Huxley", '["https://example.com/bnw"]', "test snippet 2")
print(f"  ✅ ساخته شد: #{p2} (Brave New World)")

# --- After ---
print("\n=== AFTER ===")
with get_connection() as conn:
    rows = conn.execute("SELECT id, title, author FROM projects ORDER BY id").fetchall()
print(f"تعداد: {len(rows)}")
for r in rows:
    print(f"  #{r['id']}: {r['title']} — {r['author']}")