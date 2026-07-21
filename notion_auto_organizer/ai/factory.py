from __future__ import annotations

from ..config import Settings
from .client import AIClient
from .gemini import GeminiClient
from .openai import OpenAIClient


def create_ai_client(settings: Settings) -> AIClient:
    api_key = settings.ai_api_key.get_secret_value()
    if settings.ai_provider == "gemini":
        return GeminiClient(api_key, settings.ai_model)
    if settings.ai_provider == "openai":
        return OpenAIClient(
            api_key,
            settings.ai_model,
            base_url=settings.ai_base_url,
        )
    raise ValueError(f"Unsupported AI_PROVIDER: {settings.ai_provider}")
