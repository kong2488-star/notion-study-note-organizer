from __future__ import annotations

from typing import Any, Protocol

from .note_schema import OrganizedNote, render_markdown

NOTE_ORGANIZER_PROMPT = """당신은 입문자 친화적인 한국어 개발 학습 노트를 다듬는 편집자입니다.
사용자가 대충 적은 Notion 메모를 구조화된 블록 목록으로 다시 정리하세요.

규칙:
- 원본의 의도와 학습 맥락을 보존하세요.
- 입문자가 따라가기 쉬운 흐름으로 정리하세요.
- 가능하면 다음 순서로 블록을 구성하세요:
  heading(level=1, 제목) → heading(level=2, "핵심 요약") → 관련 블록 →
  heading(level=2, "개념 정리") → 관련 블록 → heading(level=2, "예시 코드") → code와 설명 블록
- 원본에서 프로그래밍 언어나 프레임워크를 추론하고, 이해를 돕는 짧은 예시 코드를
  code 블록으로 추가하세요.
- 각 예시 코드 아래에 무엇을 눈여겨봐야 하는지 짧은 paragraph 블록으로 설명하세요.
- 원본에 명백히 잘못된 설명이 있으면 자연스럽게 바로잡되, 확실하지 않은 내용을 지어내지 마세요.
- "확인 필요" 같은 경고 라벨을 남발하지 마세요.
- 각 블록의 text/content 필드에는 순수 텍스트만 쓰세요. 굵게(**), 기울임(*), 취소선(~~),
  인라인 코드(`), 링크([]()) 같은 Markdown 서식 문자는 쓰지 마세요.
"""


class AIClient(Protocol):
    def organize_markdown(self, markdown: str) -> str:
        """Turn rough Markdown notes into organized study notes."""


def organize_with_agent(agent: Any, markdown: str, *, provider: str) -> str:
    result = agent.invoke({"messages": [{"role": "user", "content": markdown}]})
    note = result.get("structured_response")
    if note is None:
        raise RuntimeError(f"{provider} agent did not return a structured response.")
    text = render_markdown(note).strip()
    if not text:
        raise RuntimeError(f"{provider} agent returned an empty structured response.")
    return text


__all__ = [
    "AIClient",
    "NOTE_ORGANIZER_PROMPT",
    "OrganizedNote",
    "organize_with_agent",
]
