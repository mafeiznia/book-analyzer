"""Base interface and dataclasses for LLM providers."""
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
    """Every provider must implement this interface."""

    name: str = ""
    label: str = ""
    base_url: str = ""
    env_key: str = ""
    default_models: list[str] = []
    is_builtin: bool = True

    def __init__(
        self,
        api_key: str = "",
        base_url: str | None = None,
        models: list[str] | None = None,
    ) -> None:
        self.api_key = api_key
        if base_url:
            self.base_url = base_url
        self.models = list(models) if models else list(self.default_models)

    @property
    def has_key(self) -> bool:
        return bool(self.api_key and self.api_key.strip())

    @abstractmethod
    async def test_connection(self) -> ConnectionTestResult:
        ...

    @abstractmethod
    async def ask(
        self,
        prompt: str,
        model: str,
        max_tokens: int = 2000,
        temperature: float = 0.2,
    ) -> LLMResponse:
        ...