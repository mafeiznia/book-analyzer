# راهنمای تست

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
| `test/test_crawler.py` | تست دریافت و پارس URLها | `python -m test.test_crawler` |
| `test/test_search.py` | تست DuckDuckGo | `python -m test.test_search` |
| `test/test_collector.py` | تست جریان کامل crawl + search | `python -m test.test_collector` |
| `test/test_analyzer.py` | تست تحلیل LLM کامل | `python -m test.test_analyzer` |
| `test/check_db.py` | نمایش محتوای دیتابیس | `python -m test.check_db` |
| `test/diag.py` | تشخیص DB + افزودن تستی | `python -m test.diag` |
| `test/seed_test.py` | افزودن پروژه‌های نمونه | `python -m test.seed_test` |
| `test/clean_test.py` | حذف همه پروژه‌ها | `python -m test.clean_test` |

**نکته:** این فایل‌ها برای توسعه‌اند، نه تولید.

---

## چک‌لیست تست هر ماژول

### ماژول crawler

```powershell
python -m test.test_crawler
```

**انتظار:**

- Wikipedia: ۱۰۰K+ کاراکتر، زمان < ۵ ثانیه
- Goodreads: ۹۰K+ کاراکتر
- URL نامعتبر: خطای شبکه با پیام واضح

### ماژول search

```powershell
python -m test.test_search "The Great Gatsby F. Scott Fitzgerald"
```

**انتظار:** ۵ نتیجه با عنوان، URL، snippet.

**نکته:** DuckDuckGo ممکن است rate-limit کند. چند دقیقه صبر کنید.

### ماژول collector

```powershell
python -m test.test_collector
```

**انتظار (سه سناریو):**

1. **بدون لینک** → جست‌وجو فعال، ۳ نتیجه crawl
2. **با Wikipedia** → متن کافی، جست‌وجو غیرفعال
3. **URL نامعتبر** → جست‌وجو فعال

### ماژول analyzer

```powershell
python -m test.test_analyzer
```

**پیش‌نیاز:** `.env` با `DEFAULT_MODEL` معتبر و Provider فعال.

**انتظار:**

- لاگ مرحله ۱/۳، ۲/۳، ۳/۳
- خروجی JSON معتبر (دوزبانه)
- پرامپت ترجمه تولیدشده
- آمار توکن

### ماژول exporters

```powershell
# JSON
python -c "from exporters.to_json import save_json; print(save_json(1,'Test','A',1,{'genre':{'primary':{'fa':'ت','en':'T'}}},'p',[],'pr','m'))"

# MD
python -c "from exporters.to_md import save_markdown; print(save_markdown(1,'Test','A',1,{},'p',[],'pr','m'))"

# PDF
python -c "from exporters.to_pdf import save_pdf; print(save_pdf(1,'Test',1,'# Test'))"
```

**انتظار:** فایل‌ها در `output/1_Test/v1/` ساخته شوند.

### ماژول providers

از UI:

- آیکن چرخ‌دنده → تنظیمات
- «تست اتصال» روی Provider → پیام «X از Y مدل کار می‌کند»

CLI:

```powershell
python -c "from providers.manager import provider_manager; provider_manager.load(); print([r['name'] for r in provider_manager.list_providers()])"
```

### ماژول storage

```powershell
python -m test.check_db
```

**انتظار:** تعداد و لیست پروژه‌ها.

---

## تست انتها-به-انتها (UI)

### سناریو ۱ — پروژه جدید کامل

1. «پروژه جدید» → پر کردن فیلدها → «ذخیره و بازگشت»
2. باز کردن پروژه → «شروع تحلیل»
3. مشاهده لاگ زنده
4. مشاهده نتیجه در همان صفحه
5. بررسی سه فایل در `output/<id>_<title>/v1/`

### سناریو ۲ — بازتحلیل

1. پروژه قبلی → «شروع تحلیل» مجدد
2. **انتظار:** `v2` ساخته شود، `v1` حفظ شود

### سناریو ۳ — ویرایش Provider

1. تنظیمات → Provider → «ویرایش»
2. تغییر کلید API → «ذخیره»
3. «تست اتصال» → موفق
4. بج کلید: `💾 پایگاه داده`
5. «پاک کردن کلید» → «ذخیره» → بج: `📄 .env`

### سناریو ۴ — Provider سفارشی

1. تنظیمات → «افزودن Provider سفارشی»
2. پر کردن فیلدها + کلید API
3. «افزودن» → در لیست ظاهر می‌شود
4. «تست اتصال» → موفق
5. «فعال‌سازی» → فقط این یکی فعال
6. حذف → از لیست می‌رود

### سناریو ۵ — جست‌وجو

1. لیست پروژه‌ها → در باکس جست‌وجو `orwell`
2. **انتظار:** فقط پروژه‌های George Orwell
3. `xyz` → «هیچ پروژه‌ای یافت نشد»

### سناریو ۶ — حذف

