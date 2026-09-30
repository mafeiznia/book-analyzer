# HANDOFF — سیستم Provider (Multi-LLM)

> **هدف این سند:** یک چارچوب قابل استفاده مجدد برای افزودن چند ارائه‌دهنده LLM (OpenAI, OpenRouter, Gemini, DeepSeek, GLM, سفارشی) به یک برنامه پایتون.
>
> **مبنا:** پروژه Book Analyzer (Flet + SQLite).
>
> **سازگاری:** Flet 0.24+، Python 3.12، pydantic v2.

---

## ۱. مسئله‌ای که حل می‌شود

کاربر می‌خواهد:
- بین چند Provider LLM سوییچ کند (OpenAI، OpenRouter، Gemini، DeepSeek، GLM، و هر سرویس سازگار با OpenAI)
- در هر زمان فقط **یک Provider فعال** باشد
- کلید API را یا در `.env` بگذارد یا مستقیماً از UI وارد کند
- مدل‌ها را ویرایش کند (کم/زیاد کند)
- Provider سفارشی اضافه کند بدون دست‌زدن به کد
- اتصال هر Provider را از UI تست کند (چند مدل، نه فقط یکی)

## ۲. معماری کلی

```
┌─────────────────────────────────────────────────────────┐
│  UI (settings.py)                                        │
│   - کارت هر Provider                                     │
│   - دیالوگ افزودن / ویرایش / حذف                         │
│   - دکمه «تست اتصال» + «فعال‌سازی»                       │
└──────────────────────┬──────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────┐
│  ProviderManager (providers/manager.py)                  │
│   - load()           بارگذاری از DB + .env               │
│   - get_active()     Provider فعال                       │
│   - list_providers() برای UI                             │
│   - add_custom() / update_provider() / remove_custom()  │
│   - set_active()                                         │
└──────────────────────┬──────────────────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        ▼              ▼              ▼
┌──────────────┐ ┌────────────┐ ┌──────────────┐
│  Registry    │ │  Builtin   │ │   Custom     │
│  BUILTIN={}  │ │  Providers │ │  Provider    │
└──────────────┘ └────────────┘ └──────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│  Base Classes                                            │
│   - LLMProvider (interface)                              │
│   - OpenAICompatibleProvider (shared impl)               │
└─────────────────────────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│  Storage (SQLite) — جدول providers                       │
└─────────────────────────────────────────────────────────┘
```

## ۳. ساختار فایل‌ها

```
providers/
├── __init__.py
├── base.py                    # interface + dataclasses
├── _openai_compatible.py      # کلاس پایه مشترک
├── openrouter.py              # پیاده‌سازی‌های builtin
├── openai.py
├── deepseek.py
├── glm.py
├── gemini.py                  # SDK متفاوت (google-generativeai)
├── custom.py                  # Provider ساخته‌شده توسط کاربر
├── registry.py                # ثبت builtinها
└── manager.py                 # مدیریت کامل
```

## ۴. اسکیمای دیتابیس

```sql
CREATE TABLE IF NOT EXISTS providers (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT UNIQUE NOT NULL,
    base_url    TEXT,
    env_key     TEXT,
    api_key     TEXT DEFAULT '',      -- از migration 001
    is_builtin  INTEGER DEFAULT 0,
    is_active   INTEGER DEFAULT 0,
    models      TEXT,                  -- JSON array
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**قواعد:**
- `name` یکتا (case-sensitive)
- فقط یک ردیف می‌تواند `is_active=1` باشد
- `models` همیشه JSON array از رشته‌ها
- `api_key` خالی یعنی «از `.env` بخوان»

## ۵. اولویت‌دهی کلید API

```python
db_key = (row["api_key"] or "").strip()
env_value = os.getenv(row["env_key"], "").strip() if row["env_key"] else ""
api_key = db_key if db_key else env_value
```

**منابع ممکن (`key_source`):**
| مقدار | معنی | بج UI |
|---|---|---|
| `db` | از پایگاه داده | 💾 پایگاه داده (سبز) |
| `env` | از فایل `.env` | 📄 .env (آبی) |
| `none` | هیچ‌کدام | ⚠️ تنظیم نشده (زرد) |

## ۶. Interface پایه (`providers/base.py`)

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class ConnectionTestResult:
    ok: bool
    message: str
    latency_ms: int = 0
    sample_model: str | None = None


@dataclass
class LLMResponse:
    text: str
    tokens_in: int
    tokens_out: int
    cost_usd: float
    model: str
    provider: str


class LLMProvider(ABC):
    """هر Provider باید این interface را پیاده کند."""
    name: str = ""
    label: str = ""
    base_url: str = ""
    env_key: str = ""
    default_models: list[str] = []
    is_builtin: bool = True

    def __init__(self, api_key="", base_url=None, models=None):
        self.api_key = api_key
        if base_url:
            self.base_url = base_url
        self.models = list(models) if models else list(self.default_models)

    @property
    def has_key(self) -> bool:
        return bool(self.api_key and self.api_key.strip())

    @abstractmethod
    async def test_connection(self) -> ConnectionTestResult: ...

    @abstractmethod
    async def ask(self, prompt: str, model: str,
                  max_tokens: int = 2000,
                  temperature: float = 0.2) -> LLMResponse: ...
```

