"""Check all Markdown files for unbalanced code fences.

A code fence is ``` (three backticks).
Each opening fence must have a matching closing fence.
If the total count is odd, a fence is left unclosed.
"""
from pathlib import Path


def check_file(path: Path) -> dict:
    """Return stats about code fences in a file."""
    try:
        content = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        content = path.read_text(encoding="utf-8", errors="replace")

    lines = content.splitlines()
    fence_count = 0
    fence_positions = []

    for i, line in enumerate(lines, 1):
        stripped = line.lstrip()
        if stripped.startswith("```"):
            fence_count += 1
            fence_positions.append(i)

    return {
        "path": path,
        "count": fence_count,
        "balanced": fence_count % 2 == 0,
        "positions": fence_positions,
    }


def main():
    root = Path(__file__).parent

    files = []
    if (root / "README.md").exists():
        files.append(root / "README.md")
    files.extend(sorted((root / "docs").glob("*.md")))

    print("=" * 70)
    print(f"Checking {len(files)} Markdown files...")
    print("=" * 70)

    problems = []
    for f in files:
        stats = check_file(f)
        status = "OK" if stats["balanced"] else "PROBLEM"
        marker = "   " if stats["balanced"] else " ! "

        rel = f.relative_to(root)
        print(f"{marker} {str(rel):<55} fences: {stats['count']:>3}  [{status}]")

        if not stats["balanced"]:
            problems.append(stats)

    print("=" * 70)
    if problems:
        print(f"\nFound {len(problems)} file(s) with problems:\n")
        for p in problems:
            rel = p["path"].relative_to(root)
            print(f"  File: {rel}")
            print(f"  Unbalanced: {p['count']} fences (should be even)")
            print(f"  Fence line numbers: {p['positions']}")
            print()
    else:
        print("\nAll files OK!")
    print("=" * 70)


if __name__ == "__main__":
    main()