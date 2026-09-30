"""Temporary script to seed test projects."""
from storage.db import init_db
from storage import repositories as repo

init_db()

projects = [
    (
        "The Great Gatsby",
        "F. Scott Fitzgerald",
        '["https://www.goodreads.com/book/show/4671.The_Great_Gatsby"]',
        "In my younger and more vulnerable years…",
    ),
    (
        "1984",
        "George Orwell",
        '["https://www.goodreads.com/book/show/5470.1984"]',
        "It was a bright cold day in April, and the clocks were striking thirteen.",
    ),
    (
        "Brave New World",
        "Aldous Huxley",
        '["https://www.goodreads.com/book/show/5129.Brave_New_World"]',
        "A squat grey building of only thirty-four stories.",
    ),
]

for title, author, urls, snippet in projects:
    pid = repo.create_project(title=title, author=author, urls=urls, snippet=snippet)
    print(f"✅ #{pid}: {title} — {author}")

print("\nDone.")