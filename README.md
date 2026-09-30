# Book Analyzer

تحلیل‌گر هوشمند کتاب برای مترجمان — انگلیسی → فارسی

![نسخه](https://img.shields.io/badge/version-1.0.0-9CAF3F)
![پایتون](https://img.shields.io/badge/python-3.12-blue)
![مجوز](https://img.shields.io/badge/license-MIT-green)

![صفحه اصلی](docs/screenshots/main.png)

---

## معرفی

**Book Analyzer** یک برنامه دسکتاپ تک‌کاربره برای مترجمان و ویراستاران حرفه‌ای است که با گرفتن عنوان، نویسنده، چند لینک و بخشی از متن یک کتاب، تحلیلی چهارمحوری از آن تولید می‌کند:

- 📖 **ژانر** — اصلی و زیرژانر
- 🎭 **لحن** — با نمونه‌های نقل‌قول واقعی
- ✍️ **سبک نویسنده** — جمله، راوی، واژگان، ویژگی‌ها
- 🌐 **نکات ترجمه** — چالش‌ها و راهبردهای انگلیسی → فارسی

و سه خروجی می‌دهد:

| خروجی | زبان | کاربرد |
|---|---|---|
| `analysis.json` | انگلیسی | import در سیستم‌های واژه‌نامه‌ساز و مترجم LLM |
| `report.md` | فارسی | ویرایش و اشتراک‌گذاری |
| `report.pdf` | فارسی | ارائه به ویراستار یا چاپ |

علاوه بر این، یک **پرامپت ترجمه آماده** بر اساس تحلیل تولید می‌شود.

---

## نصب

### نسخه نصبی (پیشنهادی)

از [Releases](https://github.com/mafeiznia/book-analyzer/releases) فایل `BookAnalyzer_Setup_x64_v1.0.0.exe` را دانلود و نصب کنید.

**پیش‌نیاز:** ویندوز ۱۰ نسخه ۱۸۰۹ یا بالاتر (x64).

### نسخه توسعه (Python)

```powershell
git clone https://github.com/mafeiznia/book-analyzer.git
cd book-analyzer
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
python app.py
اولین اجرا
به تنظیمات (آیکن چرخ‌دنده) بروید.

یک Provider را انتخاب و کلید API آن را وارد کنید. پیشنهاد: Groq (رایگان، سریع).

روی «تست اتصال» بزنید.

روی «فعال‌سازی» بزنید.

یک پروژه جدید بسازید و فیلدها را پر کنید.

روی «شروع تحلیل» بزنید.

راهنمای کامل: docs/USER_GUIDE.md

Providerهای پشتیبانی‌شده
Provider	کلید رایگان	پایداری	سرعت
Groq	✅	⭐⭐⭐⭐⭐	بسیار سریع
OpenRouter	✅ (محدود)	⭐⭐	متوسط
OpenAI	❌ (پول‌دار)	⭐⭐⭐⭐⭐	متوسط
Google Gemini	✅	⭐⭐⭐⭐	متوسط
DeepSeek	❌	⭐⭐⭐⭐	متوسط
GLM (Zhipu)	❌	⭐⭐⭐	متوسط
توصیه: برای شروع، Groq را انتخاب کنید (رایگان و پایدار).
راهنما: console.groq.com/keys

ویژگی‌های کلیدی
🎨 رابط کاربری فارسی RTL با تم تاریک و رنگ زیتونی

🔌 Providerهای چندگانه با امکان افزودن Provider سفارشی

🌐 جست‌وجوی خودکار با DuckDuckGo اگر لینک‌های کاربر کافی نباشند

📋 لاگ زنده با سطح ساده/فنی

📦 نسخه‌بندی تحلیل‌ها (v1, v2, ...) — نسخه‌های قبلی حفظ می‌شوند

🎯 انتخاب مدل per-project

⛔ لغو تحلیل در حین کار

🔐 مدیریت امن کلیدها (پایگاه داده یا .env)

ساختار پروژه
text
book-analyzer/
├── app.py                # نقطه ورود
├── ui/                   # رابط کاربری Flet
├── core/                 # منطق تحلیل
├── providers/            # لایه Providerها
├── storage/              # SQLite + migrations
├── exporters/            # خروجی JSON/MD/PDF
├── services/             # LogBus
├── assets/               # فونت و لوگو
├── docs/                 # مستندات
├── installer/            # Inno Setup
└── test/                 # تست‌های دستی
مستندات
سند	موضوع
docs/ARCHITECTURE.md	معماری کامل
docs/USER_GUIDE.md	راهنمای کاربر
docs/DEVELOPER_GUIDE.md	راه‌اندازی و توسعه
docs/ROADMAP.md	نقشه راه
docs/CHANGELOG.md	تاریخچه تغییرات
docs/TESTING_GUIDE.md	تست‌ها
docs/TROUBLESHOOTING.md	عیب‌یابی
docs/HANDOFF.md	تحویل پروژه
docs/HANDOFF_PROVIDERS.md	چارچوب Provider (قابل استفاده مجدد)
docs/HANDOFF_ABOUT_DIALOG.md	چارچوب About (قابل استفاده مجدد)
docs/HANDOFF_INSTALLER.md	چارچوب Installer (قابل استفاده مجدد)
توسعه
powershell
# build خودکار + پاکسازی نسخه توزیعی
.\build_release.ps1

# ساخت Installer
cd installer
iscc BookAnalyzer_x64.iss
راهنمای کامل: docs/DEVELOPER_GUIDE.md

محدودیت‌های شناخته‌شده
اسکرول صفحه با چرخ ماوس «تکه‌تکه» است (محدودیت Flet 0.24 روی ویندوز دسکتاپ)

مدل‌های رایگان OpenRouter ناپایدار هستند (راه‌حل: Groq یا شارژ OpenRouter)

مجوز
MIT License — © 2026 Mahmoud Aharpour Feiznia

ارتباط
🌐 وب‌سایت: yadoto.ir
📧 ایمیل: ma.feiznia@gmail.com
💼 LinkedIn: Mahmoud Aharpour Feiznia