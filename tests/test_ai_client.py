import pytest

from notion_auto_organizer.ai_client import organize_with_agent
from notion_auto_organizer.note_schema import HeadingBlock, OrganizedNote, ParagraphBlock


class FakeAgent:
    def __init__(self, result):
        self.result = result

    def invoke(self, payload):
        assert payload["messages"][0]["content"] == "원문"
        return self.result


def test_organize_with_agent_renders_structured_response():
    note = OrganizedNote(blocks=[HeadingBlock(level=1, text="제목")])
    agent = FakeAgent({"structured_response": note})

    result = organize_with_agent(agent, "원문", provider="Test")

    assert result == "# 제목"


def test_organize_with_agent_raises_when_structured_response_missing():
    agent = FakeAgent({"structured_response": None})

    with pytest.raises(RuntimeError, match="did not return a structured response"):
        organize_with_agent(agent, "원문", provider="Test")


def test_organize_with_agent_raises_when_rendered_text_is_empty():
    note = OrganizedNote(blocks=[ParagraphBlock(text="")])
    agent = FakeAgent({"structured_response": note})

    with pytest.raises(RuntimeError, match="empty structured response"):
        organize_with_agent(agent, "원문", provider="Test")
