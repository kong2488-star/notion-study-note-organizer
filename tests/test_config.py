import os
from pathlib import Path

import pytest

from notion_auto_organizer.config import load_dotenv, load_settings


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


@pytest.fixture
def isolated_environ(monkeypatch):
    environ_copy = dict(os.environ)
    monkeypatch.setattr(os, "environ", environ_copy)
    return environ_copy


def test_load_dotenv_parses_values_and_skips_noise(tmp_path: Path, isolated_environ):
    env_file = tmp_path / ".env"
    env_file.write_text(
        "\n".join(
            [
                "# comment line",
                "",
                "PLAIN_VALUE=hello",
                'DOUBLE_QUOTED="quoted value"',
                "SINGLE_QUOTED='single'",
                "SPACED_KEY = spaced value ",
                "no-equals-sign-line",
            ]
        ),
        encoding="utf-8",
    )

    load_dotenv(env_file)

    assert isolated_environ["PLAIN_VALUE"] == "hello"
    assert isolated_environ["DOUBLE_QUOTED"] == "quoted value"
    assert isolated_environ["SINGLE_QUOTED"] == "single"
    assert isolated_environ["SPACED_KEY"] == "spaced value"


def test_load_dotenv_does_not_override_existing_env(tmp_path: Path, isolated_environ):
    isolated_environ["EXISTING_KEY"] = "from-environment"
    env_file = tmp_path / ".env"
    env_file.write_text("EXISTING_KEY=from-file\n", encoding="utf-8")

    load_dotenv(env_file)

    assert isolated_environ["EXISTING_KEY"] == "from-environment"


def test_load_dotenv_ignores_missing_file(tmp_path: Path):
    load_dotenv(tmp_path / "does-not-exist.env")
