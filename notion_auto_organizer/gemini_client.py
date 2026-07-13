from __future__ import annotations

from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI

from .ai_client import NOTE_ORGANIZER_PROMPT, organize_with_agent


class GeminiClient:
    def __init__(self, api_key: str, model: str) -> None:
        chat_model = ChatGoogleGenerativeAI(
            model=model,
            google_api_key=api_key,
            temperature=0.3,
        )
        self.agent = create_agent(
            model=chat_model,
            tools=[],
            system_prompt=NOTE_ORGANIZER_PROMPT,
            name="note_organizer_agent",
        )

    def organize_markdown(self, markdown: str) -> str:
        return organize_with_agent(self.agent, markdown, provider="Gemini")
