# عیب‌یابی

<div dir="rtl" markdown="1">

این سند مشکلات رایج و راه‌حل آن‌ها را فهرست می‌کند.

---

## خطاهای نصب

### خطای `SSLEOFError` یا `ConnectionError` هنگام `pip install`

**علت:** اتصال به PyPI اصلی از ایران مشکل دارد.

**راه‌حل:** از آینه PyPI استفاده کنید:

```powershell
pip install -r requirements.txt -i https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple
```

یا برای همیشه:

```powershell
pip config set global.index-url https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple
pip config set global.trusted-host mirrors.tuna.tsinghua.edu.cn
```

آینه‌های جایگزین:

- `https://mirrors.aliyun.com/pypi/simple/`
- `https://pypi.tuna.tsinghua.edu.cn/simple`

---

### خطای `metadata-generation-failed` برای `pydantic-core`

**علت:** Python 3.13 یا 3.14 نصب است و pydantic-core wheel آماده ندارد. pip می‌خواهد از سورس build کند که نیاز به Rust دارد.

**راه‌حل:** Python 3.12 نصب کنید و venv را با آن بسازید:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

---

### خطای `subprocess-exited-with-error` برای `pyreqwest-impersonate` یا `curl_cffi`

**علت:** `duckduckgo-search` قدیمی به Rust نیاز دارد.

**راه‌حل:** از پکیج جدید `ddgs` استفاده کنید:

```powershell
pip uninstall -y duckduckgo-search curl_cffi pyreqwest-impersonate
pip install ddgs
```

---

### خطای `OSError: cannot load library 'gobject-2.0-0'`

**علت:** WeasyPrint برای ساخت PDF به کتابخانه GTK نیاز دارد که روی ویندوز نصب نیست.

