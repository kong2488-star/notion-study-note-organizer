# 006 AI 모듈을 `ai/` 서브패키지로 분리

- **상태:** 완료

## 동기

`notion_auto_organizer/` 패키지 최상위에 AI 관련 파일 5개(`ai_client.py`, `ai_factory.py`, `note_schema.py`, `gemini_client.py`, `openai_client.py`)가 핵심 인프라 파일과 섞여 있어 관심사 분리가 불명확하다. 이를 `ai/` 서브패키지로 묶어 구조를 명확히 한다.

## 목표

- AI 관련 5개 모듈이 `notion_auto_organizer/ai/` 서브패키지로 이동한다.
- 외부 코드(`organizer.py`, `cli.py`, 테스트)의 동작이 변경되지 않는다.
- `python -m pytest`가 통과한다.

## 범위

**포함:**
- `ai/` 서브패키지 신규 파일 6개 생성
- 기존 플랫 파일 5개 삭제
- `organizer.py`, `cli.py` import 수정
- 테스트 파일 5개 import 수정
- `AGENTS.md`, `docs/ARCHITECTURE.md` 경로 갱신

**제외:**
- 각 모듈의 로직 변경 없음

## 단계

1. `ai/schema.py` 생성 (`note_schema.py` 내용 이동)
2. `ai/client.py` 생성 (`ai_client.py` 내용 이동, `.note_schema` → `.schema`)
3. `ai/gemini.py` 생성 (`gemini_client.py` 이동, `.ai_client` → `.client`)
4. `ai/openai.py` 생성 (`openai_client.py` 이동, `.ai_client` → `.client`)
5. `ai/factory.py` 생성 (`ai_factory.py` 이동, 상대 import 갱신)
6. `ai/__init__.py` 생성 (public exports 정의)
7. `organizer.py:8` — `.ai_client` → `.ai`
8. `cli.py:5` — `.ai_factory` → `.ai`
9. 기존 플랫 파일 5개 삭제
10. 테스트 5개 import 경로 수정
11. `AGENTS.md`, `docs/ARCHITECTURE.md` 경로 갱신
12. `python -m pytest` 실행

## 검증

- `python -m pytest` 실행 후 AI 관련 테스트(`test_ai_client.py`, `test_ai_factory.py`, `test_note_schema.py`, `test_gemini_client.py`, `test_openai_client.py`) 전원 통과
- smoke test: `python -c "from notion_auto_organizer.ai import AIClient, create_ai_client, GeminiClient, OpenAIClient, OrganizedNote"`
