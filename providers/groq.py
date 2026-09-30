"""Groq provider — OpenAI-compatible, extremely fast inference."""
from providers._openai_compatible import OpenAICompatibleProvider


class GroqProvider(OpenAICompatibleProvider):
    name = "groq"
    label = "Groq"
    base_url = "https://api.groq.com/openai/v1"
    env_key = "GROQ_API_KEY"
    default_models = [
        "openai/gpt-oss-120b",
        "openai/gpt-oss-20b",
        "qwen/qwen3.8-27b",
    ]