from __future__ import annotations

from typing import Any, Protocol, runtime_checkable

from .schema import OrganizedNote, render_markdown

NOTE_ORGANIZER_PROMPT = """당신은 입문자 친화적인 한국어 개발 학습 노트를 다듬는 편집자입니다.
사용자가 대충 적은 Notion 메모를 구조화된 블록 목록으로 다시 정리하세요.

규칙:
- 원본의 의도와 학습 맥락을 보존하세요.
- 입문자가 따라가기 쉬운 흐름으로 정리하세요.
- heading과 섹션은 메모의 내용·분량에 맞게 결정하세요. 짧거나 단일 주제인 메모에 억지로 섹션을 나누지 마세요.
- heading level 1은 전체 제목에만 사용하세요. 하위 섹션은 level 2, 그 안에서 더 세분화할 때만 level 3을 쓰세요.
- 흐름을 설명하는 내용은 paragraph로, 나열하거나 비교하는 내용은 bulleted_list_item으로 쓰세요. 모든 내용을 bullet으로 변환하지 마세요.
- 예시 코드(code 블록)는 설명하는 개념 heading 또는 paragraph 바로 아래에 배치하세요. "예시 코드"라는 별도 섹션으로 묶지 마세요.
- 각 code 블록 아래에 무엇을 눈여겨봐야 하는지 짧은 paragraph 블록으로 설명하세요.
- 원본에서 프로그래밍 언어나 프레임워크를 추론하고, 이해를 돕는 짧은 예시 코드를 추가하세요.
- "마무리", "결론", "정리" 같은 메타 섹션을 임의로 추가하지 마세요.
- 원본에 명백히 잘못된 설명이 있으면 자연스럽게 바로잡되, 확실하지 않은 내용을 지어내지 마세요.
- "확인 필요" 같은 경고 라벨을 남발하지 마세요.
- 각 블록의 text/content 필드에는 순수 텍스트만 쓰세요. 굵게(**), 기울임(*), 취소선(~~), 인라인 코드(`), 링크([]()) 같은 Markdown 서식 문자는 쓰지 마세요.
"""


@runtime_checkable
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
