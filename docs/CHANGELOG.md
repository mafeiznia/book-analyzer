# Changelog

تمام تغییرات مهم پروژه در این فایل ثبت می‌شود.


## [1.1.0] — ارتقاء Flet — ۱۴۰۴

ارتقاء Flet از `0.24.1` به `0.28.3` برای رفع باگ اسکرول.

### افزوده
- پشتیبانی از نسخه جدید Flet 0.28.3
- نسخه Flet به جدول «اطلاعات فنی» در دیالوگ About اضافه شد

### تغییر
- `ft.colors.*` → `ft.Colors.*` (۱۲۰ مورد در ۶ فایل UI)
- `ft.icons.*` → `ft.Icons.*` (۱۲۰ مورد در ۶ فایل UI)
- `flet==0.24.1` → `flet==0.28.3` در `requirements.txt`
- `duckduckgo-search==6.3.5` → `ddgs==9.16.0` در `requirements.txt`
- چیدمان جدول «اطلاعات فنی» به RTL کامل (برچسب فارسی راست‌چین، مقدار انگلیسی چپ‌چین)
- نسخه از `1.0.0` به `1.1.0` در `build_release.ps1`, `core/about_info.py`, `installer/BookAnalyzer_x64.iss`

### رفع
- **باگ اسکرول تکه‌تکه با چرخ ماوس** (محدودیت Flet 0.24) — حل شده در Flet 0.28.3
- باگ نمایش خالی «تاریخ ساخت» در دیالوگ About
- باگ چپ‌چین بودن جدول اطلاعات فنی در نسخه frozen

### یادداشت
- مهاجرت به Flet 1.0 **متوقف شد** — چون هدف اصلی (رفع باگ اسکرول) در 0.28.3 محقق شد و مهاجرت به 1.0 شامل breaking changes گسترده است.
- سند `docs/HANDOFF_FLET_MIGRATION.md` به‌عنوان مرجع آینده حفظ می‌شود.

---

## [1.0.0] — انتشار عمومی — ۱۴۰۴

اولین نسخه پایدار و قابل انتشار.

### افزوده
- بخش «درباره» با دیالوگ About (نسخه، نویسنده، تکنولوژی‌ها، مجوز)
- آیکن ℹ️ در هدرهای لیست پروژه‌ها و تنظیمات
- فایل `LICENSE` (MIT)
- `core/about_info.py` — متادیتای برنامه
- `ui/components/about_dialog.py` — دیالوگ About
- Provider **Groq** با سه مدل (`openai/gpt-oss-120b`, `openai/gpt-oss-20b`, `qwen/qwen3.8-27b`)
- انتخاب مدل در فرم پروژه (per-project model)
- دکمه «لغو تحلیل» در حین کار
- نمایش زمان سپری‌شده با فرمت `⏱ MM:SS`
- دکمه «کپی لاگ» در پنجره لاگ زنده
- اسکریپت `build_release.ps1` برای build خودکار و پاکسازی
- Installer با Inno Setup (`installer/BookAnalyzer_x64.iss`)
- مستندات کامل ۸ گانه + ۳ سند HANDOFF
- پیام «(لغو شد)» روی زمان‌سنج پس از لغو

### تغییر
- اولویت انتخاب مدل: dropdown فرم → `DEFAULT_MODEL` در `.env`
- Providerها اولویت کلید: پایگاه داده → `.env`
- همه مسیرها (`data`, `output`, `assets`, `prompts`) با `sys.frozen` سازگار شدند
- تم تاریک با رنگ زیتونی به‌عنوان پیش‌فرض

### رفع
- باگ «گیر کردن LLM» در محیط exe (timeout صریح + `max_retries=0` + `import httpx`)
- باگ `PermissionError` در rebuild (بستن پروسه + اسکریپت)
- باگ نمایش نشدن فونت/لوگو در محیط frozen
- باگ کپی نشدن متن لاگ (به‌خاطر `selectable` ناسازگار در ویندوز)