## ۷. کلاس پایه مشترک (`providers/_openai_compatible.py`)

اکثر سرویس‌ها (OpenAI، OpenRouter، DeepSeek، GLM، Together، ...) از **OpenAI Chat Completions API** تبعیت می‌کنند. پس فقط یک کلاس پایه می‌نویسیم:

```python
import time
from openai import AsyncOpenAI
from providers.base import ConnectionTestResult, LLMProvider, LLMResponse


class OpenAICompatibleProvider(LLMProvider):
    """پایه مشترک برای هر endpoint سازگار OpenAI."""

    async def test_connection(self) -> ConnectionTestResult:
        if not self.has_key:
            return ConnectionTestResult(
                ok=False,
                message=f"کلید API تنظیم نشده است. متغیر {self.env_key} را در .env پر کنید.",
            )
        if not self.models:
            return ConnectionTestResult(ok=False, message="هیچ مدلی تعریف نشده.")

        client = AsyncOpenAI(api_key=self.api_key, base_url=self.base_url, timeout=20.0)
        working, failed = [], []

        for model in self.models[:8]:
            start = time.time()
            try:
                await client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": "ping"}],
                    max_tokens=5,
                )
                working.append((model, int((time.time() - start) * 1000)))
            except Exception as e:
                failed.append((model, f"{type(e).__name__}: {str(e)[:80]}"))

        if working:
            lines = [f"✅ {len(working)} از {len(self.models)} مدل کار می‌کند:"]
            for m, lat in working[:5]:
                lines.append(f"  • {m} — {lat}ms")
            first_model, first_latency = working[0]
            return ConnectionTestResult(
                ok=True, message="\n".join(lines),
                latency_ms=first_latency, sample_model=first_model,
            )
        else:
            lines = ["❌ هیچ مدلی پاسخ نداد."]
            for m, err in failed[:3]:
                lines.append(f"  • {m}\n    {err}")
            return ConnectionTestResult(ok=False, message="\n".join(lines))

    async def ask(self, prompt, model, max_tokens=2000, temperature=0.2):
        if not self.has_key:
            raise RuntimeError(f"کلید API برای {self.name} تنظیم نشده است.")

        client = AsyncOpenAI(api_key=self.api_key, base_url=self.base_url, timeout=120.0)
        resp = await client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=temperature,
        )
        text = resp.choices[0].message.content or ""
        usage = getattr(resp, "usage", None)
        return LLMResponse(
            text=text,
            tokens_in=getattr(usage, "prompt_tokens", 0) if usage else 0,
            tokens_out=getattr(usage, "completion_tokens", 0) if usage else 0,
            cost_usd=0.0,
            model=model,
            provider=self.name,
        )
```

**نکات مهم:**
- **تست چند مدلی:** به‌جای تست فقط مدل اول، همه مدل‌ها تست می‌شوند. این برای Providerهای رایگان (که مدل‌ها مرتب rate-limit می‌شوند) حیاتی است.
- **`max_tokens=5`** در تست → کمترین مصرف توکن.
- **Timeout تست: ۲۰s | Timeout ask: ۱۲۰s** (برای پاسخ‌های طولانی LLM).
- **`cost_usd`** اینجا صفر است. اگر قیمت‌گذاری لازم بود، باید یک جدول قیمت جدا اضافه شود.

## ۸. Providerهای Builtin

### الگوی ساده (سازگار OpenAI)

