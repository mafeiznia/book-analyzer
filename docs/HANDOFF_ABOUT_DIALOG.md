# HANDOFF — دیالوگ About (درباره برنامه)

> **هدف این سند:** یک چارچوب قابل استفاده مجدد برای افزودن دیالوگ «درباره» به هر برنامه Flet.
>
> **مبنا:** پروژه Book Analyzer (Flet 0.24+, Python 3.12).
>
> **سازگاری:** Flet 0.24+، pyperclip (اختیاری)، RTL فارسی.

---

## ۱. هدف و دامنه

### چرا دیالوگ About؟

یک بخش «درباره» استاندارد در هر برنامه دسکتاپی:
- اطلاعات نسخه و تاریخ ساخت
- اطلاعات تماس نویسنده/تیم
- لینک به سایت، ایمیل، شبکه‌های اجتماعی
- لیست تکنولوژی‌های استفاده‌شده
- مجوز و کپی‌رایت

### چرا به‌صورت دیالوگ (نه صفحه مستقل)؟

- سبک‌تر: نیازی به Route جدید یا صفحه جداگانه نیست
- قابل دسترس از هر جای برنامه
- UX آشناتر: کاربران انتظار دارند About یک modal کوچک باشد

## ۲. ساختار فایل‌ها

```
core/
  about_info.py              ← همه متادیتا (یک منبع حقیقت)
ui/
  components/
    about_dialog.py          ← سازنده دیالوگ
  pages/
    projects_list.py         ← آیکن ℹ️ در هدر
    settings.py              ← (اختیاری) آیکن ℹ️ در هدر
assets/
  logo.png                   ← لوگو (اختیاری)
  icon.ico                   ← آیکن برنامه
```

**اصل کلیدی:** همه اطلاعات در `core/about_info.py` متمرکز است. هر جا نیاز شد (دیالوگ، README، بسته‌بندی)، از همان منبع می‌خواند.

## ۳. فایل `core/about_info.py`

```python
"""Application metadata for the About dialog.

Edit this file to update app info, author details, or tech stack.
"""
from pathlib import Path


# ============================================================
# APPLICATION
# ============================================================
APP_NAME = "Book Analyzer"
APP_VERSION = "0.11.0"
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
AUTHOR_LINKEDIN_URL = "https://www.linkedin.com/in/..."


# ============================================================
# LICENSE & COPYRIGHT
# ============================================================
LICENSE_NAME = "MIT License"
COPYRIGHT_YEAR = "2026"
COPYRIGHT_HOLDER = "Mahmoud Aharpour Feiznia"


# ============================================================
# REPOSITORY
# ============================================================
GITHUB_URL = ""  # اگر خالی باشد، دکمه‌اش نمایش داده نمی‌شود


# ============================================================
# TECHNOLOGY STACK
# ============================================================
TECH_STACK: list[tuple[str, str]] = [
    ("رابط کاربری", "Flet (Python) + Material 3"),
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
ASSETS_DIR = Path(__file__).parent.parent / "assets"
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
```

### نکات کلیدی طراحی این فایل

1. **همه چیز در یک ماژول خالص پایتون** — بدون وابستگی به Flet، بدون import سنگین.
2. **لیست‌ها به‌صورت tuple list** — آسان برای تکرار در UI.
3. **مسیرها با `pathlib.Path`** — قابل حمل بین ویندوز و لینوکس.
4. **`get_build_date()` با try/except** — اگر `app.py` نبود (مثلاً در exe)، به "—" برمی‌گردد.
5. **`GITHUB_URL` خالی = عدم نمایش دکمه** — رفتار تطبیقی.

## ۴. فایل `ui/components/about_dialog.py`