### محدودیت‌های شناخته‌شده
- اسکرول صفحه با چرخ ماوس «تکه‌تکه» است (محدودیت Flet 0.24 روی ویندوز دسکتاپ)
- مدل‌های رایگان OpenRouter ناپایدار هستند (راه‌حل: Groq یا شارژ OpenRouter)

---

## [0.11.0] — گام ۱۱
### افزوده
- تست اتصال چندمدلی (چند مدل به‌جای یکی)
- ویرایش Provider (کلید API، مدل‌ها)
- پشتیبانی از `api_key` در پایگاه داده
- بج منبع کلید (`💾 پایگاه داده` / `📄 .env` / `⚠️ تنظیم نشده`)

## [0.10.0] — گام ۱۰
### افزوده
- خروجی JSON (انگلیسی) + MD (فارسی) + PDF (فارسی)
- نسخه‌بندی خروجی‌ها در `output/<project>/v<N>/`
- دکمه «باز کردن پوشه خروجی» در UI
- دوزبانه‌سازی کامل (fa/en) با `Bilingual` type و `flatten_for_lang`
- `core/bilingual.py` با توابع `pick`, `pick_list`, `flatten_for_lang`

### حذف
- دیالوگ Save فایل (به‌خاطر باگ FilePicker روی ویندوز)

## [0.9.0] — گام ۹
### افزوده
- دکمه «شروع تحلیل» در صفحه پروژه
- پنجره لاگ زنده با toggle ساده/فنی
- `LogBus` با تاریخچه + subscribe/unsubscribe
- ذخیره‌سازی تحلیل در `analyses` (نسخه‌بندی)

## [0.8.0] — گام ۸
### افزوده
- تولید خودکار پرامپت ترجمه
- `core/prompts/translation.txt`
- `build_translation_prompt` در `prompt_builder.py`

## [0.7.0] — گام ۷
### افزوده
- تحلیل LLM با خروجی JSON اعتبارسنجی‌شده
- `core/schemas.py` (Pydantic)
- `core/prompts/analysis.txt`
- `core/analyzer.py` (analyze_book)
- `core/prompt_builder.py`
- `test_analyzer.py` (CLI)
- رفع مشکل import JSON از پاسخ LLM (strip code fences + extract braces)

## [0.6.0] — گام ۶
### افزوده
- جست‌وجوی خودکار با DuckDuckGo (`ddgs`)
- `core/search.py`
- `core/collector.py` (crawl + fallback search)

### تغییر
- مهاجرت از `duckduckgo-search` به `ddgs` (به‌خاطر مشکل build Rust)

## [0.5.0] — گام ۵
### افزوده
- ماژول Crawler (`core/crawler.py`)
- پشتیبانی از async + timeout + User-Agent
- تست CLI (`test_crawler.py`)

## [0.4.0] — گام ۴
### افزوده
- فرم ورودی واقعی پروژه (عنوان، نویسنده، لینک‌ها، متن نمونه)
- اعتبارسنجی فیلدها
- دکمه‌های «ذخیره» و «ذخیره و بازگشت»
- دکمه 🔄 بروزرسانی در لیست پروژه‌ها
- `serialize_urls` / `parse_urls` در repositories

## [0.3.0] — گام ۳
### افزوده
- CRUD کامل پروژه‌ها (`storage/repositories.py`)
- صفحه لیست پروژه‌ها با جست‌وجو و حذف
- حالت خالی و حالت پر

## [0.2.0] — گام ۲
### افزوده
- لایه Provider با ۵ builtin (OpenRouter, OpenAI, DeepSeek, GLM, Gemini)
- `ProviderManager` (load, set_active, add_custom, remove_custom)
- صفحه تنظیمات Providerها
- تست اتصال چندمدلی
- افزودن Provider سفارشی

### تغییر
- مدل‌های builtin همیشه از کد خوانده می‌شوند (نه DB)

## [0.1.0] — گام ۱
### افزوده
- اسکلت پروژه (Flet + SQLite)
- تم تاریک با رنگ زیتونی و RTL فارسی
- فونت Vazirmatn
- صفحه لیست پروژه‌ها (placeholder)
- `LogBus` اولیه
- `.gitignore` و `.env.example`