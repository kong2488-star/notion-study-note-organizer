from __future__ import annotations

from langchain.agents import create_agent
from langchain_openai import ChatOpenAI

from .ai_client import NOTE_ORGANIZER_PROMPT, organize_with_agent


class OpenAIClient:
    def __init__(self, api_key: str, base_url: str, model: str) -> None:
        chat_model = ChatOpenAI(
            api_key=api_key,
            base_url=base_url,
            model=model,
            temperature=0.3,
        )
        self.agent = create_agent(
            model=chat_model,
            tools=[],
            system_prompt=NOTE_ORGANIZER_PROMPT,
            name="note_organizer_agent",
        )

    def organize_markdown(self, markdown: str) -> str:
        return organize_with_agent(self.agent, markdown, provider="OpenAI")