1. روی آیکن سطل زباله → تأیید
2. **انتظار:** کارت حذف، از DB هم پاک

### سناریو ۷ — تغییر تم

1. روی آیکن 🌙/☀️ در هدر بزنید
2. **انتظار:** تم عوض شود، در همه صفحات اعمال شود
3. برنامه را ببندید و باز کنید → تم ذخیره‌شده حفظ شود

### سناریو ۸ — لغو تحلیل

1. یک تحلیل را شروع کنید
2. قبل از اتمام، روی «لغو تحلیل» بزنید
3. **انتظار:** تحلیل متوقف شود، زمان‌سنج با برچسب «(لغو شد)» ثابت بماند

---

## چک‌لیست گام‌ها

### گام ۱ — اسکلت

- [ ] برنامه با تم روشن باز می‌شود
- [ ] RTL فارسی
- [ ] SQLite ساخته می‌شود

### گام ۲ — Providerها

- [ ] ۶ Provider در لیست
- [ ] تست اتصال کار می‌کند
- [ ] افزودن سفارشی کار می‌کند
- [ ] فعال‌سازی فقط یکی

### گام ۳ — CRUD پروژه

- [ ] ساخت / باز کردن / حذف
- [ ] جست‌وجو
- [ ] دکمه 🔄

### گام ۴ — فرم ورودی

- [ ] اعتبارسنجی عنوان
- [ ] اعتبارسنجی نویسنده
- [ ] اعتبارسنجی لینک
- [ ] ذخیره / ذخیره و بازگشت

### گام ۵ — Crawler

- [ ] Wikipedia کار می‌کند
- [ ] Goodreads کار می‌کند
- [ ] URL نامعتبر خطا می‌دهد
- [ ] چند URL همزمان

### گام ۶ — Search

- [ ] جست‌وجو ۵ نتیجه می‌دهد
- [ ] Collector سه سناریو را درست اجرا می‌کند
- [ ] در سناریو Wikipedia جست‌وجو فعال نمی‌شود

### گام ۷ — تحلیل

- [ ] `test_analyzer.py` موفق
- [ ] JSON دوزبانه معتبر
- [ ] حداقل ۳ نکته ترجمه
- [ ] بدون نقل‌قول ساختگی

### گام ۸ — پرامپت ترجمه

- [ ] تولید می‌شود
- [ ] کاملاً انگلیسی
- [ ] شامل BOOK PROFILE + GUIDELINES

### گام ۹ — UI تحلیل

- [ ] دکمه «شروع تحلیل» فعال
- [ ] لاگ زنده کار می‌کند
- [ ] toggle ساده/فنی
- [ ] دکمه کپی لاگ
- [ ] ذخیره در DB

### گام ۱۰ — خروجی‌ها

- [ ] سه فایل ساخته می‌شوند
- [ ] JSON: انگلیسی
- [ ] MD: فارسی
- [ ] PDF: فارسی + RTL
- [ ] «باز کردن پوشه» Explorer را باز می‌کند

### گام ۱۱ — پالایش

- [ ] انتخاب مدل per-project
- [ ] دکمه «لغو تحلیل»
- [ ] نمایش زمان سپری‌شده
- [ ] ویرایش Provider کار می‌کند
- [ ] افزودن Provider با کلید API
- [ ] About با لوگو

### گام ۱۲ — انتشار

- [ ] `build_release.ps1` موفق
- [ ] Installer ساخته می‌شود
- [ ] نسخه `1.0.0` در About
- [ ] نصب روی ماشین دوم
- [ ] تست کامل روی ماشین دوم
- [ ] انتشار در GitHub Releases

---

## تست‌های پس از بسته‌بندی

روی ماشین **بدون Python**:

- [ ] نصب بدون خطا
- [ ] برنامه باز می‌شود
- [ ] فونت فارسی درست
- [ ] About کار می‌کند
- [ ] Provider تست موفق
- [ ] Crawl لینک
- [ ] تحلیل LLM
- [ ] **PDF ساخته می‌شود** (حساس!)
- [ ] باز کردن پوشه خروجی
- [ ] Uninstaller همه چیز را پاک می‌کند

---

## تست‌های آینده (pytest)

اگر پروژه به فاز بعدی رسید، این تست‌های خودکار توصیه می‌شوند:

```python
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


# tests/test_prompt_builder.py
def test_translation_prompt_is_english():
    ...
```

هدف: پوشش ۶۰٪+ در نسخه ۱.x.

---

## معیارهای پذیرش MVP

| معیار | آستانه |
|---|---|
| زمان تحلیل یک کتاب | < ۲ دقیقه |
| دقت ژانر (ارزیابی انسانی) | > ۸۰٪ |
| نرخ موفقیت API | > ۹۵٪ |
| خطاهای PDF | ۰ |
| رضایت کاربر | > ۴/۵ |
| حجم بسته نصبی | < ۲۰۰ MB |