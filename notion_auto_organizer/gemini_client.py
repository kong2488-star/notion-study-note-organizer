from __future__ import annotations

from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI

from .ai_client import AIClient, NOTE_ORGANIZER_PROMPT, extract_agent_text


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
        result = self.agent.invoke(
            {"messages": [{"role": "user", "content": markdown}]}
        )
        text = extract_agent_text(result).strip()
        if not text:
            raise RuntimeError("Gemini agent did not return output text.")
        return text
