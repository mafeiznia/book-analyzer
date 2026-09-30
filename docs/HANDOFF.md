# سند تحویل پروژه (Handoff)

> **هدف:** این سند برای هر شخصی است که در آینده این پروژه را تحویل می‌گیرد — چه خودتان پس از یک وقفه، چه توسعه‌دهنده جدید.
>
> **آخرین به‌روزرسانی:** پس از گام ۱۱

---

## ۱. وضعیت فعلی پروژه

**نسخه:** 0.11.0 (MVP تکمیل‌شده)

**وضعیت:** قابل استفاده برای کاربر نهایی (مترجم/ویراستار).

**قابلیت‌ها:**
- مدیریت پروژه‌ها (ساخت، باز کردن، جست‌وجو، حذف)
- تحلیل LLM کتاب (ژانر، لحن، سبک، نکات ترجمه)
- خروجی دوزبانه: JSON (انگلیسی) + MD/PDF (فارسی)
- تولید خودکار پرامپت ترجمه
- Providerهای چندگانه با تست اتصال چندمدلی
- ویرایش Provider و افزودن Provider سفارشی
- لاگ زنده (ساده/فنی)
- نسخه‌بندی تحلیل‌ها در `output/<project>/v<N>/`

**وضعیت تست:** تمام گام‌های ۱ تا ۱۱ روی ویندوز x64 با Python 3.12 تست شده.

**وضعیت بسته‌بندی:** هنوز انجام نشده (گام ۱۲).

---

## ۲. اطلاعات زمینه‌ای مهم

### چرا این پروژه ساخته شد؟

مترجم/ویراستار حرفه‌ای (کاربر اصلی) قبل از شروع ترجمه یک کتاب، نیاز دارد بداند:
- کتاب از چه ژانری است؟
- لحن و سبک نویسنده چگونه است؟
- چه چالش‌هایی در ترجمه انگلیسی ← فارسی وجود دارد؟

قبل از این پروژه، این کار به‌صورت دستی انجام می‌شد و ساعات زیادی طول می‌کشید. هدف این ابزار، کاهش این زمان به چند دقیقه است.

### تصمیمات محصولی مهم

| تصمیم | چرا |
|---|---|
| **تک‌کاربره** | کاربر یک مترجم تنهاست، نه تیم |
| **Local-first (SQLite)** | کتاب‌ها محرمانه‌اند، نباید در سرور ذخیره شوند |
| **دوزبانه در یک جا** | LLM یک‌بار تحلیل می‌کند، هر دو زبان را می‌دهد |
| **بدون دیالوگ Save برای خروجی** | FilePicker روی ویندوز باگ دارد؛ به‌جایش «باز کردن پوشه» |
| **Provider plugin-based** | پوشش ۹۰٪ سرویس‌ها با یک interface |
| **Python 3.12 (نه 3.14)** | pydantic-core و weasyprint wheel آماده ندارند |

---

## ۳. نقشه پوشه‌ها — چه چیزی مهم است
book-analyzer/
├── app.py ← نقطه ورود، Router اصلی
├── requirements.txt ← وابستگی‌ها
├── .env ← کلیدهای API (در .gitignore)
├── .env.example ← نمونه
│
├── ui/ ← رابط کاربری
│ ├── theme.py ← رنگ، فونت، RTL
│ ├── pages/
│ │ ├── projects_list.py
│ │ ├── project_view.py ← بزرگ‌ترین فایل، همه UI تحلیل
│ │ └── settings.py ← مدیریت Providerها
│ └── components/
│ ├── log_panel.py
│ └── result_view.py
│
├── core/ ← منطق اصلی
│ ├── analyzer.py ← analyze_book() — قلب پروژه
│ ├── collector.py
│ ├── crawler.py
│ ├── search.py
│ ├── prompt_builder.py
│ ├── schemas.py ← Bilingual, Analysis
│ ├── bilingual.py ← pick, flatten_for_lang
│ └── prompts/
│ ├── analysis.txt ← پرامپت تحلیل (انگلیسی)
│ └── translation.txt ← پرامپت ترجمه (انگلیسی)
│
├── providers/ ← لایه Providerها
│ ├── base.py ← interface
│ ├── _openai_compatible.py ← کلاس پایه مشترک
│ ├── manager.py ← ProviderManager
│ └── ...
│
├── storage/
│ ├── db.py ← SCHEMA + init
│ ├── migrations.py ← migrations
│ └── repositories.py ← CRUD
│
├── exporters/
│ ├── to_json.py ← انگلیسی
│ ├── to_md.py ← فارسی
│ └── to_pdf.py ← فارسی + WeasyPrint
│
├── assets/fonts/ ← Vazirmatn (باید دانلود شود)
├── data/projects.db ← SQLite (خودکار ساخته می‌شود)
├── output/ ← خروجی‌ها
└── docs/ ← همین مستندات

