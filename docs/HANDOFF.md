# سند تحویل پروژه (Handoff)

> **هدف:** این سند برای هر شخصی است که در آینده این پروژه را تحویل می‌گیرد — چه خودتان پس از یک وقفه، چه توسعه‌دهنده جدید.
>
> **آخرین به‌روزرسانی:** نسخه 1.0.0

---

## ۱. وضعیت فعلی پروژه

**نسخه:** 1.0.0 (منتشرشده در GitHub)

**وضعیت:** منتشرشده و قابل استفاده برای کاربر نهایی.

**قابلیت‌ها:**

- مدیریت پروژه‌ها (ساخت، باز کردن، جست‌وجو، حذف)
- تحلیل LLM کتاب (ژانر، لحن، سبک، نکات ترجمه)
- خروجی دوزبانه: JSON (انگلیسی) + MD/PDF (فارسی)
- تولید خودکار پرامپت ترجمه
- Providerهای چندگانه (Groq, OpenRouter, OpenAI, Gemini, DeepSeek, GLM) + سفارشی
- تست اتصال چندمدلی
- ویرایش Provider و کلید API
- انتخاب مدل per-project
- لاگ زنده + دکمه کپی + لغو تحلیل + زمان‌سنج
- نسخه‌بندی تحلیل‌ها در `output/<project>/v<N>/`
- تم روشن و تاریک با toggle
- بخش About با اطلاعات نویسنده و تکنولوژی‌ها

**وضعیت تست:** تمام تست‌ها روی ویندوز x64 با Python 3.12 و روی ماشین دوم موفق.

**وضعیت بسته‌بندی:** انجام شده — installer در GitHub Releases.

---

## ۲. اطلاعات زمینه‌ای مهم

### چرا این پروژه ساخته شد؟

مترجم/ویراستار حرفه‌ای قبل از شروع ترجمه یک کتاب، نیاز دارد بداند:

- کتاب از چه ژانری است؟
- لحن و سبک نویسنده چگونه است؟
- چه چالش‌هایی در ترجمه انگلیسی → فارسی وجود دارد؟

هدف این ابزار، کاهش این زمان از ساعات به چند دقیقه است.

### تصمیمات محصولی مهم

| تصمیم | چرا |
|---|---|
| **تک‌کاربره** | کاربر یک مترجم تنهاست |
| **Local-first (SQLite)** | کتاب‌ها محرمانه‌اند |
| **دوزبانه در یک جا** | LLM یک‌بار تحلیل می‌کند، هر دو زبان را می‌دهد |
| **بدون دیالوگ Save برای خروجی** | FilePicker روی ویندوز باگ دارد |
| **Provider plugin-based** | پوشش ۹۰٪ سرویس‌ها با یک interface |
| **Python 3.12 (نه 3.14)** | pydantic-core و weasyprint wheel آماده ندارند |

---

## ۳. نقشه پوشه‌ها

```text
book-analyzer/
├── app.py                    ← نقطه ورود، Router اصلی
├── requirements.txt
├── .env                      ← کلیدها (در .gitignore)
├── .env.example
├── build_release.ps1         ← اسکریپت build خودکار
├── LICENSE
├── README.md
│
├── ui/                       ← رابط کاربری
│   ├── theme.py
│   ├── pages/
│   │   ├── projects_list.py
│   │   ├── project_view.py   ← بزرگ‌ترین فایل
│   │   └── settings.py
│   └── components/
│       ├── log_panel.py
│       ├── result_view.py
│       └── about_dialog.py
│
├── core/                     ← منطق اصلی
│   ├── analyzer.py
│   ├── collector.py
│   ├── crawler.py
│   ├── search.py
│   ├── prompt_builder.py
│   ├── schemas.py
│   ├── bilingual.py
│   ├── about_info.py
│   ├── settings.py
│   └── prompts/
│       ├── analysis.txt
│       └── translation.txt
│
├── providers/
│   ├── base.py
│   ├── _openai_compatible.py
│   ├── manager.py
│   └── ...
│
├── storage/
│   ├── db.py
│   ├── migrations.py
│   └── repositories.py
│
├── exporters/
│   ├── to_json.py            ← انگلیسی
│   ├── to_md.py              ← فارسی
│   └── to_pdf.py             ← فارسی + WeasyPrint
│
├── assets/
│   ├── fonts/
│   ├── logo.png
│   └── icon.ico
│
├── data/projects.db          ← SQLite (خودکار)
├── output/                   ← خروجی‌ها
├── installer/                ← Inno Setup
├── docs/                     ← مستندات
└── test/                     ← تست‌های دستی
```