```python
"""About dialog — app info, author, tech stack."""
import webbrowser

import flet as ft

from core.about_info import (
    APP_NAME, APP_TAGLINE_FA, APP_VERSION,
    AUTHOR_EMAIL, AUTHOR_LINKEDIN_URL,
    AUTHOR_NAME_EN, AUTHOR_NAME_FA,
    AUTHOR_WEBSITE, AUTHOR_WEBSITE_URL,
    COPYRIGHT_HOLDER, COPYRIGHT_YEAR,
    GITHUB_URL, LICENSE_NAME, LOGO_PATH,
    TECH_STACK, get_build_date,
)
from ui.theme import OLIVE_PRIMARY


def _open_url(page: ft.Page, url: str) -> None:
    """Open URL in default browser."""
    if not url:
        page.open(ft.SnackBar(ft.Text("⚠️ آدرس تنظیم نشده است")))
        page.update()
        return
    try:
        webbrowser.open(url)
    except Exception as ex:
        page.open(ft.SnackBar(ft.Text(f"❌ خطا: {ex}")))
    page.update()


def _copy_to_clipboard(page: ft.Page, text: str, label: str = "متن") -> None:
    """Copy text to clipboard."""
    try:
        import pyperclip
        pyperclip.copy(text)
        page.open(ft.SnackBar(ft.Text(f"✅ {label} کپی شد")))
    except ImportError:
        page.open(ft.SnackBar(ft.Text("⚠️ pyperclip نصب نیست")))
    except Exception as ex:
        page.open(ft.SnackBar(ft.Text(f"❌ خطا: {ex}")))
    page.update()


def show_about_dialog(page: ft.Page) -> None:
    """Build and show the About dialog."""

    # --- Logo ---
    logo_control: ft.Control
    if LOGO_PATH.exists():
        logo_control = ft.Container(
            content=ft.Image(
                src=str(LOGO_PATH), width=96, height=96,
                fit=ft.ImageFit.CONTAIN,
            ),
            width=96, height=96,
            alignment=ft.alignment.center,
        )
    else:
        logo_control = ft.Container(
            content=ft.Icon(ft.icons.MENU_BOOK, size=64, color=OLIVE_PRIMARY),
            width=96, height=96,
            alignment=ft.alignment.center,
        )

    # --- Header ---
    header = ft.Column(
        [
            logo_control,
            ft.Container(height=4),
            ft.Text(APP_NAME, size=22, weight=ft.FontWeight.BOLD),
            ft.Text(f"نسخه {APP_VERSION}", size=13, color=ft.colors.OUTLINE),
            ft.Container(height=4),
            ft.Text(APP_TAGLINE_FA, size=13, italic=True,
                    color=ft.colors.ON_SURFACE_VARIANT),
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=2,
    )

    # --- Author buttons ---
    def _author_button(icon, label, on_click) -> ft.Control:
        return ft.TextButton(
            content=ft.Row(
                [
                    ft.Icon(icon, size=16, color=OLIVE_PRIMARY),
                    ft.Text(label, size=12),
                ],
                spacing=6, tight=True,
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            on_click=on_click,
        )

    author_row_buttons = ft.Row(
        [
            _author_button(ft.icons.EMAIL, "ایمیل",
                lambda e: _copy_to_clipboard(page, AUTHOR_EMAIL, "ایمیل")),
            _author_button(ft.icons.LINK, "LinkedIn",
                lambda e: _open_url(page, AUTHOR_LINKEDIN_URL)),
            _author_button(ft.icons.LANGUAGE, AUTHOR_WEBSITE,
                lambda e: _open_url(page, AUTHOR_WEBSITE_URL)),
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=4,
    )

    author_block = ft.Container(
        content=ft.Column(
            [
                ft.Text("طراحی و توسعه", size=11, color=ft.colors.OUTLINE),
                ft.Text(AUTHOR_NAME_FA, size=14, weight=ft.FontWeight.BOLD),
                ft.Text(AUTHOR_NAME_EN, size=12,
                        color=ft.colors.ON_SURFACE_VARIANT),
                ft.Container(height=4),
                author_row_buttons,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=2,
        ),
        padding=10,
        bgcolor=ft.colors.with_opacity(0.04, ft.colors.ON_SURFACE),
        border_radius=8,
    )

    # --- Tech stack ---
    tech_rows = []
    for label, value in TECH_STACK:
        tech_rows.append(
            ft.Row(
                [
                    ft.Text(f"{label}:", size=11,
                            weight=ft.FontWeight.BOLD, width=100),
                    ft.Text(value, size=11, selectable=True, expand=True),
                ],
                vertical_alignment=ft.CrossAxisAlignment.START,
            )
        )

    tech_rows.append(
        ft.Row(
            [
                ft.Text("تاریخ ساخت:", size=11,
                        weight=ft.FontWeight.BOLD, width=100),
                ft.Text(get_build_date(), size=11,
                        selectable=True, color=ft.colors.OUTLINE),
            ],
        )
    )

    tech_block = ft.Container(
        content=ft.Column(
            [
                ft.Row(
                    [
                        ft.Icon(ft.icons.BUILD, size=14, color=OLIVE_PRIMARY),
                        ft.Text("اطلاعات فنی", size=12,
                                weight=ft.FontWeight.BOLD),
                    ],
                    spacing=6,
                ),
                ft.Divider(height=1),
                *tech_rows,
            ],
            spacing=6,
        ),
        padding=10,
        bgcolor=ft.colors.with_opacity(0.03, ft.colors.PRIMARY),
        border_radius=8,
    )

    # --- Footer ---
    footer_parts = [
        ft.Text(f"© {COPYRIGHT_YEAR} {COPYRIGHT_HOLDER}",
                size=10, color=ft.colors.OUTLINE),
        ft.Text(f"مجوز: {LICENSE_NAME}", size=10, color=ft.colors.OUTLINE),
    ]

    if GITHUB_URL:
        footer_parts.append(
            ft.TextButton(
                "مخزن GitHub",
                icon=ft.icons.CODE,
                on_click=lambda e: _open_url(page, GITHUB_URL),
            )
        )

    footer = ft.Column(
        footer_parts,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=0,
    )

    # --- Content ---
    content = ft.Column(
        [
            header,
            ft.Divider(height=1),
            author_block,
            tech_block,
            ft.Divider(height=1),
            footer,
        ],
        spacing=10,
        tight=True,
        width=380,
        scroll=ft.ScrollMode.AUTO,
    )

    # --- Dialog ---
    dlg = ft.AlertDialog(
        modal=True,
        content=content,
        actions=[
            ft.TextButton("بستن", on_click=lambda e: _close(dlg, page)),
        ],
        actions_alignment=ft.MainAxisAlignment.CENTER,
    )

    page.overlay.append(dlg)
    dlg.open = True
    page.update()


def _close(dlg: ft.AlertDialog, page: ft.Page) -> None:
    dlg.open = False
    page.update()
```

