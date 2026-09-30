"""Central registry of built-in providers."""
from providers.base import LLMProvider
from providers.deepseek import DeepSeekProvider
from providers.gemini import GeminiProvider
from providers.glm import GLMProvider
from providers.groq import GroqProvider
from providers.openai import OpenAIProvider
from providers.openrouter import OpenRouterProvider


BUILTIN: dict[str, type[LLMProvider]] = {
    OpenRouterProvider.name: OpenRouterProvider,
    OpenAIProvider.name: OpenAIProvider,
    DeepSeekProvider.name: DeepSeekProvider,
    GLMProvider.name: GLMProvider,
    GeminiProvider.name: GeminiProvider,
    GroqProvider.name: GroqProvider,
}


def get_builtin(name: str) -> type[LLMProvider] | None:
    return BUILTIN.get(name)