# HANDOFF — مهاجرت به Flet 1.0

> **هدف:** راهنمای کامل برای مهاجرت پروژه Book Analyzer از Flet 0.24.1 به Flet 1.0.
>
> **وضعیت فعلی:** نسخه `1.0.0` با Flet `0.24.1` منتشر شده و پایدار است.
>
> **وضعیت هدف:** نسخه `2.0.0` با Flet `1.x` — بدون شکستن قابلیت‌ها.

---

## ۱. اطلاعات زمینه‌ای (Context for New Chat)

### وضعیت پروژه

- **مسیر پروژه:** `C:\projects\Translation\Book-analyzer`
- **GitHub:** [github.com/mafeiznia/book-analyzer](https://github.com/mafeiznia/book-analyzer)
- **نسخه فعلی:** `1.0.0` (منتشرشده)
- **تگ فعلی:** `v1.0.0` در GitHub
- **آخرین commit:** `77e83f1` (workflow GitHub Actions)
- **تعداد فایل‌ها:** ۷۹+
- **Python:** 3.12 (`.venv`)
- **Flet:** 0.24.1 (تثبیت‌شده)
- **سیستم‌عامل توسعه:** ویندوز x64

### کاربر

- مترجم/ویراستار حرفه‌ای
- فارسی‌زبان (RTL)
- انتظار: رفتار گام‌به‌گام، تأیید در هر اقدام

### سبک کار مورد انتظار

- **یک اقدام در هر پیام** — منتظر تأیید بمان
- **بدون if/then یا چند گزینه همزمان** — فقط یک مسیر مشخص
- **پاسخ‌ها فارسی** — ولی کد و نام فایل انگلیسی
- **هر پیام کوتاه** — نه چند تغییر با هم

---

## ۲. ساختار پروژه فعلی

```text
Book-analyzer/
├── .github/
│   └── workflows/
│       └── build.yml              ← workflow ساخت خودکار
├── app.py                          ← نقطه ورود (ft.app)
├── requirements.txt                ← flet==0.24.1
├── build_release.ps1               ← build خودکار + cleanup
├── LICENSE                         ← MIT
├── README.md                       ← با RTL wrapper
├── check_md.py                     ← ابزار بررسی Markdown
├── .env                            ← کلیدها (gitignore شده)
├── .env.example                    ← نمونه
├── .gitignore
├── assets/
│   ├── fonts/                      ← Vazirmatn (.ttf + .woff2)
│   ├── icon.ico
│   └── logo.png
├── core/
│   ├── about_info.py
│   ├── analyzer.py                 ← analyze_book() — async
│   ├── bilingual.py
│   ├── collector.py                ← async
│   ├── crawler.py                  ← async (httpx)
│   ├── prompt_builder.py
│   ├── schemas.py                  ← Pydantic v2
│   ├── search.py                   ← async
│   ├── settings.py
│   └── prompts/
│       ├── analysis.txt
│       └── translation.txt
├── providers/
│   ├── _openai_compatible.py       ← async (AsyncOpenAI)
│   ├── base.py
│   ├── custom.py
│   ├── deepseek.py
│   ├── gemini.py                   ← asyncio.to_thread
│   ├── glm.py
│   ├── groq.py
│   ├── manager.py
│   ├── openai.py
│   ├── openrouter.py
│   └── registry.py
├── storage/
│   ├── db.py                       ← sys.frozen aware
│   ├── migrations.py
│   ├── models.py
│   └── repositories.py
├── exporters/
│   ├── to_json.py                  ← sys.frozen aware
│   ├── to_md.py
│   └── to_pdf.py                   ← WeasyPrint
├── services/
│   └── log_bus.py                  ← LogBus (publish-subscribe)
├── ui/
│   ├── theme.py                    ← OLIVE_PRIMARY
│   ├── pages/
│   │   ├── projects_list.py
│   │   ├── project_view.py         ← بزرگ‌ترین فایل (~۶۰۰ خط)
│   │   └── settings.py
│   └── components/
│       ├── log_panel.py
│       ├── result_view.py
│       └── about_dialog.py
├── installer/
│   ├── BookAnalyzer_x64.iss
│   └── Output/
├── docs/
│   ├── ARCHITECTURE.md
│   ├── CHANGELOG.md
│   ├── DEVELOPER_GUIDE.md
│   ├── HANDOFF.md
│   ├── HANDOFF_ABOUT_DIALOG.md
│   ├── HANDOFF_INSTALLER.md
│   ├── HANDOFF_PROVIDERS.md
│   ├── ROADMAP.md
│   ├── TESTING_GUIDE.md
│   ├── TROUBLESHOOTING.md
│   └── USER_GUIDE.md
├── test/                            ← تست‌های دستی
└── data/
    └── projects.db                  ← SQLite (gitignore شده)
```

---

## ۳. قابلیت‌های فعلی (که باید حفظ شوند)

1. **مدیریت پروژه‌ها** — CRUD + جست‌وجو + حذف
2. **تحلیل LLM دوزبانه** — ژانر، لحن، سبک، نکات ترجمه
3. **سه خروجی** — JSON (EN) + MD (FA) + PDF (FA)
4. **پرامپت ترجمه** — تولید خودکار
5. **۶ Provider builtin** — Groq, OpenRouter, OpenAI, Gemini, DeepSeek, GLM
6. **Provider سفارشی** — افزودن از UI
7. **ویرایش Provider** — کلید API + مدل‌ها
8. **انتخاب مدل per-project**
9. **لغو تحلیل + زمان‌سنج**
10. **لاگ زنده** + toggle ساده/فنی + کپی
11. **تم روشن/تاریک** با toggle + ذخیره در `data/settings.json`
12. **About** با لوگو، نویسنده، تکنولوژی‌ها
13. **نسخه‌بندی تحلیل‌ها** (v1, v2, ...)
14. **RTL فارسی** با Vazirmatn
15. **بسته‌بندی** با `flet pack` + Inno Setup
16. **Workflow GitHub Actions** — ساخت خودکار

---

## ۴. APIهای Flet 0.24 که استفاده می‌کنیم (برای مهاجرت)

| API فعلی (0.24) | جایگزین (1.0) | فایل‌ها |
|---|---|---|
| `ft.app(target=main)` | `ft.run(main)` | `app.py` |
| `ft.ElevatedButton` | `ft.Button` | همه pages |
| `ft.IconButton` | (بررسی) | همه pages |
| `page.window.width` | (بررسی) | `app.py` |
| `page.overlay.append(dlg)` | (بررسی) | `settings.py`, `projects_list.py` |
| `page.open(dlg)` | (بررسی) | همه pages |
| `page.run_task(fn, ...)` | (بررسی) | `project_view.py` |
| `ft.colors.X` | `ft.Colors.X` | همه جا |
| `ft.icons.X` | `ft.Icons.X` | همه جا |
| `ft.padding.X` | (بررسی) | همه جا |
| `ft.AlertDialog` | (بررسی) | `settings.py`, `about_dialog.py` |
| `ft.TextField` | (بررسی) | همه فرم‌ها |
| `ft.Dropdown` | (بررسی) | `project_view.py` |
| `ft.SnackBar` | (بررسی) | همه |
| `ft.ListView` | (بررسی) | pages |

**نکته:** جدول بالا تقریبی است. باید مستندات رسمی Flet 1.0 را خواند و به‌روز کرد.

---

## ۵. خطرات و مشکلات شناخته‌شده

### خطر ۱ — مدل تک‌رشته‌ای
در Flet 1.0، کدهای sync مسدودکننده کل UI را فریز می‌کنند. **اکثر کد ما async است، ولی باید بررسی شود:**
- `LogBus.emit()` — احتمالاً sync (فوری، مشکل کم)
- `storage/repositories.py` — sync (SQLite)
- `exporters/*.py` — sync (file I/O)
- `providers/gemini.py` — از `asyncio.to_thread` استفاده می‌کند (خوب)

### خطر ۲ — `ft.FilePicker` به service تبدیل شده
ما در `project_view.py` از FilePicker استفاده می‌کردیم (که بعداً حذف شد). بررسی شود.

### خطر ۳ — تغییرات در `LogBus`
`LogBus` به `page.update()` از thread های مختلف وابسته است. در مدل تک‌رشته‌ای، باید بررسی شود.

### خطر ۴ — `page.window.*`
API پنجره در Flet 1.0 تغییر کرده. بررسی شود.

### خطر ۵ — PDF با WeasyPrint
مستقل از Flet است، ولی باید بعد از مهاجرت تست شود.

### خطر ۶ — مدل رایگان OpenRouter
ناپایدار است. الان از **Groq** استفاده می‌کنیم که پایدار است.

---

## ۶. نقشه مهاجرت

### مرحله ۱ — شاخه جدید Git

```powershell
git checkout -b flet-1.0-migration
```

**مهم:** در شاخه جداگانه کار کنیم، نه در `main`. تا اگر شکست خورد، بازگشت آسان باشد.

### مرحله ۲ — ارتقاء به Flet 0.28.3 (پل)

```powershell
pip install flet==0.28.3
python app.py
```

**هدف:** رفع هشدارهای deprecation. هر هشدار = یک API که در 1.0 حذف می‌شود.

**اجرا با هشدارها:**
```powershell
python -W default::DeprecationWarning app.py
```

### مرحله ۳ — مستندات Flet 1.0

خواندن:
- [Flet 1.0 migration guide](https://docs.flet.dev/migration-guide/)
- [Flet changelog](https://github.com/flet-dev/flet/releases)
- [Flet examples](https://github.com/flet-dev/examples)

### مرحله ۴ — مهاجرت به Flet 1.0

```powershell
pip install 'flet[all]' --upgrade
```

سپس به ترتیب:
1. `app.py` — `ft.app` → `ft.run`
2. `ft.colors` → `ft.Colors`, `ft.icons` → `ft.Icons`
3. `ft.ElevatedButton` → `ft.Button`
4. کدهای sync مسدودکننده → async
5. `FilePicker` (اگر جایی مانده) → service
6. تست کامل

### مرحله ۵ — تست کامل

| تست | انتظار |
|---|---|
| باز شدن برنامه | ✅ |
| ظاهر (تم، فونت، RTL) | ✅ |
| Providerها | ✅ |
| تست اتصال Groq | ✅ |
| تحلیل کامل | ✅ |
| خروجی JSON/MD/PDF | ✅ |
| About | ✅ |
| تم toggle | ✅ |
| لاگ + کپی | ✅ |
| لغو + زمان‌سنج | ✅ |
| انتخاب مدل | ✅ |

### مرحله ۶ — Merge و انتشار

```powershell
git checkout main
git merge flet-1.0-migration
# ارتقاء نسخه به 2.0.0 در core/about_info.py
# بروزرسانی CHANGELOG
git tag -a v2.0.0 -m "Release 2.0.0 — Flet 1.0 migration"
git push origin main
git push origin v2.0.0
gh release create v2.0.0 ...
```

---

## ۷. دستورات پرکاربرد

### فعال‌سازی venv
```powershell
.\.venv\Scripts\Activate.ps1
```

### اجرای برنامه
```powershell
python app.py
```

### بررسی Markdown
```powershell
python check_md.py
```

### build کامل
```powershell
.\build_release.ps1
```

### ساخت installer
```powershell
cd installer
iscc BookAnalyzer_x64.iss
cd ..
```

### commit + push
```powershell
git add .
git commit -m "message"
git push
```

### بررسی وضعیت
```powershell
git status
git log --oneline -10
```

---

## ۸. منابع رسمی

- **Flet docs:** [docs.flet.dev](https://docs.flet.dev)
- **Flet GitHub:** [github.com/flet-dev/flet](https://github.com/flet-dev/flet)
- **Flet migration guide:** [docs.flet.dev/migration-guide](https://docs.flet.dev/migration-guide/)
- **Flet Discord:** [discord.gg/dzWXP8SHG8](https://discord.gg/dzWXP8SHG8)
- **نمونه‌های workflow:** [github.com/flet-dev/flet-github-action-workflows](https://github.com/flet-dev/flet-github-action-workflows)

---

## ۹. دستور شروع چت جدید

**برای شروع مهاجرت در چت جدید، این متن را در ابتدا پیست کنید:**

```
می‌خواهم پروژه Book Analyzer را از Flet 0.24.1 به Flet 1.0 مهاجرت دهم.

سند HANDOFF کامل در docs/HANDOFF_FLET_MIGRATION.md در پروژه‌ام هست.
پروژه در C:\projects\Translation\Book-analyzer است.
GitHub: github.com/mafeiznia/book-analyzer

خواهش می‌کنم:
1. ابتدا سند HANDOFF را بخوان
2. سپس گام‌به‌گام و با تأیید من پیش برو
3. یک اقدام در هر پیام (بدون if/then یا چند گزینه)
4. پاسخ‌ها فارسی

شروع کن با:
- بررسی وضعیت فعلی پروژه
- تأیید نسخه Flet فعلی
- پیشنهاد مرحله بعد
```

---

## ۱۰. تعهدات سبک کار (تکرار مهم)

- **یک اقدام در هر پیام** — همیشه
- **منتظر تأیید** — بدون فرض
- **بدون if/then همزمان** — یک مسیر
- **بدون چند گزینه** — سؤال ساده، یک جواب
- **پاسخ‌ها فارسی**، کد انگلیسی
- **بدون طولانی‌نویسی** — کوتاه و دقیق

---

**پایان سند HANDOFF_FLET_MIGRATION**

هر کسی که این سند را بخواند، می‌تواند مهاجرت را از همین نقطه شروع کند.