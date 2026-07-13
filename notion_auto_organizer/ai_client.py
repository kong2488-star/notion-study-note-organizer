from __future__ import annotations

from typing import Any, Protocol

NOTE_ORGANIZER_PROMPT = """You are an editor for beginner-friendly Korean developer study notes.
Rewrite the user's rough Notion notes into structured Markdown.

Rules:
- Preserve the original intent and learning context.
- Make the flow clear for an intro-to-beginner learner.
- Use this exact section shape when possible:
  # 제목
  ## 핵심 요약
  ## 개념 정리
  ## 예시 코드
- Please respond without using Markdown bold syntax (**).
- Infer the programming language or framework from the source note.
- Add short, helpful example code when it improves understanding.
- Explain what to notice below each code example.
- Smoothly correct clearly wrong explanations.
- Do not overuse warning labels or "확인 필요".
- Return only Markdown body content. Do not wrap the whole answer in a code fence.
"""


class AIClient(Protocol):
    def organize_markdown(self, markdown: str) -> str:
        """Turn rough Markdown notes into organized study notes."""


def organize_with_agent(agent: Any, markdown: str, *, provider: str) -> str:
    result = agent.invoke({"messages": [{"role": "user", "content": markdown}]})
    text = extract_agent_text(result).strip()
    if not text:
        raise RuntimeError(f"{provider} agent did not return output text.")
    return text


def extract_agent_text(result: dict) -> str:
    for message in reversed(result.get("messages", [])):
        content = getattr(message, "content", None)
        if content is None and isinstance(message, dict):
            content = message.get("content")
        text = _content_to_text(content)
        if text:
            return text
    return ""


def _content_to_text(content: object) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        chunks: list[str] = []
        for item in content:
            if isinstance(item, str):
                chunks.append(item)
            elif isinstance(item, dict) and isinstance(item.get("text"), str):
                chunks.append(item["text"])
        return "".join(chunks)
    return ""
