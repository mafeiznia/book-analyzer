 راهنمای تست

## رویکرد تست

پروژه از تست خودکار واحد (unit test) در MVP استفاده نمی‌کند. به‌جای آن:

- **تست دستی ماژول‌به‌ماژول** با اسکریپت‌های CLI
- **تست انتها-به-انتها** از طریق UI
- **چک‌لیست** برای هر گام توسعه

فاز بعد (نسخه ۱.x) می‌تواند تست خودکار با `pytest` اضافه کند.

---

## اسکریپت‌های تست CLI

| فایل | نقش | دستور |
|---|---|---|
| `test_crawler.py` | تست دریافت و پارس URLها | `python test_crawler.py` |
| `test_search.py` | تست DuckDuckGo | `python test_search.py` |
| `test_collector.py` | تست جریان کامل crawl + search | `python test_collector.py` |
| `test_analyzer.py` | تست تحلیل LLM کامل | `python test_analyzer.py` |
| `check_db.py` | نمایش محتوای دیتابیس | `python check_db.py` |
| `diag.py` | تشخیص DB + افزودن تستی | `python diag.py` |
| `seed_test.py` | افزودن پروژه‌های نمونه | `python seed_test.py` |
| `clean_test.py` | حذف همه پروژه‌ها | `python clean_test.py` |

**نکته:** این فایل‌ها برای توسعه‌اند، نه تولید. در نسخه نهایی (گام ۱۲) می‌توان حذف شوند یا به پوشه `tests/manual/` منتقل شوند.

---

## چک‌لیست تست هر ماژول

### ماژول crawler