**راه‌حل ۱ (ساده):** GTK را از [github.com/tschoonj/GTK-for-Windows-Runtime-Installer](https://github.com/tschoonj/GTK-for-Windows-Runtime-Installer/releases) دانلود و نصب کنید. سپس ترمینال را ببندید و باز کنید.

**راه‌حل ۲ (Playwright):** به Playwright مهاجرت کنید:

```powershell
pip install playwright
playwright install chromium
```

---

## خطاهای اجرا

### خطای `ModuleNotFoundError: No module named 'core'`

**علت:** فایل `__init__.py` در یکی از پوشه‌ها نیست.

**راه‌حل:** این فایل‌های خالی را بسازید:

```powershell
New-Item -ItemType File -Path core\__init__.py -Force
New-Item -ItemType File -Path ui\__init__.py -Force
New-Item -ItemType File -Path ui\pages\__init__.py -Force
New-Item -ItemType File -Path ui\components\__init__.py -Force
New-Item -ItemType File -Path providers\__init__.py -Force
New-Item -ItemType File -Path storage\__init__.py -Force
New-Item -ItemType File -Path services\__init__.py -Force
New-Item -ItemType File -Path exporters\__init__.py -Force
```

---

### خطای `SyntaxError: invalid syntax` در `__init__.py`

**علت:** دستور PowerShell را داخل فایل پایتون گذاشته‌اید.

**راه‌حل:** فایل `__init__.py` باید **خالی** باشد. محتوایش را پاک کنید.

---

### خطای `DeprecationWarning: window_width is deprecated`

**علت:** Flet API قدیمی.

**راه‌حل:** در `app.py` از API جدید استفاده کنید:

```python
# از:
page.window_width = 1100

# به:
page.window.width = 1100
```

---

### خطای `await outside async function`

**علت:** `FilePicker.save_file()` در بعضی نسخه‌های Flet روی ویندوز پاسخ نمی‌دهد.

**راه‌حل:** دیالوگ Save را حذف کنید و به‌جای آن دکمه «باز کردن پوشه خروجی» بگذارید.

---

### خطای `TypeError` در `result_view.py` بعد از افزودن دوزبانه

**علت:** فیلدها الان `{"fa": ..., "en": ...}` هستند ولی UI رشته انتظار دارد.

**راه‌حل:** از `pick(value, "fa")` استفاده کنید:

```python
from core.bilingual import pick, pick_list

# به‌جای:
genre.get("primary")

# بنویسید:
pick(genre.get("primary"), "fa")
```

---

## خطاهای Provider

### `RateLimitError: 429` — You have no credits

**علت:** حساب OpenAI اعتبار ندارد.

**راه‌حل:** یا اعتبار اضافه کنید، یا از OpenRouter (رایگان) یا Groq استفاده کنید.

---

### `RateLimitError: 429` — temporarily rate-limited upstream

**علت:** مدل رایگان OpenRouter موقتاً rate-limit شده.

**راه‌حل:**

1. در تنظیمات، «تست اتصال» بزنید تا ببینید کدام مدل‌ها کار می‌کنند.
2. در `.env`، `DEFAULT_MODEL` را به مدل کارکننده تغییر دهید.
3. یا چند دقیقه صبر کنید.
4. **بهترین راه‌حل:** از Groq استفاده کنید (پایدار و رایگان).

---

### `NotFoundError: 404` — This model is unavailable for free

**علت:** مدل قبلاً رایگان بود ولی الان نیست.

**راه‌حل:** از [openrouter.ai/models?max_price=0](https://openrouter.ai/models?max_price=0) مدل جدید بردارید و در `providers/openrouter.py` و `.env` جایگزین کنید.

---

### پس از تغییر کلید API، همچنان کلید قدیمی استفاده می‌شود

**علت:** ممکن است کلید جدید در DB ذخیره نشده باشد.

**راه‌حل:**

1. تنظیمات → ویرایش Provider → بررسی بج (باید `💾 پایگاه داده` باشد)
2. اگر `📄 .env` است، یعنی کلید DB خالی است و از `.env` می‌خواند.
3. کلید را در فیلد API وارد کنید و «ذخیره» بزنید.

---

### خطای `Unable to locate credentials`

**علت:** Provider فعال کلید ندارد.

**راه‌حل:**

1. تنظیمات → Provider مورد نظر → «تست اتصال»
2. اگر پیام «کلید API تنظیم نشده» داد:
   - کلید را در DB وارد کنید (دکمه ویرایش)، یا
   - `.env` را پر کنید و برنامه را ری‌استارت کنید

---

## خطاهای تحلیل

### «خروجی LLM معتبر نبود»

**علت:** مدل JSON معتبر تولید نکرده (متن اضافه قبل/بعد، یا ساختار اشتباه).

**راه‌حل‌ها:**

1. مدل قوی‌تر انتخاب کنید (مثلاً Gemini یا `openai/gpt-oss-120b` روی Groq).
2. اگر متن اضافه قبل از JSON است، تابع `_extract_json` خودش آن را حل می‌کند. اگر باز هم خطا دارد، متن خطا را در لاگ فنی ببینید.
3. اگر ساختار اشتباه است (فیلدی نیست)، احتمالاً مدل از اسکیما پیروی نکرده. مدل عوض کنید.

---

### «طول پرامپت خیلی زیاد است» یا خطای context length

**علت:** متن منابع بیش از حد طولانی.

**راه‌حل:** در `core/prompt_builder.py`:

```python
MAX_TOTAL_SOURCE_CHARS = 24_000  # ← این را به 12_000 کاهش دهید
```

---

### «هیچ منبعی برای تحلیل در دسترس نیست»

**علت:** همه لینک‌ها خطا دادند و جست‌وجو هم نتیجه نداد.

**راه‌حل:**

1. لینک‌های دیگر امتحان کنید (Wikipedia معمولاً کار می‌کند).
2. اتصال اینترنت را بررسی کنید.
3. متن کتاب را دستی در فیلد «بخشی از متن کتاب» وارد کنید.

---

### «هیچ Provider فعالی وجود ندارد»

**علت:** در تنظیمات، هیچ Provider فعال نشده.

**راه‌حل:** تنظیمات → «فعال‌سازی» روی یکی از Providerها.

---

## خطاهای PDF

### PDF خالی است یا کاراکترهای مربع (□□□) نمایش می‌دهد

**علت:** فونت Vazirmatn ثبت نشده.

**راه‌حل:** مطمئن شوید فایل‌های فونت در `assets/fonts/` هستند:

```text
assets/fonts/Vazirmatn-Regular.ttf
assets/fonts/Vazirmatn-Bold.ttf
```

و در `exporters/to_pdf.py`، در CSS:

```css
body {
    font-family: Vazirmatn, Tahoma, sans-serif;
}
```

---

### PDF ساخته می‌شود ولی متن از چپ نوشته شده (LTR)

**علت:** CSS در `to_pdf.py` جهت را RTL نکرده.

**راه‌حل:** در HTML template:

```html
<body style="direction: rtl; text-align: right;">
```

---

## خطاهای دیتابیس

### خطای `sqlite3.OperationalError: no such column: api_key`

**علت:** Migration اجرا نشده.

**راه‌حل:** فایل `storage/migrations.py` را بررسی کنید و `init_db()` را دوباره صدا بزنید:

```powershell
python -c "from storage.db import init_db; init_db(); print('OK')"
```

---

### پروژه‌های قبلی نمایش داده نمی‌شوند

**علت:** برنامه cache دارد (از آخرین خواندن DB).

**راه‌حل:** دکمه 🔄 در هدر لیست پروژه‌ها را بزنید، یا برنامه را ری‌استارت کنید.

---

## خطاهای ظاهری

### اسکرول روان نیست

**علت:** محدودیت شناخته‌شده Flet 0.24 روی ویندوز دسکتاپ.

**راه‌حل:** فعلاً قابل رفع نیست. با اسکرول‌بار کار می‌کند. در نسخه‌های Flet 1.0+ ممکن است حل شود.

---

### فونت فارسی نمایش داده نمی‌شود

**راه‌حل:** در `ui/theme.py`، `register_fonts(page)` را در `main()` صدا بزنید.

---

### در LogPanel، لاگ‌های فنی نمایش داده نمی‌شوند

**علت:** toggle «نمایش لاگ فنی» خاموش است.

**راه‌حل:** روی toggle بزنید تا روشن شود.

---

## خطاهای بسته‌بندی

### پس از بسته‌بندی، برنامه باز نمی‌شود

**علت:** Flet client همراه بسته نیست.

**راه‌حل:** از `flet pack` رسمی استفاده کنید، نه PyInstaller خام:

```powershell
flet pack app.py --name BookAnalyzer --onedir
```

---

### پس از بسته‌بندی، PDF ساخته نمی‌شود

**علت:** GTK Runtime همراه بسته نیست.

**راه‌حل ۱:** DLLهای GTK را در بسته بگنجانید.

**راه‌حل ۲:** در اسکریپت Inno Setup، GTK Runtime را به‌عنوان پیش‌نیاز نصب کنید.

---

## دریافت کمک

اگر مشکل شما در این سند نبود:

1. **کنسول را بررسی کنید**: آخرین خطا را یادداشت کنید.
2. **لاگ فنی را روشن کنید**: در صفحه پروژه، toggle «نمایش لاگ فنی» را روشن کنید.
3. **GitHub Issues**: با توضیح کامل + خروجی خطا + سیستم‌عامل، issue باز کنید.
4. **دیباگ مرحله‌به‌مرحله**: از `test/*.py` برای جدا کردن مشکل استفاده کنید.

---

## چه چیزی را در گزارش خطا بفرستید

هنگام گزارش مشکل، این‌ها را بفرستید:

- **سیستم‌عامل:** ویندوز ۱۱، ARM64 یا x64
- **Python:** `python --version`
- **نسخه Flet:** `pip show flet`
- **خروجی کامل ترمینال**: از ابتدا تا انتها
- **آخرین لاگ فنی از LogPanel**
- **محتوای `.env`** (بدون کلیدهای واقعی!)
- **چه کاری انجام دادید که به خطا خوردید**

</div>