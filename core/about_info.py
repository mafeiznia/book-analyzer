"""Application metadata for the About dialog.

Edit this file to update app info, author details, or tech stack.
"""
from pathlib import Path
import sys

# ============================================================
# APPLICATION
# ============================================================
APP_NAME = "Book Analyzer"
APP_VERSION = "1.1.0"
APP_TAGLINE_FA = "تحلیل‌گر هوشمند کتاب برای مترجمان"
APP_TAGLINE_EN = "Smart Book Analyzer for Translators"


# ============================================================
# AUTHOR
# ============================================================
AUTHOR_NAME_FA = "محمود اهرپور فیض‌نیا"
AUTHOR_NAME_EN = "Mahmoud Aharpour Feiznia"
AUTHOR_EMAIL = "ma.feiznia@gmail.com"
AUTHOR_WEBSITE = "yadoto.ir"
AUTHOR_WEBSITE_URL = "https://yadoto.ir"
AUTHOR_LINKEDIN_URL = "linkedin.com/in/mahmoud-aharpour-feiznia-585782265"  # TODO: تأیید شود


# ============================================================
# LICENSE & COPYRIGHT
# ============================================================
LICENSE_NAME = "MIT License"
COPYRIGHT_YEAR = "2026"
COPYRIGHT_HOLDER = "Mahmoud Aharpour Feiznia"


# ============================================================
# REPOSITORY
# ============================================================
GITHUB_URL = ""  # TODO: پس از انتشار در گام ۱۲ پر شود


# ============================================================
# TECHNOLOGY STACK
# ============================================================
# هر ردیف: (عنوان فارسی، مقدار)
TECH_STACK: list[tuple[str, str]] = [
    ("رابط کاربری", "Flet 0.28.3 (Python) + Material 3"),
    ("زبان برنامه‌نویسی", "Python 3.12"),
    ("دیتابیس", "SQLite"),
    ("مدل زبانی", "چندگانه (OpenRouter, OpenAI, Gemini, DeepSeek, GLM, Custom)"),
    ("جست‌وجو", "DuckDuckGo (ddgs)"),
    ("Crawler", "httpx + BeautifulSoup + lxml"),
    ("تولید PDF", "WeasyPrint + Vazirmatn"),
    ("خروجی‌ها", "JSON / Markdown / PDF"),
    ("مجوز", "MIT License"),
]


# ============================================================
# ASSETS
# ============================================================
def _get_assets_dir() -> Path:
    """Return the assets directory.

    - In frozen mode: <_MEIPASS>/assets (read-only, bundled)
    - In dev mode: <project_root>/assets
    """
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS) / "assets"
    return Path(__file__).parent.parent / "assets"


ASSETS_DIR = _get_assets_dir()
LOGO_PATH = ASSETS_DIR / "logo.png"
ICON_PATH = ASSETS_DIR / "icon.ico"


# ============================================================
# BUILD INFO
# ============================================================
def get_build_date() -> str:
    """Return the modification date of the main app file (as build date)."""
    try:
        app_file = Path(__file__).parent.parent / "app.py"
        if app_file.exists():
            mtime = app_file.stat().st_mtime
            from datetime import datetime
            return datetime.fromtimestamp(mtime).strftime("%Y-%m-%d")
    except Exception:
        pass
    return "—"