# راهنمای توسعه‌دهنده

## پیش‌نیازها

- Python **3.12** (نه 3.13 یا 3.14 — pydantic-core wheel آماده ندارد)
- pip با آینه PyPI (برای ایران)
- Git (اختیاری، برای نسخه‌بندی)

## راه‌اندازی محیط

```powershell
# ۱. کلون یا دانلود پروژه
cd C:\projects\Translation\Book-analyzer

# ۲. ساخت venv
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1

# ۳. تنظیم آینه PyPI (یک‌بار)
pip config set global.index-url https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple
pip config set global.trusted-host mirrors.tuna.tsinghua.edu.cn

# ۴. نصب وابستگی‌ها
pip install -r requirements.txt

# ۵. کپی .env
Copy-Item .env.example .env
# سپس .env را ویرایش و OPENROUTER_API_KEY را پر کنید

# ۶. دانلود فونت Vazirmatn
# از github.com/rastikerdar/vazirmatn/releases
# دو فایل Vazirmatn-Regular.ttf و Vazirmatn-Bold.ttf را در assets\fonts\ بریزید

# ۷. اجرا
python app.py
ساختار پوشه
text
book-analyzer/
├── app.py                    # نقطه ورود
├── requirements.txt
├── .env
├── .env.example
├── .gitignore
├── README.md
├── LICENSE
│
├── ui/
│   ├── theme.py              # رنگ‌ها، فونت، RTL
│   ├── pages/
│   │   ├── projects_list.py  # لیست پروژه‌ها
│   │   ├── project_view.py   # فرم + تحلیل + نتیجه
│   │   └── settings.py       # Providerها
│   └── components/
│       ├── log_panel.py      # لاگ زنده
│       └── result_view.py    # نمایش تحلیل
│
├── core/
│   ├── analyzer.py           # هماهنگ‌کننده
│   ├── collector.py          # جمع‌آوری منابع
│   ├── crawler.py            # HTTP + پارس
│   ├── search.py             # DuckDuckGo
│   ├── prompt_builder.py     # ساخت پرامپت
│   ├── schemas.py            # Pydantic
│   ├── bilingual.py          # توابع دوزبانه
│   └── prompts/
│       ├── analysis.txt
│       └── translation.txt
│
├── providers/
│   ├── base.py
│   ├── _openai_compatible.py
│   ├── openrouter.py
│   ├── openai.py
│   ├── deepseek.py
│   ├── glm.py
│   ├── gemini.py
│   ├── custom.py
│   ├── registry.py
│   └── manager.py
│
├── storage/
│   ├── db.py                 # init + connection
│   ├── migrations.py         # migrations
│   ├── models.py             # dataclasses
│   └── repositories.py       # CRUD
│
├── exporters/
│   ├── to_json.py            # انگلیسی
│   ├── to_md.py              # فارسی
│   └── to_pdf.py             # فارسی
│
├── services/
│   └── log_bus.py            # انتشار لاگ
│
├── assets/
│   └── fonts/
│       ├── Vazirmatn-Regular.ttf
│       └── Vazirmatn-Bold.ttf
│
├── data/
│   └── projects.db           # SQLite
│
├── output/                   # خروجی پروژه‌ها
│
├── docs/                     # این پوشه
│
└── test_*.py                 # اسکریپت‌های تست دستی
قواعد کد
۱. جداسازی لایه‌ها
ui/ هرگز مستقیماً به DB نمی‌نویسد — همیشه از storage/repositories.py

core/ هرگز به UI import نمی‌کند

providers/ هرگز به core/ import نمی‌کند

۲. لاگ
همیشه از log_bus.emit(level, message, technical=None) استفاده کنید:

level="simple" — برای کاربر

level="technical" — جزئیات فنی (در .env toggle نمایش)

۳. Async
توابع async با async def

در UI با page.run_task(fn, ...)

توابع همگام را با asyncio.to_thread async کنید

۴. دوزبانه
هرگز رشته ساده در schemas.py نگذارید — همیشه Bilingual

در UI/MD: pick(v, "fa")

در JSON/پرامپت: flatten_for_lang(analysis, "en")

۵. مسیرها
همه‌جا pathlib.Path استفاده کنید، نه رشته

مسیرهای نسبی از Path(__file__).parent بسازید

افزودن Provider جدید
مثال: افزودن Together AI
python
# providers/together.py
from providers._openai_compatible import OpenAICompatibleProvider


class TogetherProvider(OpenAICompatibleProvider):
    name = "together"
    label = "Together AI"
    base_url = "https://api.together.xyz/v1"
    env_key = "TOGETHER_API_KEY"
    default_models = [
        "meta-llama/Llama-3.3-70B-Instruct-Turbo",
        "Qwen/Qwen2.5-72B-Instruct-Turbo",
    ]
سپس در providers/registry.py:

python
from providers.together import TogetherProvider

BUILTIN = {
    ...
    TogetherProvider.name: TogetherProvider,
}
و در .env:

env
TOGETHER_API_KEY=...
افزودن بخش جدید به تحلیل
۱. فیلد جدید در core/schemas.py (نوع Bilingual)
۲. توضیح در core/prompts/analysis.txt
۳. نمایش در ui/components/result_view.py (با pick(v, "fa"))
۴. نمایش در exporters/to_md.py

تست دستی هر ماژول
ماژول	دستور
schemas	python -c "from core.schemas import Analysis; print('OK')"
crawler	python test_crawler.py
search	python test_search.py
collector	python test_collector.py
analyzer	python test_analyzer.py
providers	در UI ← تنظیمات ← تست اتصال
عیب‌یابی سریع
خطا	راه‌حل
ModuleNotFoundError: No module named 'core'	__init__.py را در پوشه‌ها بررسی کنید
SyntaxError: New-Item ...	دستور PowerShell را داخل فایل پایتون گذاشته‌اید
OSError: cannot load library 'gobject-2.0-0'	GTK نصب نیست (نگاه کنید TROUBLESHOOTING.md)
RateLimitError: 429	مدل رایگان rate-limit شده، مدل دیگر انتخاب کنید
SSLEOFError هنگام pip install	از آینه PyPI استفاده کنید
انتشار در GitHub
powershell
git init
git add .
git commit -m "Initial commit"

# مطمئن شوید .env و data/ و output/ در .gitignore هستند
git remote add origin https://github.com/<username>/book-analyzer.git
git push -u origin main
ساخت نسخه جدید
powershell
# ۱. بروزرسانی نسخه در docs/CHANGELOG.md
# ۲. اگر وابستگی جدید اضافه شد: pip freeze > requirements.txt
# ۳. commit و tag:
git tag -a v0.2.0 -m "Release 0.2.0"
git push origin v0.2.0
بسته‌بندی (گام ۱۲)
راهنمای کامل در docs/HANDOFF.md.

نکات Python 3.12
جنریک‌ها: list[int] به‌جای List[int]

Union: str | None به‌جای Optional[str]

Pattern matching: برای switch case پیچیده

نیم‌فاصله در ویندوز: از کاراکتر ZWNJ (\u200c) در رشته‌های فارسی

نکات Flet
page.run_task(fn, ...) برای توابع async

page.open(dialog) برای نمایش دیالوگ

page.overlay.append(...) قبل از page.update() برای عناصر شناور

page.update() بعد از هر تغییر UI (یا control.update() برای صرفه‌جویی)

ft.ListView برای ناحیه اسکرول (روان‌تر از ft.Column + scroll)

