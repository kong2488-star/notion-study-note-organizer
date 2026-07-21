from notion_auto_organizer.ai import gemini as gemini_client
from notion_auto_organizer.ai.gemini import GeminiClient
from notion_auto_organizer.ai.schema import HeadingBlock, OrganizedNote


class FakeAgent:
    def invoke(self, payload):
        assert payload["messages"][0]["content"] == "원문"
        note = OrganizedNote(blocks=[HeadingBlock(level=1, text="정리된 노트")])
        return {"structured_response": note}


def test_gemini_client_builds_langchain_agent(monkeypatch):
    captured = {}

    def fake_model(**kwargs):
        captured["model"] = kwargs
        return object()

    def fake_create_agent(**kwargs):
        captured["agent"] = kwargs
        return FakeAgent()

    monkeypatch.setattr(gemini_client, "ChatGoogleGenerativeAI", fake_model)
    monkeypatch.setattr(gemini_client, "create_agent", fake_create_agent)

    result = GeminiClient("gemini-key", "gemini-2.5-flash-lite").organize_markdown("원문")

    assert result == "# 정리된 노트"
    assert captured["model"] == {
        "model": "gemini-2.5-flash-lite",
        "google_api_key": "gemini-key",
        "temperature": 0.3,
    }
    assert captured["agent"]["tools"] == []
    assert captured["agent"]["response_format"] is OrganizedNote
    assert captured["agent"]["name"] == "note_organizer_agent"