---

## ۴. اجرای پروژه

```powershell
# فعال‌سازی venv
.\.venv\Scripts\Activate.ps1

# اجرا
python app.py
```

اگر venv نیست:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

---

## ۵. اطلاعات حساس و امنیتی

### فایل `.env`

- شامل کلیدهای API
- **در `.gitignore`** — هرگز commit نشود
- اگر لو رفت، کلید را در Provider باطل و کلید جدید بسازید

### کلیدها در DB

- جدول `providers` ستون `api_key` دارد
- **اگر `data/projects.db` به اشتراک گذاشته شود، کلیدها هم لو می‌روند**
- اسکریپت `build_release.ps1` این فایل را پاک می‌کند

### لاگ‌ها

- `log_bus` هرگز `api_key` را چاپ نمی‌کند
- فقط `has_key: True/False` در لاگ‌های فنی

---

## ۶. کارهای باقی‌مانده (TODO)

### نسخه ۱.x — بهبودها

- [ ] پاراگراف‌بندی هوشمند کتاب (chunking) برای کتاب‌های بزرگ
- [ ] اجرای موازی چند مدل + داوری بین نتایج
- [ ] export به XLIFF (برای CAT tools)
- [ ] کش کردن نتایج crawl
- [ ] نمایش هزینه تخمینی قبل از تحلیل
- [ ] ARM64 build برای ویندوز ARM

### تست خودکار

- [ ] افزودن `pytest` و تست‌های واحد
- [ ] CI با GitHub Actions

### مستندات

- [ ] اسکرین‌شات‌های بیشتر در README
- [ ] ویدیوی راهنما

---

## ۷. مسائل شناخته‌شده

| # | مسئله | شدت | راه‌حل موقت |
|---|---|---|---|
| ۱ | اسکرول تکه‌تکه در ویندوز | کم | با اسکرول‌بار کار می‌کند |
| ۲ | مدل‌های رایگان OpenRouter ناپایدار | متوسط | استفاده از Groq |
| ۳ | کیفیت ترجمه اسامی با مدل‌های کوچک | کم | مدل بزرگ‌تر انتخاب کنید |
| ۴ | 403 روی بعضی سایت‌ها | کم | سایت دیگر یا متن دستی |
| ۵ | پاسخ JSON غیرمعتبر از LLM | متوسط | `_extract_json` خودکار حل می‌کند |
| ۶ | نبود ARM64 installer | کم | فقط x64 فعلاً |

---

## ۸. وابستگی‌های کلیدی

```text
flet==0.24.1
python-dotenv==1.0.1
httpx==0.27.2
beautifulsoup4==4.12.3
lxml==5.3.0
ddgs
openai==1.54.3
google-generativeai==0.8.3
pydantic>=2.12,<3
weasyprint==63.0
markdown==3.7
pyperclip==1.11.0
```

**نکات مهم:**

- `ddgs` جایگزین `duckduckgo-search`
- `pydantic>=2.12` برای Python 3.14، ولی توصیه Python 3.12
- `weasyprint` روی ویندوز به GTK نیاز دارد

---

## ۹. افزودن Provider جدید

مثال: افزودن Together AI

### گام ۱ — فایل جدید

```python
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
```

### گام ۲ — ثبت در registry

```python
# providers/registry.py
from providers.together import TogetherProvider

BUILTIN = {
    ...
    TogetherProvider.name: TogetherProvider,
}
```

### گام ۳ — کلید در `.env`

```env
TOGETHER_API_KEY=...
```

برنامه را ری‌استارت کنید. Provider جدید در لیست ظاهر می‌شود.

---

## ۱۰. افزودن بخش جدید به تحلیل

۱. `core/schemas.py` — فیلد جدید (نوع `Bilingual`)
۲. `core/prompts/analysis.txt` — توضیح در پرامپت
۳. `ui/components/result_view.py` — نمایش (با `pick(v, "fa")`)
۴. `exporters/to_md.py` — افزودن به گزارش

---

## ۱۱. مسیر پیشرفت توصیه‌شده

اگر می‌خواهید پروژه را ادامه دهید:

