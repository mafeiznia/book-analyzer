# معماری Book Analyzer

> آخرین به‌روزرسانی: پس از گام ۱۱

## خلاصه

Book Analyzer یک برنامه دسکتاپ تک‌کاربره است که برای مترجم/ویراستار حرفه‌ای طراحی شده تا با گرفتن عنوان، نویسنده، چند لینک و بخشی از متن کتاب، تحلیلی چهارمحوری از آن تولید کند (ژانر، لحن، سبک، نکات ترجمه) و سه خروجی بدهد: JSON (انگلیسی)، MD و PDF (فارسی).

## لایه‌ها
┌─────────────────────────────────────────────────────────┐
│ UI Layer (Flet + Python) │
│ app.py (Router) │
│ ui/pages/projects_list.py │
│ ui/pages/project_view.py │
│ ui/pages/settings.py │
│ ui/components/log_panel.py │
│ ui/components/result_view.py │
│ ui/theme.py │
└───────────────────────┬─────────────────────────────────┘
│
┌───────────────────────▼─────────────────────────────────┐
│ Core Layer │
│ analyzer.py — هماهنگ‌کننده اصلی │
│ collector.py — جمع‌آوری منابع │
│ crawler.py — HTTP + استخراج متن │
│ search.py — DuckDuckGo │
│ prompt_builder.py — ساخت پرامپت │
│ schemas.py — اسکیمای Pydantic │
│ bilingual.py — توابع کمکی دوزبانه │
│ prompts/ — قالب‌های پرامپت (txt) │
└───────────────────────┬─────────────────────────────────┘
│
┌───────────────┼───────────────┐
▼ ▼ ▼
┌──────────────┐ ┌────────────┐ ┌──────────────┐
│ Providers │ │ Storage │ │ Exporters │
│ Manager │ │ SQLite │ │ json/md/pdf │
└──────────────┘ └────────────┘ └──────────────┘
│
▼
┌──────────────────────────────┐
│ External APIs │
│ OpenRouter / OpenAI / ... │
│ DuckDuckGo │
│ Target websites (crawl) │
└──────────────────────────────┘

text

## جریان کار
۱. کاربر فرم پروژه را پر می‌کند
↓
۲. پروژه در SQLite ذخیره می‌شود
↓
۳. کلیک «شروع تحلیل»:
۳.۱ collector.py لینک‌های کاربر را crawl می‌کند
۳.۲ اگر متن کافی نبود، DuckDuckGo جست‌وجو می‌کند
۳.۳ prompt_builder پرامپت تحلیل را می‌سازد
۳.۴ provider.ask() ← LLM
۳.۵ analyzer.py خروجی JSON را با Pydantic اعتبارسنجی می‌کند
۳.۶ prompt_builder پرامپت ترجمه را می‌سازد
↓
۴. نتیجه در SQLite ذخیره می‌شود (نسخه‌بندی شده)
↓
۵. سه فایل در output/<project>/v<N>/ ساخته می‌شود:

analysis.json (انگلیسی)

report.md (فارسی)

report.pdf (فارسی)
↓
۶. نتیجه در UI نمایش داده می‌شود (فارسی)

text

## دوزبانه‌سازی (Design Pattern)

هر فیلد متنی خروجی LLM به‌صورت `{"fa": "...", "en": "..."}` است. سپس:

| مصرف‌کننده | زبان | جایگاه |
|---|---|---|
| UI (نمایش) | fa | pick(v, "fa") |
| report.md | fa | flatten_for_lang(analysis, "fa") |
| report.pdf | fa | از MD |
| analysis.json | en | flatten_for_lang(analysis, "en") |
| پرامپت ترجمه | en | flatten_for_lang(analysis, "en") |

## مدل داده (SQLite)
projects
id, title, author, urls (JSON), snippet, status,
created_at, updated_at

analyses
id, project_id, version, provider, model,
result_json (دوزبانه), translation_prompt,
sources_used (JSON), tokens_in, tokens_out, cost_usd,
created_at

providers
id, name, base_url, env_key, api_key,
is_builtin, is_active, models (JSON), created_at

logs
id, project_id, level, message, technical (JSON), created_at

text

## ساختار Provider (Plugin Pattern)
providers/
base.py — interface
_openai_compatible.py — پایه مشترک
openrouter.py — پیاده‌سازی
openai.py — پیاده‌سازی
deepseek.py — پیاده‌سازی
glm.py — پیاده‌سازی
gemini.py — پیاده‌سازی
custom.py — Provider سفارشی
registry.py — ثبت builtinها
manager.py — بارگذاری + فعال‌سازی

text

## خروجی‌ها
output/
└── <project_id>_<slug>/
├── v1/
│ ├── analysis.json
│ ├── report.md
│ └── report.pdf
├── v2/
│ └── ...

text

## وابستگی‌های اصلی

| کتابخانه | نقش |
|---|---|
| flet | UI دسکتاپ |
| httpx | HTTP async |
| beautifulsoup4 + lxml | پارس HTML |
| ddgs | جست‌وجوی DuckDuckGo |
| openai | SDK سازگار OpenAI |
| google-generativeai | SDK Gemini |
| pydantic v2 | اعتبارسنجی + دوزبانه |
| weasyprint | PDF |
| markdown | MD ← HTML |
| pyperclip | کپی کلیپ‌بورد |
| python-dotenv | فایل .env |

## تصمیمات کلیدی معماری

1. تک‌پروسه (بدون سرور جدا): Flet UI و منطق در یک پروسه.
2. Local-first: SQLite + فایل‌سیستم محلی.
3. دوزبانه در یک جا: LLM هر دو نسخه را می‌دهد؛ مصرف‌کننده انتخاب می‌کند.
4. Plugin-based providers: افزودن provider = یک فایل.
5. بدون وابستگی به سرویس خاص: هر Provider سازگار OpenAI کار می‌کند.
6. نسخه‌بندی خروجی: هر تحلیل = یک نسخه جدید در v<N>.
7. تک‌ناحیه اسکرول: کل صفحه یک اسکرول (ListView)، widgetهای داخلی بدون scroll.
