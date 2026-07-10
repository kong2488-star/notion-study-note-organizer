import pytest

from notion_auto_organizer.config import load_settings


def set_common_env(monkeypatch):
    monkeypatch.setenv("NOTION_TOKEN", "notion-token")
    monkeypatch.setenv("GEMINI_API_KEY", "gemini-key")
    monkeypatch.setenv("GEMINI_MODEL", "gemini-model")
    monkeypatch.setenv("PROXY_TOKEN", "proxy-token")
    monkeypatch.setenv("CHAT_PROXY_URL", "https://proxy.example/v1")
    monkeypatch.setenv("OPENAI_MODEL", "openai-model")


def test_load_settings_supports_gemini_provider(monkeypatch):
    set_common_env(monkeypatch)
    monkeypatch.setenv("AI_PROVIDER", "gemini")

    settings = load_settings()

    assert settings.ai_provider == "gemini"
    assert settings.gemini_model == "gemini-model"


def test_load_settings_supports_openai_provider(monkeypatch):
    set_common_env(monkeypatch)
    monkeypatch.setenv("AI_PROVIDER", "openai")

    settings = load_settings()

    assert settings.ai_provider == "openai"
    assert settings.proxy_token == "proxy-token"
    assert settings.chat_proxy_url == "https://proxy.example/v1"
    assert settings.openai_model == "openai-model"


def test_load_settings_rejects_unknown_provider(monkeypatch):
    set_common_env(monkeypatch)
    monkeypatch.setenv("AI_PROVIDER", "unknown")

    with pytest.raises(ValueError, match="AI_PROVIDER"):
        load_settings()


def test_load_settings_validates_selected_provider(monkeypatch):
    set_common_env(monkeypatch)
    monkeypatch.setenv("AI_PROVIDER", "openai")
    monkeypatch.setenv("PROXY_TOKEN", "")

    with pytest.raises(ValueError, match="PROXY_TOKEN"):
        load_settings()
