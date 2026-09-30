"""Base class for any provider that speaks the OpenAI chat completions API."""
import time

import httpx
from openai import AsyncOpenAI

from providers.base import ConnectionTestResult, LLMProvider, LLMResponse


class OpenAICompatibleProvider(LLMProvider):
    """Shared implementation for OpenAI-compatible endpoints."""

    async def test_connection(self) -> ConnectionTestResult:
        if not self.has_key:
            return ConnectionTestResult(
                ok=False,
                message=f"کلید API تنظیم نشده است. متغیر {self.env_key} را در .env پر کنید.",
            )
        if not self.models:
            return ConnectionTestResult(ok=False, message="هیچ مدلی برای این provider تعریف نشده است.")

        client = AsyncOpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
            timeout=httpx.Timeout(connect=10.0, read=20.0, write=10.0, pool=5.0),
            max_retries=0,
        )

        working: list[tuple[str, int]] = []
        failed: list[tuple[str, str]] = []

        # Test up to 8 models
        for model in self.models[:8]:
            start = time.time()
            try:
                await client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": "ping"}],
                    max_tokens=5,
                )
                latency = int((time.time() - start) * 1000)
                working.append((model, latency))
            except Exception as e:
                short = f"{type(e).__name__}: {str(e)[:80]}"
                failed.append((model, short))

        if working:
            lines = [f"✅ {len(working)} از {len(self.models)} مدل کار می‌کند:"]
            for m, lat in working[:5]:
                lines.append(f"  • {m} — {lat}ms")
            if len(working) > 5:
                lines.append(f"  ... و {len(working) - 5} مدل دیگر")

            first_model, first_latency = working[0]
            return ConnectionTestResult(
                ok=True,
                message="\n".join(lines),
                latency_ms=first_latency,
                sample_model=first_model,
            )
        else:
            lines = ["❌ هیچ مدلی پاسخ نداد."]
            for m, err in failed[:3]:
                lines.append(f"  • {m}")
                lines.append(f"    {err}")
            return ConnectionTestResult(
                ok=False,
                message="\n".join(lines),
            )

    async def ask(
        self,
        prompt: str,
        model: str,
        max_tokens: int = 2000,
        temperature: float = 0.2,
    ) -> LLMResponse:
        if not self.has_key:
            raise RuntimeError(f"کلید API برای {self.name} تنظیم نشده است.")

        import httpx

        client = AsyncOpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
            timeout=httpx.Timeout(
                connect=15.0,      # اتصال
                read=90.0,         # خواندن پاسخ
                write=15.0,        # ارسال
                pool=10.0,         # استخر
            ),
            max_retries=0,         # هیچ retry نکن (جلوگیری از ۳×۹۰ = ۲۷۰ ثانیه)
        )
        resp = await client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=temperature,
        )
        text = resp.choices[0].message.content or ""
        usage = getattr(resp, "usage", None)
        tokens_in = getattr(usage, "prompt_tokens", 0) if usage else 0
        tokens_out = getattr(usage, "completion_tokens", 0) if usage else 0

        return LLMResponse(
            text=text,
            tokens_in=tokens_in,
            tokens_out=tokens_out,
            cost_usd=0.0,
            model=model,
            provider=self.name,
        )