text

---

## ۴. چطور پروژه را اجرا کنیم (تکرار سریع)

```powershell
# ۱. فعال‌سازی venv
.\.venv\Scripts\Activate.ps1

# ۲. بررسی .env
Get-Content .env

# ۳. اجرا
python app.py
اگر venv نیست:

powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
# سپس .env را ویرایش کنید
اگر فونت نیست: از github.com/rastikerdar/vazirmatn/releases دانلود کنید و دو فایل .ttf را در assets/fonts/ بگذارید.

۵. اطلاعات حساس و امنیتی
فایل .env
شامل کلیدهای API واقعی

در .gitignore هست — هرگز commit نشود

اگر لو رفت، کلید را در Provider باطل و کلید جدید بسازید

کلیدها در DB
جدول providers ستون api_key دارد

اگر کاربر کلید را در UI وارد کرده باشد، در data/projects.db ذخیره می‌شود

اگر data/projects.db به اشتراک گذاشته شود، کلیدها هم لو می‌روند

برای انتشار عمومی DB، ابتدا data/ را پاک کنید

لاگ‌ها
log_bus هرگز api_key را چاپ نمی‌کند

فقط has_key: True/False در لاگ‌های فنی هست

اگر توسعه‌دهنده‌ای خواست کلید را دیباگ کند، باید آن را از لاگ‌ها حذف کند

۶. کارهای باقی‌مانده (TODO)
گام ۱۲ — بسته‌بندی (اولویت بالا)
□ flet pack app.py --name BookAnalyzer --onedir --icon assets/icon.ico
□ تست روی ماشین بدون Python
□ حل مشکل GTK برای PDF (نصب GTK در Inno Setup، یا مهاجرت به Playwright)
□ ساخت اسکریپت Inno Setup (installer/BookAnalyzer_x64.iss)
□ خروجی ARM64
□ تست نصب روی ماشین دیگر
□ Uninstaller
راهنمای دقیق: در docs/DEVELOPER_GUIDE.md و سند جداگانه‌ی HANDOFF در بحث با کاربر آمده.

بهبودهای اختیاری (نسخه ۱.x)
□ پاراگراف‌بندی هوشمند کتاب (chunking) برای کتاب‌های بزرگ
□ اجرای موازی چند مدل + داوری بین نتایج
□ export به XLIFF (برای CAT tools)
□ کش کردن نتایج crawl (برای صرفه‌جویی در زمان)
□ نمایش هزینه تخمینی قبل از تحلیل
□ حالت روشن/تاریک toggle در UI
□ کلید میانبر (Ctrl+S برای ذخیره)
□ Undo/Redo در فرم
پاکسازی
□ حذف test_*.py از ریشه (یا انتقال به tests/manual/)
□ حذف diag.py, seed_test.py, check_db.py, clean_test.py
□ حذف generate_docs.py (بعد از یک‌بار استفاده)
□ حذف docs/ فایل‌های placeholder قدیمی
تست خودکار
□ افزودن pytest و تست‌های واحد
□ CI با GitHub Actions
۷. مسائل شناخته‌شده (Known Issues)
#	مسئله	شدت	راه‌حل موقت
۱	مدل‌های رایگان OpenRouter مرتب تغییر می‌کنند	متوسط	تست اتصال چندمدلی + جایگزینی دستی در providers/openrouter.py
۲	کیفیت ترجمه اسامی خاص با مدل‌های کوچک پایین است	کم	مدل قوی‌تر انتخاب کنید
۳	فایل PDF روی ویندوز بدون GTK ساخته نمی‌شود	بالا (فقط کاربر نهایی)	نصب GTK در Inno Setup
۴	heuristically استخراج متن از برخی سایت‌ها (403)	کم	سایت دیگر امتحان کنید
۵	پاسخ LLM گاهی JSON غیرمعتبر می‌دهد	متوسط	_extract_json خودکار حل می‌کند
۶	rate-limit روی مدل‌های رایگان	متوسط	Fallback دستی به مدل دیگر
۸. وابستگی‌های کلیدی و نسخه‌ها
فایل requirements.txt:

text
flet==0.24.1
python-dotenv==1.0.1
httpx==0.27.2
beautifulsoup4==4.12.3
lxml==5.3.0
ddgs          # نسخه پایدار
openai==1.54.3
google-generativeai==0.8.3
pydantic>=2.12,<3
weasyprint==63.0
markdown==3.7
pyperclip==1.11.0
نکات مهم:

ddgs جایگزین duckduckgo-search شده (نسخه‌های قدیمی به Rust نیاز دارند)

pydantic>=2.12 برای Python 3.14، ولی توصیه Python 3.12

weasyprint روی ویندوز به GTK نیاز دارد

۹. چطور یک Provider جدید اضافه کنیم
مثال: افزودن Groq

۱. فایل providers/groq.py:

python
from providers._openai_compatible import OpenAICompatibleProvider


class GroqProvider(OpenAICompatibleProvider):
    name = "groq"
    label = "Groq"
    base_url = "https://api.groq.com/openai/v1"
    env_key = "GROQ_API_KEY"
    default_models = [
        "llama-3.3-70b-versatile",
        "mixtral-8x7b-32768",
    ]
۲. providers/registry.py:

python
from providers.groq import GroqProvider

BUILTIN = {
    ...
    GroqProvider.name: GroqProvider,
}
۳. .env:

env
GROQ_API_KEY=gsk_...
۴. برنامه را ری‌استارت کنید. Groq در لیست ظاهر می‌شود.

۱۰. چطور بخش جدیدی به تحلیل اضافه کنیم
مثال: افزودن «شخصیت‌های اصلی»

۱. core/schemas.py — افزودن فیلد:

python
class Character(BaseModel):
    name: Bilingual
    role: Bilingual
    description: Bilingual

class Analysis(BaseModel):
    ...
    characters: list[Character] = Field(default_factory=list)
۲. core/prompts/analysis.txt — توضیح در پرامپت:

text
Also identify the main characters and their roles.
Each character should have: name, role, description.
۳. ui/components/result_view.py — نمایش:

python
chars = analysis.get("characters", [])
if chars:
    blocks.append(_section_header("👥", "شخصیت‌ها"))
    for c in chars:
        blocks.append(ft.Text(f"• {pick(c.get('name'), 'fa')} — {pick(c.get('role'), 'fa')}"))
۴. exporters/to_md.py — افزودن به گزارش.

۱۱. مسیر پیشرفت توصیه‌شده
اگر می‌خواهید پروژه را ادامه دهید، این ترتیب را توصیه می‌کنم:

گام ۱۲ (بسته‌بندی) — تا کاربر نهایی بتواند استفاده کند

پاکسازی test_*.py — قبل از انتشار در GitHub

افزودن pytest — پایداری بلندمدت

چند Provider بیشتر (Groq, Together) — اگر کاربر نیاز دارد

Chunking هوشمند — اگر با کتاب‌های بزرگ کار می‌کنید

نسخه وب — اگر می‌خواهید به چند کاربر سرویس بدهید

۱۲. تماس و منابع
مستندات مرتبط
docs/ARCHITECTURE.md — معماری تفصیلی

docs/DEVELOPER_GUIDE.md — راه‌اندازی و توسعه

docs/USER_GUIDE.md — راهنمای کاربر

docs/TESTING_GUIDE.md — تست‌ها

docs/TROUBLESHOOTING.md — مشکلات رایج

docs/ROADMAP.md — نقشه راه

docs/CHANGELOG.md — تاریخچه تغییرات

docs/HANDOFF_PROVIDERS.md — چارچوب Provider (قابل استفاده مجدد در پروژه‌های دیگر)
- **`docs/HANDOFF_ABOUT_DIALOG.md`** — چارچوب دیالوگ About (قابل استفاده مجدد در پروژه‌های دیگر)

مخزن کد
GitHub: <آدرس مخزن> (پس از انتشار در گام ۱۲)

تکنولوژی‌های کلیدی — لینک مستندات
Flet: https://flet.dev/docs/

Pydantic v2: https://docs.pydantic.dev/latest/

WeasyPrint: https://doc.courtbouillon.org/weasyprint/

DuckDuckGo Search (ddgs): https://pypi.org/project/ddgs/

OpenRouter: https://openrouter.ai/docs

۱۳. چند نکته برای تحویل‌گیرنده
آنچه باید در اولین روز بدانید
قبل از هر تغییر، یک شاخه جدید در Git بسازید.

قبل از اجرای هر تحلیلی، .env را چک کنید.

برای تست سریع، python app.py و یک پروژه ساده.

اگر همه چیز خراب شد، data/projects.db را از یک نسخه پشتیبان برگردانید.

هیچ‌گاه api_key واقعی را در GitHub push نکنید.

کارهایی که نباید بکنید
❌ Provider builtin را حذف نکنید (کلیدهای خارجی وابسته‌اند)

❌ Schema دیتابیس را بدون migration تغییر ندهید

❌ فایل .env را در git commit نکنید

❌ api_key را در لاگ چاپ نکنید

❌ نام Provider را بعد از انتشار عوض نکنید

اگر می‌خواهید چیزی را حذف کنید
قبل از حذف هر کد یا فایل، این سؤال‌ها را بپرسید:

آیا در مستندات به آن ارجاع داده شده؟

آیا در DB یا output/ چیزی به آن وابسته است؟

آیا در providerهای builtin استفاده می‌شود؟

آیا در .env.example ذکر شده؟

اگر می‌خواهید چیزی اضافه کنید
ابتدا در docs/ROADMAP.md ثبت کنید

Schema را در core/schemas.py تعریف کنید (با Bilingual)

پرامپت را در core/prompts/analysis.txt توضیح دهید

UI را در ui/components/result_view.py نمایش دهید

Export را در exporters/ اعمال کنید

تست کنید

در docs/CHANGELOG.md ثبت کنید

۱۴. اطلاعات کاربر اصلی
نام: (در زمان تحویل تکمیل شود)
نقش: مترجم/ویراستار حرفه‌ای
نیاز اصلی: تحلیل سریع کتاب‌های انگلیسی قبل از ترجمه به فارسی
Provider پیش‌فرض: OpenRouter (رایگان)
زبان رابط کاربری: فارسی RTL
تم مورد علاقه: تاریک با رنگ زیتونی

۱۵. امضای تحویل
نقش	نام	تاریخ	امضا
توسعه‌دهنده اولیه	—	۱۴۰۴	—
تحویل‌گیرنده	—	—	—
تأییدکننده	—	—	—
پایان سند HANDOFF

هر سؤالی داشتید، ابتدا مستندات مرتبط را ببینید. اگر پاسخ نبود، در GitHub Issues مطرح کنید.

text

---

## 🎉 تمام ۸ سند مستندات آماده شد

حالا در پوشه `docs/` باید این ۹ فایل را ببینید:
docs/
├── ARCHITECTURE.md
├── CHANGELOG.md
├── DEVELOPER_GUIDE.md
├── USER_GUIDE.md
├── ROADMAP.md
├── TESTING_GUIDE.md
├── TROUBLESHOOTING.md
├── HANDOFF.md
└── HANDOFF_PROVIDERS.md ← که قبلاً ساختید