1. **پاکسازی test/** — قبل از انتشار عمومی
2. **افزودن `pytest`** — پایداری بلندمدت
3. **Chunking هوشمند** — اگر با کتاب‌های بزرگ کار می‌کنید
4. **ARM64 build** — اگر کاربر Mac M-series یا Windows ARM دارید
5. **نسخه وب** — اگر می‌خواهید به چند کاربر سرویس بدهید

---

## ۱۲. مستندات مرتبط

- `docs/ARCHITECTURE.md` — معماری تفصیلی
- `docs/DEVELOPER_GUIDE.md` — راه‌اندازی و توسعه
- `docs/USER_GUIDE.md` — راهنمای کاربر
- `docs/TESTING_GUIDE.md` — تست‌ها
- `docs/TROUBLESHOOTING.md` — مشکلات رایج
- `docs/ROADMAP.md` — نقشه راه
- `docs/CHANGELOG.md` — تاریخچه تغییرات
- **`docs/HANDOFF_PROVIDERS.md`** — چارچوب Provider (قابل استفاده مجدد)
- **`docs/HANDOFF_ABOUT_DIALOG.md`** — چارچوب About (قابل استفاده مجدد)
- **`docs/HANDOFF_INSTALLER.md`** — چارچوب Installer (قابل استفاده مجدد)

### مخزن GitHub

- کد: [github.com/mafeiznia/book-analyzer](https://github.com/mafeiznia/book-analyzer)
- Releases: [github.com/mafeiznia/book-analyzer/releases](https://github.com/mafeiznia/book-analyzer/releases)

### تکنولوژی‌ها

- Flet: [flet.dev/docs](https://flet.dev/docs/)
- Pydantic v2: [docs.pydantic.dev](https://docs.pydantic.dev/latest/)
- WeasyPrint: [doc.courtbouillon.org/weasyprint](https://doc.courtbouillon.org/weasyprint/)
- ddgs: [pypi.org/project/ddgs](https://pypi.org/project/ddgs/)
- Groq: [console.groq.com](https://console.groq.com)
- OpenRouter: [openrouter.ai/docs](https://openrouter.ai/docs)

---

## ۱۳. نکات برای تحویل‌گیرنده

### اولین روز

1. **قبل از تغییر، یک شاخه جدید در Git بسازید.**
2. **قبل از اجرای هر تحلیلی، `.env` را چک کنید.**
3. **`python app.py` برای تست سریع.**
4. **اگر همه چیز خراب شد، `data/projects.db` را از نسخه پشتیبان برگردانید.**
5. **هیچ‌گاه `api_key` واقعی را در GitHub push نکنید.**

### کارهایی که نباید بکنید

- Provider builtin را حذف نکنید
- Schema دیتابیس را بدون migration تغییر ندهید
- فایل `.env` را commit نکنید
- `api_key` را در لاگ چاپ نکنید
- نام Provider را بعد از انتشار عوض نکنید

### اگر می‌خواهید چیزی اضافه کنید

1. ابتدا در `docs/ROADMAP.md` ثبت کنید
2. Schema را در `core/schemas.py` تعریف کنید (با `Bilingual`)
3. پرامپت را در `core/prompts/analysis.txt` توضیح دهید
4. UI را در `ui/components/result_view.py` نمایش دهید
5. Export را در `exporters/` اعمال کنید
6. تست کنید
7. در `docs/CHANGELOG.md` ثبت کنید

---

## ۱۴. اطلاعات کاربر اصلی

**نام:** محمود اهرپور فیض‌نیا
**نقش:** مترجم/ویراستار حرفه‌ای
**نیاز اصلی:** تحلیل سریع کتاب‌های انگلیسی قبل از ترجمه به فارسی
**Provider پیش‌فرض:** Groq (رایگان)
**زبان رابط کاربری:** فارسی RTL
**تم پیش‌فرض:** روشن

---

## ۱۵. امضای تحویل

| نقش | نام | تاریخ |
|---|---|---|
| توسعه‌دهنده | محمود اهرپور فیض‌نیا | ۱۴۰۴ |
| تحویل‌گیرنده | — | — |

---

**پایان سند HANDOFF**

هر سؤالی داشتید، ابتدا مستندات مرتبط را ببینید. اگر پاسخ نبود، در GitHub Issues مطرح کنید.