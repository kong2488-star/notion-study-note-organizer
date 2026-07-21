# Agent 응답을 구조화된 Pydantic 스키마로 고정

- **상태:** 완료

## 동기

계획 004에서 `NOTE_ORGANIZER_PROMPT`에 "표/중첩 리스트/4단계 이상 헤딩/인라인 서식 금지" 같은 Markdown 문법 규칙을 추가했지만, 이는 프롬프트로 지시만 할 뿐 실제로 강제하지 않습니다. 모델이 규칙을 놓치면 `markdown_convert.py`의 `markdown_to_blocks`가 해당 문법을 파싱하지 못해 Notion 페이지에 서식 문자가 그대로 노출됩니다. `validate_markdown` 같은 사후 검사 도구를 추가하는 방향을 검토했지만, agent 응답 자체를 Pydantic 스키마로 고정하면 이런 구조적 위반이 애초에 생성될 수 없어 더 견고합니다.

## 목표

- `gemini_client.py`/`openai_client.py`의 LangChain agent가 자유 텍스트 대신 `note_schema.OrganizedNote` 구조로 응답하게 만듭니다.
- 구조화된 응답을 결정적으로 Markdown 문자열로 렌더링해 기존 `AIClient.organize_markdown(markdown: str) -> str` 계약과 `organizer.py`/`cli.py`/`cache.py`/`markdown_to_blocks` 흐름을 그대로 유지합니다.
- 표, 중첩 리스트, 4단계 이상 헤딩 같은 구조적 위반이 스키마 단계에서부터 불가능하게 만듭니다.

## 범위

- `notion_auto_organizer/note_schema.py` (신규): 8종 블록 Pydantic 모델, `OrganizedNote`, `render_markdown`.
- `notion_auto_organizer/ai_client.py`: `NOTE_ORGANIZER_PROMPT` 재작성, `organize_with_agent`가 `structured_response`를 읽어 렌더링하도록 재작성, 더 이상 쓰이지 않는 `extract_agent_text`/`_content_to_text` 삭제.
- `notion_auto_organizer/gemini_client.py`, `notion_auto_organizer/openai_client.py`: `create_agent(..., response_format=OrganizedNote)` 추가.
- `tests/test_note_schema.py`, `tests/test_ai_client.py` (신규), `tests/test_gemini_client.py`, `tests/test_openai_client.py` (갱신).
- `docs/CODE_GUIDE.md`, `docs/ARCHITECTURE.md`, `AGENTS.md` 설명 갱신.
- `AIClient` Protocol 시그니처, `organizer.py`, `cli.py`, `cache.py`, `markdown_convert.py` 본체는 변경하지 않습니다.
- 이전에 검토했던 `validate_markdown` LangChain 도구는 구현하지 않습니다 (이 설계로 대체됨).

## 단계

1. `note_schema.py`에 블록 Pydantic 모델과 `render_markdown`을 작성한다.
2. `ai_client.py`의 프롬프트와 `organize_with_agent`를 구조화 응답 기반으로 재작성하고, orphan이 된 `extract_agent_text`/`_content_to_text`를 삭제한다.
3. `gemini_client.py`, `openai_client.py`에 `response_format=OrganizedNote`를 추가한다.
4. `tests/test_note_schema.py`, `tests/test_ai_client.py`를 작성하고 `tests/test_gemini_client.py`, `tests/test_openai_client.py`를 갱신한다.
5. `python -m pytest`와 `ruff check`/`ruff format --check`를 통과시킨다.
6. `docs/CODE_GUIDE.md`, `docs/ARCHITECTURE.md`, `AGENTS.md`를 갱신한다.
7. 작업 로그를 완료하고 이 계획을 완료 상태로 표시한다.

## 검증

- `python -m pytest` 전체 통과.
- `ruff check notion_auto_organizer tests`, `ruff format --check notion_auto_organizer tests` 통과.
- `test_note_schema.py`가 8개 블록 타입 각각을 `markdown_to_blocks`로 왕복 검증하는지 확인.
- `test_ai_client.py`가 `structured_response` 없음/빈 렌더링 결과에서 `RuntimeError`를 확인하는지 검토.
- 문서(`docs/CODE_GUIDE.md`, `docs/ARCHITECTURE.md`, `AGENTS.md`)가 실제 코드와 일치하는지 육안 검토.
