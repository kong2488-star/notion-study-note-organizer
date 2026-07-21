# Agent 응답을 구조화된 Pydantic 스키마로 고정 작업 로그

- **계획 번호:** 005
- **계획 경로:** `plan/005-structured-agent-response.md`
- **상태:** 완료
- **시작일:** 2026-07-20
- **완료일:** 2026-07-20

## 작업 요약

승인된 계획 005에 따라 `gemini_client.py`/`openai_client.py`의 LangChain agent 응답을 자유 텍스트 대신 `note_schema.OrganizedNote` Pydantic 구조로 고정했습니다. `ai_client.organize_with_agent`가 `structured_response`를 읽어 결정적으로 Markdown 문자열로 렌더링하도록 재작성했고, 더 이상 쓰이지 않는 `extract_agent_text`/`_content_to_text`를 삭제했습니다.

## 주요 결정과 근거

- `langchain.agents.create_agent`의 `response_format`에 Pydantic 모델을 넘기면 tool-calling 기반 구조화 출력이 강제되고, `agent.invoke(...)` 결과에 검증된 인스턴스가 `result["structured_response"]`로 들어온다는 것을 설치된 `langchain`(1.3.14)/`langchain-core`(1.4.9) 소스(`structured_output.py`, `factory.py`)로 직접 확인한 뒤 설계했습니다.
- `note_schema.py`를 새 모듈로 분리했습니다. `markdown_to_blocks`가 지원하는 8가지 블록에 1:1로 대응하는 discriminated union이라 `ai_client.py`에 넣기엔 크기가 커서, `markdown_convert.py`와 대칭되는 위치에 별도 파일로 뒀습니다.
- `AIClient` Protocol 시그니처(`organize_markdown(markdown: str) -> str`)는 그대로 유지했습니다. 구조화 응답은 provider 클라이언트 내부에서만 Markdown 문자열로 렌더링되므로 `organizer.py`, `cli.py`, `cache.py`, `markdown_to_blocks` 흐름은 전혀 바꾸지 않았습니다.
- 이전에 검토했던 `validate_markdown` LangChain 도구(사후 검사 + 자기 수정) 아이디어는 구현하지 않았습니다. 스키마로 고정하는 방식이 구조적 위반 자체를 애초에 만들 수 없게 하므로 더 견고하고, 두 메커니즘을 병행하면 불필요한 복잡도가 늘어난다고 판단했습니다.
- `render_markdown`은 블록 사이를 항상 빈 줄로 구분합니다. `markdown_to_blocks`가 빈 줄 없이 이어진 문단 줄을 하나로 합치기 때문에, 두 개의 별도 문단 블록이 하나로 병합되는 것을 막기 위한 결정입니다.
- `find_unsupported_markdown` 같은 별도 검증 함수나 기울임(단일 `*`) 텍스트 내부 서식용 sanitizer는 추가하지 않았습니다. 스키마 자체가 표/중첩 리스트/4단계 이상 헤딩을 막고, 남은 인라인 서식 문제는 프롬프트 지시로 완화하는 것으로 범위를 한정했습니다.

## 변경 파일

- `notion_auto_organizer/note_schema.py` (신규): `HeadingBlock`/`ParagraphBlock`/`BulletedListItemBlock`/`NumberedListItemBlock`/`TodoBlock`/`QuoteBlock`/`CodeBlock`/`DividerBlock`, `OrganizedBlock` discriminated union, `OrganizedNote`, `render_markdown`.
- `notion_auto_organizer/ai_client.py`: `NOTE_ORGANIZER_PROMPT`를 구조화 응답 기준으로 재작성, `organize_with_agent`가 `structured_response`를 읽어 렌더링하도록 재작성, `extract_agent_text`/`_content_to_text` 삭제, `note_schema`에서 `OrganizedNote`/`render_markdown` import.
- `notion_auto_organizer/gemini_client.py`, `notion_auto_organizer/openai_client.py`: `create_agent(...)`에 `response_format=OrganizedNote` 추가.
- `tests/test_note_schema.py` (신규): 블록별 `render_markdown` 출력과 `markdown_to_blocks` 왕복 검증.
- `tests/test_ai_client.py` (신규): `organize_with_agent`의 정상/`structured_response=None`/빈 렌더링 결과 케이스.
- `tests/test_gemini_client.py`, `tests/test_openai_client.py`: `FakeAgent.invoke`가 `{"structured_response": OrganizedNote(...)}`를 반환하도록 갱신, `response_format=OrganizedNote` 단언 추가.
- `docs/CODE_GUIDE.md`: `note_schema.py` 절 추가, `ai_client.py`/provider 클라이언트/테스트 요약 설명 갱신.
- `docs/ARCHITECTURE.md`: 모듈 경계에 `note_schema.py` 추가, `ai_client.py` 설명 갱신.
- `AGENTS.md`: 주요 파일 목록에 `note_schema.py` 추가, `ai_client.py` 설명 갱신.
- `plan/005-structured-agent-response.md`, `logs/005-structured-agent-response.md`: 이번 작업의 계획과 로그.

## 의미 있는 명령과 결과

- `python -m pytest`: 57개 테스트 전체 통과 (기존 51개 + 신규 6개).
- `python -m ruff check notion_auto_organizer tests`: 통과. 최초 실행 시 `note_schema.py`의 `Union[...]` 사용(UP007)과 `ai_client.py`의 100자 초과 줄(E501)을 지적받아 `X | Y` 문법과 줄바꿈으로 수정한 뒤 다시 통과.
- `python -m ruff format --check notion_auto_organizer tests`: 통과 (26개 파일 모두 포맷 규칙 준수).

## 실패, 원인, 해결 방법

- `ruff check`가 `note_schema.py`의 `Union[HeadingBlock, ...]`을 UP007(구식 타입 표기)로 지적함 → `Annotated[HeadingBlock | ParagraphBlock | ... | DividerBlock, Field(discriminator="type")]` 형태로 수정.
- `ruff check`가 `ai_client.py`의 프롬프트 문자열 중 한 줄이 106자로 100자 제한을 초과한다고 지적함 → 해당 줄을 프롬프트의 다른 여러 줄과 같은 2-스페이스 들여쓰기 연속 스타일로 줄바꿈해 100자 이하로 축소.

## 검증 결과

- 통과: `python -m pytest` (57 passed).
- 통과: `ruff check`, `ruff format --check`.
- 통과: `test_note_schema.py`가 8개 블록 타입 모두 `markdown_to_blocks`로 되돌렸을 때 기대한 타입 시퀀스가 나옴을 확인.
- 통과: `test_ai_client.py`가 `structured_response=None`과 빈 렌더링 결과 모두에서 `RuntimeError`를 던짐을 확인.
- 통과: `docs/CODE_GUIDE.md`, `docs/ARCHITECTURE.md`, `AGENTS.md`를 실제 코드와 대조해 일치를 확인.

## 해결되지 않은 문제와 후속 작업

- 기울임(단일 `*`) 등 블록 `text`/`content` 필드 내부의 잔여 Markdown 서식 문자는 스키마로 막지 못하고 프롬프트 지시에만 의존합니다. 실제 운영 중 문제가 드러나면 별도 sanitizer 도입을 후속 작업으로 검토합니다.
