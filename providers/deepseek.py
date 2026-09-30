from providers._openai_compatible import OpenAICompatibleProvider


class DeepSeekProvider(OpenAICompatibleProvider):
    name = "deepseek"
    label = "DeepSeek"
    base_url = "https://api.deepseek.com/v1"
    env_key = "DEEPSEEK_API_KEY"
    default_models = [
        "deepseek-chat",
        "deepseek-reasoner",
    ]