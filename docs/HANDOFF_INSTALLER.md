# HANDOFF — ساخت Installer با Inno Setup

> **هدف این سند:** یک چارچوب قابل استفاده مجدد برای ساخت installer حرفه‌ای برای هر برنامه دسکتاپ پایتون/Flet.
>
> **مبنا:** پروژه Book Analyzer.

---

## ۱. پیش‌نیازها

- **Python 3.12** با `flet` و `pyinstaller`
- **Inno Setup 6.3+** — از [jrsoftware.org/isdl.php](https://jrsoftware.org/isdl.php)
- **خروجی `flet pack`** — پوشه `dist/BookAnalyzer/` باید آماده باشد

---

## ۲. ساختار پوشه‌ها

```text
project/
├── dist/
│   └── BookAnalyzer/               ← خروجی flet pack
│       ├── BookAnalyzer.exe
│       └── _internal/
├── installer/
│   ├── BookAnalyzer_x64.iss        ← اسکریپت Inno Setup
│   └── Output/                     ← خروجی installer
│       └── BookAnalyzer_Setup_x64_v1.1.0.exe
├── assets/
│   └── icon.ico                    ← آیکن برنامه
├── LICENSE                         ← متن مجوز
└── build_release.ps1               ← اسکریپت build خودکار
```

---

## ۳. اسکریپت Inno Setup (`.iss`)

فایل `installer/BookAnalyzer_x64.iss`:

```iss
; Book Analyzer - Inno Setup Script
#define MyAppName "Book Analyzer"
#define MyAppVersion "1.1.0"
#define MyAppPublisher "Mahmoud Aharpour Feiznia"
#define MyAppURL "https://yadoto.ir"
#define MyAppExeName "BookAnalyzer.exe"

[Setup]
AppId={{B8A3F1D2-4E5C-4A9B-8F7E-1C2D3E4F5A6B}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
LicenseFile=..\LICENSE
OutputDir=Output
OutputBaseFilename=BookAnalyzer_Setup_x64_v{#MyAppVersion}
SetupIconFile=..\assets\icon.ico
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
MinVersion=10.0.17763
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
UninstallDisplayIcon={app}\{#MyAppExeName}
UninstallDisplayName={#MyAppName}
CloseApplications=yes
RestartApplications=yes
CloseApplicationsFilter=*.exe,*.dll

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "..\dist\BookAnalyzer\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs; Excludes: "data\*.db,data\settings.json,.env,output\*"

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#MyAppName}}"; Flags: nowait postinstall skipifsilent
```

---

## ۴. توضیح بخش‌های کلیدی

### `AppId`
یک **GUID یکتا**. برای GUID جدید: `Tools → Generate GUID` در Inno Setup IDE.

### `ArchitecturesAllowed=x64compatible`
اجازه می‌دهد installer روی ویندوز x64 **و** ARM64 (با شبیه‌سازی) اجرا شود.

### `PrivilegesRequired=lowest` + `PrivilegesRequiredOverridesAllowed=dialog`
به کاربر اجازه می‌دهد بین نصب سراسری (نیاز به ادمین) یا نصب فقط برای کاربر جاری انتخاب کند.

### `Excludes: "data\*.db,data\settings.json,.env,output\*"`
فایل‌های حساس (دیتابیس، کلیدها، خروجی‌ها) در installer قرار نمی‌گیرند. کاربر جدید با دیتابیس خالی شروع می‌کند.

### `MinVersion=10.0.17763`
حداقل نسخه ویندوز: ویندوز ۱۰ نسخه ۱۸۰۹ یا بالاتر.

---

## ۵. کامپایل

```powershell
cd installer
iscc BookAnalyzer_x64.iss
```

خروجی: `installer/Output/BookAnalyzer_Setup_x64_v1.1.0.exe`

---

## ۶. نسخه ARM64 (اختیاری)

برای ساخت installer ARM64، یک کپی با این تغییرات:

```iss
ArchitecturesAllowed=arm64
ArchitecturesInstallIn64BitMode=arm64
OutputBaseFilename=BookAnalyzer_Setup_arm64_v{#MyAppVersion}
```

**نکته:** `flet pack` هنوز از ARM64 پشتیبانی رسمی نمی‌کند. باید از `flet build` استفاده کنید یا منتظر نسخه‌های بعدی بمانید.

---

## ۷. تست Installer

روی یک **ماشین بدون Python**:

| # | تست | انتظار |
|---|---|---|
| ۱ | اجرای installer | باز شدن wizard |
| ۲ | صفحه License | نمایش متن MIT |
| ۳ | انتخاب مسیر | `C:\Program Files\Book Analyzer` |
| ۴ | Shortcut روی Desktop | ساخته شود (اختیاری) |
| ۵ | منوی Start | دو آیتم: برنامه و Uninstall |
| ۶ | اجرای برنامه | باز شدن UI |
| ۷ | تنظیم Provider | وارد کردن کلید API در UI |
| ۸ | یک تحلیل کوچک | موفق، خروجی در `output/` |
| ۹ | Uninstall | پاک کردن کامل، بدون باقی‌مانده |

---

## ۸. عیب‌یابی

| خطا | علت | راه‌حل |
|---|---|---|
| `LicenseFile not found` | مسیر نسبی اشتباه | از `..\LICENSE` استفاده کنید |
| `SetupIconFile not found` | فایل ico نیست | `..\assets\icon.ico` را چک کنید |
| `The process cannot access the file` | برنامه باز است | `CloseApplications=yes` را فعال کنید |
| `ArchitecturesAllowed` خطا | Inno Setup قدیمی | نسخه ۶.۳+ نصب کنید |
| فایل DB در installer | Excludes اشتباه | `Excludes: "data\*.db,.env,output\*"` |

---

## ۹. انتشار

بعد از تست موفق:

1. `BookAnalyzer_Setup_x64_v1.1.0.exe` را در GitHub Releases آپلود کنید.
2. در README لینک دانلود را بگذارید.
3. در CHANGELOG ثبت کنید.

---

## ۱۰. اسکریپت build خودکار

فایل `build_release.ps1` که build و cleanup را یک‌جا انجام می‌دهد:

```powershell
# build_release.ps1
$ErrorActionPreference = "Stop"

Write-Host "Cleaning previous build..." -ForegroundColor Cyan

Get-Process BookAnalyzer -ErrorAction SilentlyContinue | Stop-Process -Force
Start-Sleep -Seconds 2

Remove-Item -Recurse -Force dist -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force build -ErrorAction SilentlyContinue
Remove-Item -Force BookAnalyzer.spec -ErrorAction SilentlyContinue

Write-Host "Building with flet pack..." -ForegroundColor Cyan

flet pack app.py `
  --name BookAnalyzer `
  --onedir `
  --icon assets\icon.ico `
  --add-data "assets;assets" `
  --add-data "core\prompts;core\prompts" `
  --hidden-import certifi `
  --hidden-import openai `
  --hidden-import google.generativeai `
  --hidden-import weasyprint `
  --hidden-import ddgs `
  --hidden-import pyperclip `
  --hidden-import markdown `
  --hidden-import lxml `
  --hidden-import bs4 `
  --hidden-import pydantic `
  --hidden-import httpx `
  --hidden-import dotenv `
  --product-name "Book Analyzer" `
  --file-description "Smart Book Analyzer for Translators" `
  --product-version "1.1.0" `
  --file-version "1.1.0.0" `
  --company-name "Mahmoud Aharpour Feiznia" `
  --copyright "Copyright (c) 2026 Mahmoud Aharpour Feiznia"

Write-Host "Cleaning user-specific data from dist..." -ForegroundColor Cyan

Remove-Item -Force "dist\BookAnalyzer\data\projects.db" -ErrorAction SilentlyContinue
Remove-Item -Force "dist\BookAnalyzer\data\settings.json" -ErrorAction SilentlyContinue
Remove-Item -Force "dist\BookAnalyzer\.env" -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force "dist\BookAnalyzer\output\*" -ErrorAction SilentlyContinue

New-Item -ItemType File -Path "dist\BookAnalyzer\data\.gitkeep" -Force | Out-Null
New-Item -ItemType File -Path "dist\BookAnalyzer\output\.gitkeep" -Force | Out-Null

Write-Host ""
Write-Host "Build complete and clean!" -ForegroundColor Green
Write-Host "Dist folder: dist\BookAnalyzer\" -ForegroundColor Green
Write-Host "Ready to distribute or package with Inno Setup." -ForegroundColor Green
```

**نکات مهم:**

- **بدون ایموجی** — PowerShell با ایموجی در فایل `.ps1` مشکل دارد
- **حذف `data/settings.json`** — جلوی لو رفتن تنظیمات کاربر را می‌گیرد
- **`--hidden-import`** برای هر پکیج خارجی

---

## ۱۱. خلاصه تصمیمات کلیدی

| تصمیم | دلیل |
|---|---|
| `--onedir` (نه `--onefile`) | سرعت بیشتر راه‌اندازی |
| `flet pack` (نه PyInstaller خام) | مدیریت خودکار Flet client |
| `PrivilegesRequired=lowest` | کاربر بدون ادمین هم نصب کند |
| `Excludes` برای DB و output | لو نرفتن داده‌های توسعه‌دهنده |
| نسخه بدون ایموجی در `.ps1` | جلوگیری از خطای parser |
| `build_release.ps1` جداگانه | خودکارسازی build + cleanup |

---

**پایان سند HANDOFF_INSTALLER**