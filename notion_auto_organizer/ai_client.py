from __future__ import annotations

from typing import Any, Protocol

NOTE_ORGANIZER_PROMPT = """당신은 입문자 친화적인 한국어 개발 학습 노트를 다듬는 편집자입니다.
사용자가 대충 적은 Notion 메모를 구조화된 Markdown으로 다시 작성하세요.

규칙:
- 원본의 의도와 학습 맥락을 보존하세요.
- 입문자가 따라가기 쉬운 흐름으로 정리하세요.
- 가능하면 다음 섹션 구조를 그대로 사용하세요:
  # 제목
  ## 핵심 요약
  ## 개념 정리
  ## 예시 코드
- 원본에서 프로그래밍 언어나 프레임워크를 추론하고, 이해를 돕는 짧은 예시 코드를 추가하세요.
- 각 예시 코드 아래에 무엇을 눈여겨봐야 하는지 짧게 설명하세요.
- 원본에 명백히 잘못된 설명이 있으면 자연스럽게 바로잡되, 확실하지 않은 내용을 지어내지 마세요.
- "확인 필요" 같은 경고 라벨을 남발하지 마세요.
- 다음 Markdown 문법만 사용하세요: 제목(#, ##, ###, 4단계 이상 금지), 문단, 순서 없는/있는 목록(중첩 금지), 체크박스(- [ ]), 인용(>), 코드펜스, 구분선(---).
- 굵게(**), 기울임(*), 취소선(~~), 인라인 코드(`), 링크([]())를 포함한 모든 인라인 서식 문법을 사용하지 마세요. Notion으로 옮길 때 그대로 문자로 노출되어 깨집니다. 강조하고 싶으면 문장으로 풀어서 쓰세요.
- 표를 사용하지 마세요. 표 대신 목록이나 문단으로 정리하세요.
- Markdown 본문만 반환하세요. 답변 전체를 코드펜스로 감싸지 마세요.
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