```python
# providers/openrouter.py
from providers._openai_compatible import OpenAICompatibleProvider


class OpenRouterProvider(OpenAICompatibleProvider):
    name = "openrouter"
    label = "OpenRouter"
    base_url = "https://openrouter.ai/api/v1"
    env_key = "OPENROUTER_API_KEY"
    default_models = [
        "google/gemini-2.0-flash-exp:free",
        "qwen/qwen-2.5-72b-instruct:free",
    ]
```

### الگوی پیچیده (SDK متفاوت — مثال Gemini)

```python
# providers/gemini.py
import asyncio, time
from providers.base import ConnectionTestResult, LLMProvider, LLMResponse


class GeminiProvider(LLMProvider):
    name = "gemini"
    label = "Google Gemini"
    base_url = "https://generativelanguage.googleapis.com"
    env_key = "GEMINI_API_KEY"
    default_models = ["gemini-1.5-flash", "gemini-1.5-pro"]

    def _sync_test(self, model):
        import google.generativeai as genai
        genai.configure(api_key=self.api_key)
        start = time.time()
        genai.GenerativeModel(model).generate_content("ping")
        return int((time.time() - start) * 1000)

    async def test_connection(self):
        if not self.has_key:
            return ConnectionTestResult(ok=False, message="کلید تنظیم نشده")
        try:
            latency = await asyncio.to_thread(self._sync_test, self.models[0])
            return ConnectionTestResult(
                ok=True, message=f"اتصال موفق",
                latency_ms=latency, sample_model=self.models[0],
            )
        except Exception as e:
            return ConnectionTestResult(ok=False, message=f"خطا: {e}")

    async def ask(self, prompt, model, max_tokens=2000, temperature=0.2):
        # مشابه — با asyncio.to_thread
        ...
```

**الگو:** SDKهای async از خودشان، SDKهای sync با `asyncio.to_thread`.

### ثبت در Registry

```python
# providers/registry.py
from providers.deepseek import DeepSeekProvider
from providers.gemini import GeminiProvider
from providers.glm import GLMProvider
from providers.openai import OpenAIProvider
from providers.openrouter import OpenRouterProvider


BUILTIN: dict[str, type[LLMProvider]] = {
    OpenRouterProvider.name: OpenRouterProvider,
    OpenAIProvider.name: OpenAIProvider,
    DeepSeekProvider.name: DeepSeekProvider,
    GLMProvider.name: GLMProvider,
    GeminiProvider.name: GeminiProvider,
}
```

## ۹. Provider سفارشی (`providers/custom.py`)

```python
from providers._openai_compatible import OpenAICompatibleProvider


class CustomProvider(OpenAICompatibleProvider):
    is_builtin = False

    def __init__(self, name, label, base_url, env_key,
                 api_key="", models=None):
        self.name = name
        self.label = label
        self.base_url = base_url
        self.env_key = env_key
        self.default_models = models or []
        super().__init__(api_key=api_key, models=models)
```

**نکته:** کاربر فرض می‌شود سرویس OpenAI-compatible اضافه می‌کند. اگر کسی SDK متفاوتی دارد، باید plugin اختصاصی بنویسد (نه از UI).

## ۱۰. Manager (`providers/manager.py`)

### Singleton

```python
class ProviderManager:
    def __init__(self):
        self.providers: dict[str, LLMProvider] = {}
        self.active: str | None = None

provider_manager = ProviderManager()
```

### `load()` — الگوریتم بارگذاری

```
۱. پاک‌سازی حافظه
۲. seed کردن builtinها:
   برای هر cls در BUILTIN:
     اگر در DB نیست → INSERT با is_builtin=1
۳. خواندن همه ردیف‌ها
۴. برای هر ردیف:
   - محاسبه api_key: DB > .env
   - اگر builtin → cls(api_key, default_models از کد)
   - اگر custom → CustomProvider(...)
   - افزودن به self.providers
   - اگر is_active → self.active = name
۵. اگر هیچ Provider فعالی نبود:
   DEFAULT_PROVIDER از .env یا اولین Provider
```

### `list_providers()` — برای UI

```python
def list_providers(self) -> list[dict]:
    rows = SELECT * FROM providers ORDER BY is_builtin DESC, name
    for r in rows:
        d["has_key"] = provider.has_key
        d["models_list"] = json.loads(d["models"])
        d["key_source"] = self._key_source(d)   # db | env | none
    return result
```

### `update_provider()` — ویرایش

