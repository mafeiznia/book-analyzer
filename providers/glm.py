from providers._openai_compatible import OpenAICompatibleProvider


class GLMProvider(OpenAICompatibleProvider):
    name = "glm"
    label = "GLM (Zhipu)"
    base_url = "https://open.bigmodel.cn/api/paas/v4"
    env_key = "GLM_API_KEY"
    default_models = [
        "glm-4-flash",
        "glm-4-air",
        "glm-4-plus",
    ]