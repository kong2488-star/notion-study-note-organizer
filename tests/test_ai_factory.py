from notion_auto_organizer.ai import factory as ai_factory
from notion_auto_organizer.config import Settings


def make_settings(**overrides) -> Settings:
    values = {
        "notion_token": "notion-token",
        "ai_provider": "gemini",
        "ai_api_key": "shared-key",
        "ai_model": "shared-model",
    }
    values.update(overrides)
    return Settings(_env_file=None, **values)


def test_factory_passes_shared_settings_to_gemini(monkeypatch):
    captured = {}

    def fake_gemini(api_key, model):
        captured.update(api_key=api_key, model=model)
        return object()

    monkeypatch.setattr(ai_factory, "GeminiClient", fake_gemini)

    ai_factory.create_ai_client(make_settings())

    assert captured == {"api_key": "shared-key", "model": "shared-model"}


def test_factory_passes_optional_base_url_to_openai(monkeypatch):
    captured = {}

    def fake_openai(api_key, model, *, base_url=None):
        captured.update(api_key=api_key, model=model, base_url=base_url)
        return object()

    monkeypatch.setattr(ai_factory, "OpenAIClient", fake_openai)

    ai_factory.create_ai_client(
        make_settings(
            ai_provider="openai",
            ai_base_url="https://proxy.example/v1",
        )
    )

    assert captured == {
        "api_key": "shared-key",
        "model": "shared-model",
        "base_url": "https://proxy.example/v1",
    }
