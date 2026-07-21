from __future__ import annotations

from langchain.agents import create_agent
from langchain_openai import ChatOpenAI

from .ai_client import NOTE_ORGANIZER_PROMPT, OrganizedNote, organize_with_agent


class OpenAIClient:
    def __init__(self, api_key: str, model: str, *, base_url: str | None = None) -> None:
        model_options: dict[str, object] = {
            "api_key": api_key,
            "model": model,
            "temperature": 0.3,
        }
        if base_url is not None:
            model_options["base_url"] = base_url
        chat_model = ChatOpenAI(**model_options)
        self.agent = create_agent(
            model=chat_model,
            tools=[],
            system_prompt=NOTE_ORGANIZER_PROMPT,
            response_format=OrganizedNote,
            name="note_organizer_agent",
        )

    def organize_markdown(self, markdown: str) -> str:
        return organize_with_agent(self.agent, markdown, provider="OpenAI")