## ۵. افزودن به صفحات

### آیکن ℹ️ در هدر

در هر صفحه‌ای که می‌خواهید دکمه About داشته باشد:

```python
from ui.components.about_dialog import show_about_dialog

# در header یا هر Row:
ft.IconButton(
    icon=ft.icons.INFO_OUTLINE,
    tooltip="درباره برنامه",
    on_click=lambda e: show_about_dialog(page),
)
```

### محل قرارگیری توصیه‌شده

```
[عنوان صفحه]                    [ℹ️]  [⚙️]
```

- **ℹ️ (Info):** قبل از تنظیمات
- **⚙️ (Settings):** آخرین آیکن

## ۶. رفتار دکمه‌ها

| دکمه | رفتار | fallback |
|---|---|---|
| ایمیل | کپی در کلیپ‌بورد + SnackBar | اگر pyperclip نیست → پیام هشدار |
| LinkedIn | باز کردن در مرورگر | اگر آدرس خالی → SnackBar هشدار |
| سایت | باز کردن در مرورگر | اگر آدرس خالی → SnackBar هشدار |
| GitHub (اختیاری) | باز کردن در مرورگر | اگر آدرس خالی → دکمه نمایش داده نمی‌شود |
| بستن | غیرفعال کردن `dlg.open` | — |

### چرا ایمیل کپی می‌شود نه mailto؟

- `mailto:` روی بعضی سیستم‌ها نیاز به کلاینت ایمیل پیش‌فرض دارد که ممکن است تنظیم نباشد
- کپی ساده‌تر و مطمئن‌تر است — کاربر خودش در Gmail/Outlook پیست می‌کند

## ۷. Layout

```
┌─────────────────────────────────────────────┐
│  ┌──────┐                                   │
│  │ LOGO │                                   │
│  └──────┘                                   │
│                                             │
│  Book Analyzer                              │
│  نسخه 0.11.0                                │
│  تحلیل‌گر هوشمند کتاب برای مترجمان           │
│  ─────────────────────────────────          │
│                                             │
│  ┌─ طراحی و توسعه ──────────────────────┐  │
│  │      محمود اهرپور فیض‌نیا             │  │
│  │      Mahmoud Aharpour Feiznia        │  │
│  │  [ایمیل]  [LinkedIn]  [yadoto.ir]    │  │
│  └──────────────────────────────────────┘  │
│                                             │
│  ┌─ 🔧 اطلاعات فنی ──────────────────────┐  │
│  │  رابط کاربری:  Flet...                │  │
│  │  زبان:         Python 3.12            │  │
│  │  دیتابیس:      SQLite                 │  │
│  │  ...                                  │  │
│  │  تاریخ ساخت:   2026-09-29             │  │
│  └──────────────────────────────────────┘  │
│  ─────────────────────────────────          │
│                                             │
│       © 2026 Mahmoud Aharpour Feiznia       │
│       مجوز: MIT License                     │
│                                             │
│              [بستن]                         │
└─────────────────────────────────────────────┘
```