```python
def update_provider(self, name, api_key=None, models=None,
                    env_key=None, base_url=None):
    # ۱. بررسی is_builtin
    # ۲. ساخت داینامیک UPDATE
    # ۳. env_key و base_url فقط برای custom قابل ویرایش
    # ۴. self.load() در انتها
```

**قاعده:** `api_key` و `models` برای همه؛ `env_key` و `base_url` فقط برای custom.

### `add_custom()` / `remove_custom()` / `set_active()`

```python
def set_active(self, name):
    UPDATE providers SET is_active=0
    UPDATE providers SET is_active=1 WHERE name=?
    self.active = name

def add_custom(self, name, base_url, env_key, models, api_key=""):
    INSERT ... is_builtin=0
    self.load()

def remove_custom(self, name):
    DELETE FROM providers WHERE name=? AND is_builtin=0
    self.load()
```

## ۱۱. UI Patterns (`ui/pages/settings.py`)

### ساختار کارت Provider

```
┌─────────────────────────────────────────────────────────┐
│ ● OpenRouter (https://...)          [کلید: 📄 .env]     │
│ [builtin] [۵ مدل]                                        │
│ [تست اتصال] [ویرایش] [فعال‌سازی / فعال ✓] [🗑️]          │
│ [status message — قابل انتخاب]                          │
└─────────────────────────────────────────────────────────┘
```

### دیالوگ ویرایش

**فیلدها:**
- **نام** — غیرقابل ویرایش (disabled)
- **Base URL** — فقط برای custom
- **نام کلید در .env** — فقط برای custom
- **کلید API** — `password=True, can_reveal_password=True`
- **منبع فعلی** — متن راهنما (`💾 پایگاه داده` / `📄 .env` / `⚠️ تنظیم نشده`)
- **دکمه «پاک کردن کلید»** — بازگشت به `.env`
- **مدل‌ها** — multiline با کاما

### دیالوگ افزودن

**فیلدها:**
- نام (اجباری)
- Base URL (اجباری)
- نام کلید در .env (اختیاری)
- **کلید API** (اختیاری)
- مدل‌ها (اجباری)

### بج `key_source`

```python
if src == "db":
    label, color = "کلید: 💾 پایگاه داده", ft.colors.GREEN
elif src == "env":
    label, color = "کلید: 📄 .env", ft.colors.BLUE_300
else:
    label, color = "کلید: ⚠️ تنظیم نشده", ft.colors.AMBER

badge = ft.Container(
    content=ft.Text(label, size=11, color=color),
    padding=ft.padding.symmetric(horizontal=6, vertical=2),
    bgcolor=ft.colors.with_opacity(0.15, color),
    border_radius=4,
)
```

## ۱۲. Migration Pattern

اگر جدول `providers` از قبل وجود دارد و می‌خواهید ستون اضافه کنید:

```python
# storage/migrations.py
def _column_exists(conn, table, column) -> bool:
    rows = conn.execute(f"PRAGMA table_info({table})").fetchall()
    return any(r["name"] == column for r in rows)

def run_migrations() -> None:
    with get_connection() as conn:
        if not _column_exists(conn, "providers", "api_key"):
            conn.execute("ALTER TABLE providers ADD COLUMN api_key TEXT DEFAULT ''")
            conn.commit()
```

و در `storage/db.py`:

```python
def init_db():
    with get_connection() as conn:
        conn.executescript(SCHEMA)
        conn.commit()
    from storage.migrations import run_migrations
    run_migrations()
```

**برای نصب‌های جدید:** ستون را در `SCHEMA` هم بگذارید (idempotent).

## ۱۳. تست‌های ضروری

| تست | فایل | انتظار |
|---|---|---|
| import base | `python -c "from providers.base import LLMProvider"` | بدون خطا |
| seed builtins | در UI، تنظیمات باز شود | ۵ Provider ببینید |
| تست اتصال | در UI روی دکمه بزنید | پیام «۲ از ۵ مدل کار می‌کند» |
| ویرایش کلید | در UI، کلید جدید | بج `💾`، تست موفق |
| پاک کردن کلید | دکمه «پاک کردن» | بج `📄` (اگر در .env هست) |
| افزودن custom | دیالوگ افزودن | در لیست ظاهر شود |
| حذف custom | آیکن سطل | از لیست برود |
| فعال‌سازی | دکمه فعال‌سازی | فقط یکی فعال |