```powershell
python test_crawler.py
انتظار:

Wikipedia: ۱۰۰K+ کاراکتر، زمان < ۵ ثانیه

Goodreads: ۹۰K+ کاراکتر

URL نامعتبر: خطای شبکه با پیام واضح

ماژول search
powershell
python test_search.py "The Great Gatsby F. Scott Fitzgerald"
انتظار: ۵ نتیجه با عنوان، URL، snippet.

نکته: DuckDuckGo ممکن است rate-limit کند. چند دقیقه صبر کنید.

ماژول collector
powershell
python test_collector.py
انتظار (سه سناریو):

بدون لینک ← جست‌وجو فعال، ۳ نتیجه crawl

با Wikipedia ← متن کافی، جست‌وجو غیرفعال

URL نامعتبر ← جست‌وجو فعال

ماژول analyzer
powershell
python test_analyzer.py
پیش‌نیاز: .env با DEFAULT_MODEL معتبر و Provider فعال.

انتظار:

لاگ مرحله ۱/۳، ۲/۳، ۳/۳

خروجی JSON معتبر (دوزبانه)

پرامپت ترجمه تولیدشده

آمار توکن

ماژول exporters
powershell
# JSON
python -c "from exporters.to_json import save_json; print(save_json(1,'Test','A',1,{'genre':{'primary':{'fa':'ت','en':'T'}}},'p',[],'pr','m'))"

# MD
python -c "from exporters.to_md import save_markdown; print(save_markdown(1,'Test','A',1,{},'p',[],'pr','m'))"

# PDF
python -c "from exporters.to_pdf import save_pdf; print(save_pdf(1,'Test',1,'# Test'))"
انتظار: فایل‌ها در output/1_Test/v1/ ساخته شوند.

ماژول providers
از UI:

آیکن چرخ‌دنده ← تنظیمات

«تست اتصال» روی OpenRouter ← پیام «X از Y مدل کار می‌کند»

CLI:

powershell
python -c "from providers.manager import provider_manager; provider_manager.load(); print([r['name'] for r in provider_manager.list_providers()])"
ماژول storage
powershell
python check_db.py
انتظار: تعداد و لیست پروژه‌ها.

تست انتها-به-انتها (UI)
سناریو ۱ — پروژه جدید کامل
«پروژه جدید» ← پر کردن فیلدها ← «ذخیره و بازگشت»

باز کردن پروژه ← «شروع تحلیل»

مشاهده لاگ زنده

مشاهده نتیجه در همان صفحه

بررسی سه فایل در output/<id>_<title>/v1/

سناریو ۲ — بازتحلیل
پروژه قبلی ← «شروع تحلیل» مجدد

انتظار: v2 ساخته شود، v1 حفظ شود

سناریو ۳ — ویرایش Provider
تنظیمات ← OpenRouter ← «ویرایش»

تغییر کلید API ← «ذخیره»

«تست اتصال» ← موفق

بج کلید: 💾 پایگاه داده

«پاک کردن کلید» ← «ذخیره» ← بج: 📄 .env

سناریو ۴ — Provider سفارشی
تنظیمات ← «افزودن Provider سفارشی»

پر کردن فیلدها + کلید API

«افزودن» ← در لیست ظاهر می‌شود

«تست اتصال» ← موفق

«فعال‌سازی» ← فقط این یکی فعال

حذف ← از لیست می‌رود

سناریو ۵ — جست‌وجو
لیست پروژه‌ها ← در باکس جست‌وجو orwell

انتظار: فقط پروژه‌های George Orwell

xyz ← «هیچ پروژه‌ای یافت نشد»

سناریو ۶ — حذف
روی آیکن سطل زباله ← تأیید

انتظار: کارت حذف، از DB هم پاک

چک‌لیست گام‌ها
گام ۱ — اسکلت
□ برنامه با تم تاریک باز می‌شود
□ RTL فارسی
□ SQLite ساخته می‌شود
گام ۲ — Providerها
□ ۵ Provider در لیست
□ تست اتصال کار می‌کند
□ افزودن سفارشی کار می‌کند
□ فعال‌سازی فقط یکی
گام ۳ — CRUD پروژه
□ ساخت / باز کردن / حذف
□ جست‌وجو
□ دکمه 🔄
گام ۴ — فرم ورودی
□ اعتبارسنجی عنوان
□ اعتبارسنجی نویسنده
□ اعتبارسنجی لینک
□ ذخیره / ذخیره و بازگشت
گام ۵ — Crawler
□ Wikipedia کار می‌کند
□ Goodreads کار می‌کند
□ URL نامعتبر خطا می‌دهد
□ چند URL همزمان
گام ۶ — Search
□ جست‌وجو ۵ نتیجه می‌دهد
□ Collector سه سناریو را درست اجرا می‌کند
□ در سناریو Wikipedia جست‌وجو فعال نمی‌شود
گام ۷ — تحلیل
□ test_analyzer.py موفق
□ JSON دوزبانه معتبر
□ حداقل ۳ نکته ترجمه
□ بدون نقل‌قول ساختگی
گام ۸ — پرامپت ترجمه
□ تولید می‌شود
□ کاملاً انگلیسی
□ شامل BOOK PROFILE + GUIDELINES
گام ۹ — UI تحلیل
□ دکمه «شروع تحلیل» فعال
□ لاگ زنده کار می‌کند
□ toggle ساده/فنی
□ ذخیره در DB
گام ۱۰ — خروجی‌ها
□ سه فایل ساخته می‌شوند
□ JSON: انگلیسی
□ MD: فارسی
□ PDF: فارسی + RTL
□ «باز کردن پوشه» Explorer را باز می‌کند
گام ۱۱ — پالایش
□ اسکرول روان
□ باکس پرامپت ۹۰٪ عرض
□ ویرایش Provider کار می‌کند
□ افزودن Provider با کلید API
تست‌های پس از بسته‌بندی (گام ۱۲)
روی ماشین بدون Python:

□ نصب بدون خطا
□ برنامه باز می‌شود
□ فونت فارسی درست
□ Provider تست موفق
□ Crawl لینک
□ تحلیل LLM
□ PDF ساخته می‌شود (حساس!)
□ باز کردن پوشه خروجی
□ Uninstaller همه چیز را پاک می‌کند
تست‌های آینده (pytest)
اگر پروژه به فاز بعدی رسید، این تست‌های خودکار توصیه می‌شوند:

python
# tests/test_schemas.py
def test_bilingual_coerce():
    from core.schemas import Bilingual
    b = Bilingual.model_validate("legacy")
    assert b.fa == "legacy"
    assert b.en == "legacy"

# tests/test_bilingual.py
def test_flatten():
    from core.bilingual import flatten_for_lang
    data = {"genre": {"primary": {"fa": "ت", "en": "T"}}}
    assert flatten_for_lang(data, "fa") == {"genre": {"primary": "ت"}}

# tests/test_repositories.py
def test_create_and_get(tmp_path):
    ...

# tests/test_prompt_builder.py
def test_translation_prompt_is_english():
    ...
هدف: پوشش ۶۰٪+ در نسخه ۱.x.

معیارهای پذیرش MVP
قبل از انتشار نسخه نهایی، این‌ها باید برقرار باشند:

معیار	آستانه
زمان تحلیل یک کتاب	< ۲ دقیقه
دقت ژانر (ارزیابی انسانی)	> ۸۰٪
نرخ موفقیت API	> ۹۵٪
خطاهای PDF	۰
رضایت کاربر	> ۴/۵
حجم بسته نصبی	< ۲۰۰ MB