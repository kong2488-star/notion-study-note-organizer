# NOTE_ORGANIZER_PROMPT 보강 및 한국어 번역 작업 로그

- **계획 번호:** 004
- **계획 경로:** `plan/004-improve-note-organizer-prompt.md`
- **상태:** 완료
- **시작일:** 2026-07-20
- **완료일:** 2026-07-20

## 작업 요약

승인된 계획 004에 따라 `NOTE_ORGANIZER_PROMPT`를 한국어로 번역하고, `markdown_to_blocks` 파서가 실제로 지원하는 문법으로 규칙을 좁혔습니다.

## 주요 결정과 근거

- `markdown_convert.py`를 읽고 `rich_text()`가 inline 서식(굵게/기울임/취소선/인라인 코드/링크)을 전혀 파싱하지 않는다는 점을 확인했습니다. 기존 프롬프트는 굵게만 금지했지만, 실제로는 모든 inline 서식이 Notion에 리터럴 문자로 노출되므로 전부 금지하도록 확장했습니다.
- `markdown_to_blocks`가 들여쓰기 기반 중첩이나 표 문법을 처리하지 않는다는 점을 확인해 표와 중첩 리스트 사용을 금지했습니다.
- 헤딩 정규식이 `#{1,3}`이라 4단계 이상 헤딩은 매칭되지 않고 리터럴 텍스트가 되므로 3단계까지만 쓰도록 명시했습니다.
- 기존 규칙(4단계 섹션 구조, 코드펜스로 전체를 감싸지 않기, 예시 코드 추가, 매끄러운 오류 정정, 경고 라벨 자제)은 그대로 유지했습니다.
- 프롬프트 문자열 내용을 검증하는 테스트가 없어(`tests/`에 `test_ai_client.py` 없음) 기존 테스트 스위트가 이번 변경으로 실패할 위험이 없다고 판단했습니다.

## 변경 파일

- `notion_auto_organizer/ai_client.py`: `NOTE_ORGANIZER_PROMPT`를 한국어로 번역하고 인라인 서식·표·중첩 리스트·4단계 이상 헤딩 금지 규칙을 추가했습니다.
- `docs/CODE_GUIDE.md`: `NOTE_ORGANIZER_PROMPT` 설명(175~181행 근처)을 새 규칙에 맞게 갱신했습니다.
- `plan/004-improve-note-organizer-prompt.md`, `logs/004-improve-note-organizer-prompt.md`: 이번 작업의 계획과 로그를 작성했습니다.

## 의미 있는 명령과 결과

- `python -m pip install -e ".[dev]"`: 개발 환경에 프로젝트와 의존성(pytest, langchain 계열 등)이 설치되어 있지 않아 실행. 성공.
- `python -m pytest`: 51개 테스트 전체 통과.

## 실패, 원인, 해결 방법

없음

## 검증 결과

- 통과: `python -m pytest` (51 passed).
- 통과: `docs/CODE_GUIDE.md`의 프롬프트 설명을 실제 `NOTE_ORGANIZER_PROMPT` 내용과 육안으로 대조해 일치를 확인.

## 해결되지 않은 문제와 후속 작업

없음