## ۱۴. سازگاری (Backward Compatibility)

- Providerهای قدیمی که `api_key` در DB نداشتند → `api_key=''` → از `.env` می‌خوانند
- تحلیل‌های قبلی که با Provider فعال انجام شده بودند → در `analyses` با `provider` و `model` ذخیره می‌شوند
- هیچ‌گاه نام Provider را عوض نکنید (کلیدهای خارجی به آن وابسته‌اند)

## ۱۵. نکات دام‌انداز

### ❌ اشتباه ۱ — خواندن مدل‌ها از DB برای builtinها

اگر برای builtinها مدل‌ها را از DB بخوانید، وقتی کد را آپدیت می‌کنید (لیست جدید مدل‌ها)، DB قدیمی می‌ماند.

**✅ درست:** برای builtinها، `cls.default_models` از کد خوانده شود. DB فقط برای custom منبع باشد.

### ❌ اشتباه ۲ — ذخیره `is_active=1` برای چند ردیف

اگر دو ردیف `is_active=1` باشند، رفتار تصادفی می‌شود.

**✅ درست:** در `set_active`:
```python
UPDATE providers SET is_active=0
UPDATE providers SET is_active=1 WHERE name=?
```

### ❌ اشتباه ۳ — تست فقط یک مدل

مدل‌های رایگان OpenRouter مرتب rate-limit می‌شوند.

**✅ درست:** همه مدل‌ها را تست کنید و کارکننده‌ها را گزارش دهید.

### ❌ اشتباه ۴ — timeout یکسان برای تست و ask

تست باید سریع باشد (۲۰s)، ولی ask ممکن است ۱-۲ دقیقه طول بکشد.

**✅ درست:** `timeout=20` برای تست، `timeout=120` برای ask.

### ❌ اشتباه ۵ — نگه‌داشتن کلید در حافظه به‌صورت log

اگر کلید در لاگ‌ها چاپ شود، خطر امنیتی است.

**✅ درست:** در `log_bus.emit`، هرگز `api_key` را چاپ نکنید. فقط `has_key: True/False`.

## ۱۶. راهنمای استفاده مجدد در پروژه جدید

### مرحله ۱ — کپی فایل‌ها

```
providers/__init__.py
providers/base.py
providers/_openai_compatible.py
providers/registry.py
providers/manager.py
providers/custom.py
providers/openrouter.py  (توصیه: این را داشته باشید چون رایگان دارد)
providers/openai.py
```

### مرحله ۲ — Migration در DB

جدول `providers` را با همان SCHEMA بسازید. `migrations.py` را کپی کنید.

### مرحله ۳ — UI

`ui/pages/settings.py` را کپی و در Router اضافه کنید.

### مرحله ۴ — مقدار اولیه

در `main()`:
```python
init_db()
provider_manager.load()
```

### مرحله ۵ — استفاده در منطق کسب‌وکار

```python
provider = provider_manager.get_active()
if provider is None:
    raise RuntimeError("هیچ Provider فعالی نیست")

response = await provider.ask(prompt, model=model, max_tokens=2000)
```

## ۱۷. وابستگی‌ها

```
openai>=1.54.3              # SDK سازگار OpenAI
google-generativeai>=0.8.3  # برای Gemini
python-dotenv>=1.0.1        # خواندن .env
```

## ۱۸. خلاصه تصمیمات کلیدی

| تصمیم | دلیل |
|---|---|
| Interface + Base مشترک | کاهش تکرار، توسعه آسان |
| `api_key` در DB + fallback به `.env` | انعطاف‌پذیری برای کاربر |
| تست چندمدلی | حیاتی برای مدل‌های رایگان |
| `is_active` تکی | جلوگیری از رفتار تصادفی |
| builtinها از کد، custom از DB | آپدیت‌پذیری کد |
| `key_source` badge | شفافیت برای کاربر |
| Migration idempotent | نصب‌های جدید و قدیمی هر دو کار کنند |
| CustomProvider سازگار OpenAI | پوشش ۹۰٪ سرویس‌ها |

---

**پایان سند HANDOFF_PROVIDERS**

این چارچوب در Book Analyzer تست شده و قابل استفاده مستقیم در هر پروژه پایتونی است که به چند Provider LLM نیاز دارد. برای سازگاری کامل، فقط کافی است `log_bus` و `get_connection` پروژه مقصد را با این سند هم‌نام کنید یا importها را تغییر دهید.