## ۸. نکات طراحی و UX

### رنگ‌ها
- **آیکن‌ها (ایمیل، LinkedIn، سایت):** رنگ اصلی برنامه (`OLIVE_PRIMARY`)
- **پس‌زمینه بلوک نویسنده:** `with_opacity(0.04, ON_SURFACE)`
- **پس‌زمینه بلوک فنی:** `with_opacity(0.03, PRIMARY)`
- **متن‌های ثانویه:** `OUTLINE` یا `ON_SURFACE_VARIANT`

### اندازه‌ها
- **عرض دیالوگ:** ۳۸۰ پیکسل (مناسب محتوای دو ستونی جدول تکنولوژی)
- **لوگو:** ۹۶×۹۶
- **`tight=True`** در Column — جلوگیری از فاصله‌های اضافی
- **`scroll=AUTO`** — اگر محتوا از ارتفاع صفحه بیشتر شد

### تفکیک‌های بصری
- **`Divider(height=1)`** بین بخش‌های اصلی
- **بلوک‌های `Container` با `border_radius=8`** برای گروه‌بندی
- **فاصله `spacing=10`** بین بخش‌ها

### RTL
- چون `page.rtl = True` در `app.py`، همه چیز خودکار RTL می‌شود
- آیکن‌ها کنار متن درست قرار می‌گیرند

## ۹. لوگو — پرامپت طراحی

اگر لوگو ندارید، از این پرامپت در **Recraft** (recraft.ai) یا **Ideogram** استفاده کنید:

```
Design a modern minimal app icon for a desktop application called 
"Book Analyzer".

CONCEPT:
A stylized open book viewed from a slight angle, with a subtle 
magnifying glass overlaying one of its pages — representing 
literary analysis.

STYLE:
- Flat design with subtle depth (not 3D, not skeuomorphic)
- Minimal, geometric shapes
- Clean lines, no unnecessary detail
- App icon style with rounded square background

COLORS:
- Primary background: olive green (#9CAF3F)
- Book: warm cream (#F5F1E0) or soft white
- Magnifying glass: darker olive (#5A6B1F) with gold accent (#C3D36E)

OUTPUT:
- Square aspect ratio (1:1)
- 1024x1024 minimum
- Transparent background AND solid olive background versions
- No text, no letters
- No border or outline
```

### تبدیل PNG به ICO

پس از دریافت لوگو:

```powershell
pip install pillow
python -c "from PIL import Image; img = Image.open('assets/logo.png'); img.save('assets/icon.ico', sizes=[(16,16),(32,32),(48,48),(64,64),(128,128),(256,256)])"
```

یا آنلاین: `cloudconvert.com/png-to-ico`

## ۱۰. تست

### تست import

```powershell
python -c "from ui.components.about_dialog import show_about_dialog; print('OK')"
```

### تست UI

```powershell
python app.py
```

**چک‌لیست:**
- [ ] آیکن ℹ️ در هدر دیده می‌شود
- [ ] با کلیک، دیالوگ باز می‌شود
- [ ] لوگو (اگر هست) نمایش داده می‌شود
- [ ] نام برنامه و نسخه
- [ ] «طراحی و توسعه» + نام فارسی و انگلیسی
- [ ] دکمه‌های ایمیل / LinkedIn / سایت
- [ ] کپی ایمیل در کلیپ‌بورد
- [ ] باز شدن LinkedIn در مرورگر
- [ ] باز شدن سایت در مرورگر
- [ ] جدول تکنولوژی
- [ ] تاریخ ساخت
- [ ] کپی‌رایت و مجوز
- [ ] دکمه «بستن» دیالوگ را می‌بندد
- [ ] **هیچ خطای کنسولی نیست**

## ۱۱. مسائل شناخته‌شده

