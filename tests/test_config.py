from pathlib import Path

import pytest
from pydantic import ValidationError

from notion_auto_organizer.config import Settings, load_settings

UNIFIED_ENV_KEYS = (
    "NOTION_TOKEN",
    "AI_PROVIDER",
    "AI_API_KEY",
    "AI_MODEL",
    "AI_BASE_URL",
)


@pytest.fixture(autouse=True)
def isolated_settings_env(monkeypatch):
    for key in UNIFIED_ENV_KEYS:
        monkeypatch.delenv(key, raising=False)


def set_required_env(monkeypatch, *, provider: str = "gemini") -> None:
    monkeypatch.setenv("NOTION_TOKEN", "notion-token")
    monkeypatch.setenv("AI_PROVIDER", provider)
    monkeypatch.setenv("AI_API_KEY", "ai-key")
    monkeypatch.setenv("AI_MODEL", "ai-model")


def test_load_settings_supports_gemini_with_shared_fields(monkeypatch):
    set_required_env(monkeypatch)

    settings = load_settings(env_file=None)

    assert settings.ai_provider == "gemini"
    assert settings.ai_api_key.get_secret_value() == "ai-key"
    assert settings.ai_model == "ai-model"
    assert settings.ai_base_url is None
    assert settings.cache_namespace == "gemini-ai-model"


def test_load_settings_supports_openai_official_endpoint(monkeypatch):
    set_required_env(monkeypatch, provider="openai")

    settings = load_settings(env_file=None)

    assert settings.ai_provider == "openai"
    assert settings.ai_base_url is None


def test_load_settings_supports_openai_compatible_endpoint(monkeypatch):
    set_required_env(monkeypatch, provider="openai")
    monkeypatch.setenv("AI_BASE_URL", " https://proxy.example/v1 ")

    settings = load_settings(env_file=None)

    assert settings.ai_base_url == "https://proxy.example/v1"


@pytest.mark.parametrize("provider", ["", "unknown"])
def test_load_settings_rejects_missing_or_unknown_provider(monkeypatch, provider):
    set_required_env(monkeypatch)
    if provider:
        monkeypatch.setenv("AI_PROVIDER", provider)
    else:
        monkeypatch.delenv("AI_PROVIDER")

    with pytest.raises(ValidationError, match="ai_provider"):
        load_settings(env_file=None)


@pytest.mark.parametrize("key", ["NOTION_TOKEN", "AI_API_KEY", "AI_MODEL"])
def test_load_settings_rejects_empty_required_values(monkeypatch, key):
    set_required_env(monkeypatch)
    monkeypatch.setenv(key, "   ")

    with pytest.raises(ValidationError):
        load_settings(env_file=None)


def test_load_settings_rejects_base_url_for_gemini(monkeypatch):
    set_required_env(monkeypatch)
    monkeypatch.setenv("AI_BASE_URL", "https://proxy.example/v1")

    with pytest.raises(ValidationError, match="AI_BASE_URL"):
        load_settings(env_file=None)


def test_load_settings_reads_dotenv_file(tmp_path: Path):
    env_file = tmp_path / ".env"
    env_file.write_text(
        "\n".join(
            [
                "NOTION_TOKEN=dotenv-notion-token",
                "AI_PROVIDER=gemini",
                "AI_API_KEY=dotenv-ai-key",
                "AI_MODEL=dotenv-model",
            ]
        ),
        encoding="utf-8",
    )

    settings = load_settings(env_file)

    assert settings.notion_token.get_secret_value() == "dotenv-notion-token"
    assert settings.ai_api_key.get_secret_value() == "dotenv-ai-key"
    assert settings.ai_model == "dotenv-model"


def test_environment_values_override_dotenv(monkeypatch, tmp_path: Path):
    env_file = tmp_path / ".env"
    env_file.write_text(
        "\n".join(
            [
                "NOTION_TOKEN=dotenv-notion-token",
                "AI_PROVIDER=gemini",
                "AI_API_KEY=dotenv-ai-key",
                "AI_MODEL=dotenv-model",
            ]
        ),
        encoding="utf-8",
    )
    monkeypatch.setenv("AI_MODEL", "environment-model")

    settings = load_settings(env_file)

    assert settings.ai_model == "environment-model"


def test_missing_dotenv_file_uses_environment(monkeypatch, tmp_path: Path):
    set_required_env(monkeypatch)

    settings = load_settings(tmp_path / "does-not-exist.env")

    assert settings.ai_model == "ai-model"


def test_settings_repr_does_not_expose_secrets():
    settings = Settings(
        _env_file=None,
        notion_token="notion-secret",
        ai_provider="gemini",
        ai_api_key="ai-secret",
        ai_model="ai-model",
    )

    representation = repr(settings)
    assert "notion-secret" not in representation
    assert "ai-secret" not in representation
