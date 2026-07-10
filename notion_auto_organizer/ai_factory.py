from __future__ import annotations

from .ai_client import AIClient
from .config import Settings
from .gemini_client import GeminiClient
from .openai_client import OpenAIClient


def create_ai_client(settings: Settings) -> AIClient:
    if settings.ai_provider == "gemini":
        return GeminiClient(settings.gemini_api_key, settings.gemini_model)
    if settings.ai_provider == "openai":
        return OpenAIClient(
            settings.proxy_token,
            settings.chat_proxy_url,
            settings.openai_model,
        )
    raise ValueError(f"Unsupported AI_PROVIDER: {settings.ai_provider}")
