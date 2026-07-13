from notion_auto_organizer import openai_client
from notion_auto_organizer.openai_client import OpenAIClient


class FakeAgent:
    def invoke(self, payload):
        assert payload["messages"][0]["content"] == "원문"
        return {"messages": [{"content": [{"text": "# 정리된 노트"}]}]}


def test_openai_client_uses_proxy_and_model(monkeypatch):
    captured = {}

    def fake_model(**kwargs):
        captured["model"] = kwargs
        return object()

    def fake_create_agent(**kwargs):
        captured["agent"] = kwargs
        return FakeAgent()

    monkeypatch.setattr(openai_client, "ChatOpenAI", fake_model)
    monkeypatch.setattr(openai_client, "create_agent", fake_create_agent)

    result = OpenAIClient(
        "proxy-token", "https://proxy.example/v1", "openai-model"
    ).organize_markdown("원문")

    assert result == "# 정리된 노트"
    assert captured["model"] == {
        "api_key": "proxy-token",
        "base_url": "https://proxy.example/v1",
        "model": "openai-model",
        "temperature": 0.3,
    }
    assert captured["agent"]["name"] == "note_organizer_agent"
