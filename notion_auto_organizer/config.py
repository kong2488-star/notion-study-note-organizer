from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

DEFAULT_PROVIDER = "gemini"
DEFAULT_GEMINI_MODEL = "gemini-3.5-flash"


@dataclass(frozen=True)
class Settings:
    notion_token: str
    ai_provider: str = DEFAULT_PROVIDER
    gemini_api_key: str = ""
    gemini_model: str = DEFAULT_GEMINI_MODEL
    proxy_token: str = ""
    chat_proxy_url: str = ""
    openai_model: str = ""


def load_dotenv(path: Path = Path(".env")) -> None:
    if not path.exists():
        return

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def load_settings() -> Settings:
    load_dotenv()
    notion_token = os.getenv("NOTION_TOKEN", "").strip()
    ai_provider = os.getenv("AI_PROVIDER", DEFAULT_PROVIDER).strip().lower() or DEFAULT_PROVIDER
    gemini_api_key = os.getenv("GEMINI_API_KEY", "").strip()
    gemini_model = os.getenv("GEMINI_MODEL", DEFAULT_GEMINI_MODEL).strip() or DEFAULT_GEMINI_MODEL
    proxy_token = os.getenv("PROXY_TOKEN", "").strip()
    chat_proxy_url = os.getenv("CHAT_PROXY_URL", "").strip()
    openai_model = os.getenv("OPENAI_MODEL", "").strip()

    missing = []
    if not notion_token:
        missing.append("NOTION_TOKEN")
    if ai_provider not in {"gemini", "openai"}:
        raise ValueError("AI_PROVIDER must be either 'gemini' or 'openai'.")
    if ai_provider == "gemini" and not gemini_api_key:
        missing.append("GEMINI_API_KEY")
    if ai_provider == "openai":
        if not proxy_token:
            missing.append("PROXY_TOKEN")
        if not chat_proxy_url:
            missing.append("CHAT_PROXY_URL")
        if not openai_model:
            missing.append("OPENAI_MODEL")
    if missing:
        names = ", ".join(missing)
        raise ValueError(f"Missing required environment values: {names}")

    return Settings(
        notion_token=notion_token,
        ai_provider=ai_provider,
        gemini_api_key=gemini_api_key,
        gemini_model=gemini_model,
        proxy_token=proxy_token,
        chat_proxy_url=chat_proxy_url,
        openai_model=openai_model,
    )
