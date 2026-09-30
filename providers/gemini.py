"""Google Gemini — uses google-generativeai SDK (not OpenAI-compatible)."""
import asyncio
import time

from providers.base import ConnectionTestResult, LLMProvider, LLMResponse


class GeminiProvider(LLMProvider):
    name = "gemini"
    label = "Google Gemini"
    base_url = "https://generativelanguage.googleapis.com"
    env_key = "GEMINI_API_KEY"
    default_models = [
        "gemini-1.5-flash",
        "gemini-1.5-pro",
        "gemini-2.0-flash",
    ]

    def _sync_test(self, model: str) -> int:
        import google.generativeai as genai

        genai.configure(api_key=self.api_key)
        m = genai.GenerativeModel(model)
        start = time.time()
        m.generate_content("ping")
        return int((time.time() - start) * 1000)

    async def test_connection(self) -> ConnectionTestResult:
        if not self.has_key:
            return ConnectionTestResult(
                ok=False,
                message=f"کلید API تنظیم نشده است. متغیر {self.env_key} را در .env پر کنید.",
            )
        model = self.models[0] if self.models else "gemini-1.5-flash"
        try:
            latency = await asyncio.to_thread(self._sync_test, model)
            return ConnectionTestResult(
                ok=True,
                message=f"اتصال موفق به «{model}»",
                latency_ms=latency,
                sample_model=model,
            )
        except Exception as e:
            return ConnectionTestResult(ok=False, message=f"خطا: {type(e).__name__} — {e}")

    def _sync_ask(self, prompt: str, model: str) -> tuple[str, int, int]:
        import google.generativeai as genai

        genai.configure(api_key=self.api_key)
        m = genai.GenerativeModel(model)
        resp = m.generate_content(prompt)
        text = resp.text or ""
        tokens_in = 0
        tokens_out = 0
        try:
            usage = resp.usage_metadata
            tokens_in = getattr(usage, "prompt_token_count", 0) or 0
            tokens_out = getattr(usage, "candidates_token_count", 0) or 0
        except Exception:
            pass
        return text, tokens_in, tokens_out

    async def ask(
        self,
        prompt: str,
        model: str,
        max_tokens: int = 2000,
        temperature: float = 0.2,
    ) -> LLMResponse:
        if not self.has_key:
            raise RuntimeError(f"کلید API برای {self.name} تنظیم نشده است.")
        text, t_in, t_out = await asyncio.to_thread(self._sync_ask, prompt, model)
        return LLMResponse(
            text=text,
            tokens_in=t_in,
            tokens_out=t_out,
            cost_usd=0.0,
            model=model,
            provider=self.name,
        )