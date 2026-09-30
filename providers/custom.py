"""User-defined provider, assumed OpenAI-compatible."""
from providers._openai_compatible import OpenAICompatibleProvider


class CustomProvider(OpenAICompatibleProvider):
    is_builtin = False

    def __init__(
        self,
        name: str,
        label: str,
        base_url: str,
        env_key: str,
        api_key: str = "",
        models: list[str] | None = None,
    ) -> None:
        self.name = name
        self.label = label
        self.base_url = base_url
        self.env_key = env_key
        self.default_models = models or []
        super().__init__(api_key=api_key, models=models)