from notion_auto_organizer.ai import openai as openai_client
from notion_auto_organizer.ai.openai import OpenAIClient
from notion_auto_organizer.ai.schema import HeadingBlock, OrganizedNote


class FakeAgent:
    def invoke(self, payload):
        assert payload["messages"][0]["content"] == "원문"
        note = OrganizedNote(blocks=[HeadingBlock(level=1, text="정리된 노트")])
        return {"structured_response": note}


def test_openai_client_uses_official_endpoint_by_default(monkeypatch):
    captured = {}

    def fake_model(**kwargs):
        captured["model"] = kwargs
        return object()

    def fake_create_agent(**kwargs):
        captured["agent"] = kwargs
        return FakeAgent()

    monkeypatch.setattr(openai_client, "ChatOpenAI", fake_model)
    monkeypatch.setattr(openai_client, "create_agent", fake_create_agent)

    result = OpenAIClient("openai-key", "openai-model").organize_markdown("원문")

    assert result == "# 정리된 노트"
    assert captured["model"] == {
        "api_key": "openai-key",
        "model": "openai-model",
        "temperature": 0.3,
    }
    assert captured["agent"]["response_format"] is OrganizedNote
    assert captured["agent"]["name"] == "note_organizer_agent"


def test_openai_client_uses_compatible_base_url(monkeypatch):
    captured = {}

    def fake_model(**kwargs):
        captured["model"] = kwargs
        return object()

    monkeypatch.setattr(openai_client, "ChatOpenAI", fake_model)
    monkeypatch.setattr(openai_client, "create_agent", lambda **kwargs: FakeAgent())

    OpenAIClient(
        "proxy-key",
        "proxy-model",
        base_url="https://proxy.example/v1",
    ).organize_markdown("원문")

    assert captured["model"]["base_url"] == "https://proxy.example/v1"
