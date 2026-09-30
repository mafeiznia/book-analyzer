from providers._openai_compatible import OpenAICompatibleProvider


class OpenAIProvider(OpenAICompatibleProvider):
    name = "openai"
    label = "OpenAI"
    base_url = "https://api.openai.com/v1"
    env_key = "OPENAI_API_KEY"
    default_models = [
        "gpt-4o-mini",
        "gpt-4o",
        "gpt-4-turbo",
    ]