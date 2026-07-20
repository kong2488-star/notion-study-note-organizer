# NOTE_ORGANIZER_PROMPT 보강 및 한국어 번역

- **상태:** 완료

## 동기

`notion_auto_organizer/ai_client.py`의 `NOTE_ORGANIZER_PROMPT`는 Gemini/OpenAI 두 제공자가 공통으로 사용하는 시스템 프롬프트이지만 영어로 작성되어 있고, 규칙이 실제 `markdown_convert.py` 파서의 제약을 다 반영하지 못합니다. `markdown_to_blocks`의 `rich_text()`는 inline 서식을 전혀 파싱하지 않아 굵게 외의 인라인 서식(기울임, 취소선, 인라인 코드, 링크)도 그대로 리터럴 문자로 Notion에 노출되고, 표와 중첩 리스트, 4단계 이상 헤딩도 지원되지 않습니다. 기존 프롬프트는 굵게(`**`)만 금지해 이 제약을 충분히 막지 못했습니다.

## 목표

- `NOTE_ORGANIZER_PROMPT`를 한국어로 번역합니다.
- `markdown_to_blocks`가 지원하지 않는 문법(모든 인라인 서식, 표, 중첩 리스트, 4단계 이상 헤딩)을 프롬프트에서 명시적으로 금지해 Notion 렌더링이 깨지는 것을 방지합니다.
- 기존 규칙(4단계 섹션 구조, 코드펜스로 전체를 감싸지 않기, 예시 코드 추가, 매끄러운 오류 정정, 경고 라벨 자제)은 유지합니다.

## 범위

- `notion_auto_organizer/ai_client.py`의 `NOTE_ORGANIZER_PROMPT` 문자열을 교체합니다.
- `docs/CODE_GUIDE.md`에서 이 프롬프트를 요약하는 설명을 새 규칙에 맞게 갱신합니다.
- `ai_client.py`의 로직(`organize_with_agent`, `extract_agent_text` 등)과 `gemini_client.py`, `openai_client.py`, `markdown_convert.py`는 변경하지 않습니다.
- AGENTS.md, README 등 이 프롬프트를 설명하지 않는 다른 문서는 변경하지 않습니다.

## 단계

1. `NOTE_ORGANIZER_PROMPT`를 한국어로 번역하면서 인라인 서식·표·중첩 리스트·4단계 이상 헤딩 금지 규칙을 추가합니다.
2. `docs/CODE_GUIDE.md`의 프롬프트 설명을 새 내용과 일치하도록 갱신합니다.
3. `python -m pytest`를 실행해 통과를 확인합니다.
4. 작업 로그를 완료하고 이 계획을 완료 상태로 표시합니다.

## 검증

- `python -m pytest` 전체 통과.
- `docs/CODE_GUIDE.md`의 프롬프트 설명이 실제 `NOTE_ORGANIZER_PROMPT` 내용과 일치하는지 육안 검토.
