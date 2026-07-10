from __future__ import annotations

from langchain.agents import create_agent
from langchain_openai import ChatOpenAI

from .ai_client import AIClient, NOTE_ORGANIZER_PROMPT, extract_agent_text


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
        result = self.agent.invoke(
            {"messages": [{"role": "user", "content": markdown}]}
        )
        text = extract_agent_text(result).strip()
        if not text:
            raise RuntimeError("OpenAI agent did not return output text.")
        return text