| مسئله | علت | راه‌حل |
|---|---|---|
| لوگو نمایش داده نمی‌شود | مسیر `assets/logo.png` اشتباه | `LOGO_PATH` در `about_info.py` را بررسی کنید |
| فونت فارسی مربعی است | فونت Vazirmatn ثبت نشده | `register_fonts(page)` در `app.py` |
| LinkedIn باز نمی‌شود | URL تنظیم نشده | `AUTHOR_LINKEDIN_URL` را پر کنید |
| دکمه‌ها کار نمی‌کنند | `page.update()` نیست | در انتهای هر هندلر `page.update()` |
| کلیک روی ℹ️ خطا می‌دهد | `page` به `show_about_dialog` نرسیده | در lambda: `lambda e: show_about_dialog(page)` |

## ۱۲. سفارشی‌سازی برای پروژه جدید

### مرحله ۱ — کپی فایل‌ها

```
core/about_info.py
ui/components/about_dialog.py
```

### مرحله ۲ — ویرایش `about_info.py`

- `APP_NAME`، `APP_VERSION`، `APP_TAGLINE_FA`
- اطلاعات نویسنده/تیم
- `TECH_STACK` مطابق پروژه جدید
- `LOGO_PATH` اگر مسیر متفاوتی دارد

### مرحله ۳ — افزودن به هدر

```python
from ui.components.about_dialog import show_about_dialog

ft.IconButton(
    icon=ft.icons.INFO_OUTLINE,
    tooltip="درباره برنامه",
    on_click=lambda e: show_about_dialog(page),
)
```

### مرحله ۴ — (اختیاری) تغییر رنگ

اگر پروژه رنگ اصلی دیگری دارد (نه سبز زیتونی):

```python
# در about_dialog.py
from ui.theme import PRIMARY_COLOR  # ← رنگ پروژه جدید
```

## ۱۳. الگوهای قابل استفاده مجدد

### الگوی کلی: «لیست tuple برای جدول»

```python
TECH_STACK: list[tuple[str, str]] = [
    ("عنوان", "مقدار"),
    ...
]

for label, value in TECH_STACK:
    # ساخت ردیف
```

**مزیت:** به‌راحتی از YAML/JSON یا DB قابل بارگذاری است.

### الگوی کلی: «fallback برای فایل‌های غایب»

```python
if LOGO_PATH.exists():
    control = ft.Image(src=str(LOGO_PATH))
else:
    control = ft.Icon(ft.icons.MENU_BOOK)  # fallback
```

**مزیت:** برنامه با یا بدون asset کار می‌کند.

### الگوی کلی: «دکمه‌های عملیاتی با try/except»

```python
def _open_url(page, url):
    if not url:
        show_warning()
        return
    try:
        webbrowser.open(url)
    except Exception as ex:
        show_error(ex)
```

**مزیت:** هیچ خطای runtime، همیشه پیام واضح به کاربر.

## ۱۴. وابستگی‌ها

```
flet>=0.24        # AlertDialog, Image, IconButton
pyperclip>=1.11   # (اختیاری) کپی در کلیپ‌بورد
```

اگر `pyperclip` نصب نیست، فقط کپی ایمیل از کار می‌افتد؛ بقیه چیزها کار می‌کنند.

## ۱۵. خلاصه تصمیمات کلیدی

| تصمیم | دلیل |
|---|---|
| متادیتا در فایل جداگانه | یک منبع حقیقت، قابل استفاده در README و بسته‌بندی |
| دیالوگ به‌جای صفحه | سبک‌تر، UX آشناتر |
| `webbrowser.open` برای URLها | بدون وابستگی به کتابخانه‌های اضافی |
| `pyperclip` برای ایمیل | کاربر ایمیل را در Gmail پیست می‌کند، نه mailto |
| `GITHUB_URL` خالی = پنهان | رفتار تطبیقی برای پروژه‌های بدون GitHub |
| fallback برای لوگو | کار در محیط توسعه و نصب |
| لیست tuple برای تکنولوژی | قابل خواندن از YAML/JSON در آینده |

---

**پایان سند HANDOFF_ABOUT_DIALOG**

این چارچوب در Book Analyzer تست شده و قابل استفاده مستقیم در هر برنامه Flet است. برای سازگاری کامل، فقط `ui/theme.py` پروژه مقصد را با رنگ اصلی خودتان هماهنگ کنید یا `OLIVE_PRIMARY` را با نام رنگ پروژه خود جایگزین کنید.