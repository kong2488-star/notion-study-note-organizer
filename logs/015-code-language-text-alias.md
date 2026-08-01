# code 블록 language "text" 별칭 추가 로그

- **계획 번호:** 015
- **계획 경로:** `plan/015-code-language-text-alias.md`
- **상태:** 완료
- **시작일:** 2026-08-01
- **완료일:** 2026-08-01

## 작업 요약

`normalize_code_language()`가 `text` 언어를 통과시켜 Notion API 400을 유발하는 문제를 `aliases`에 `"text": "plain text"` 매핑을 추가해 수정한다.

## 주요 결정과 근거

허용 목록 전체 폴백 대신 별칭 한 줄 추가(최소 수정)를 선택. 저장소 소유자가 옵션 1(최소)을 명시적으로 선택함.

## 변경 파일

- `notion_auto_organizer/markdown_convert.py`: `aliases`에 `"text": "plain text"` 추가.
- `tests/test_markdown_convert.py`: `text` → `plain text` 정규화 테스트 추가.

## 의미 있는 명령과 결과

- `python -m pytest -q` → 종료 0, 60 passed.

## 실패, 원인, 해결 방법

- 실패: `PATCH /v1/blocks/.../children` HTTP 400 validation_error, `code.language`가 `"text"`.
- 원인: `text`가 `aliases`에 없어 그대로 전달됨. Notion 허용 목록에 없는 값.
- 해결: `text → plain text` 별칭 추가.

## 검증 결과

- `python -m pytest`: 60 passed. `text → plain text` 정규화 테스트 포함 통과.

## 해결되지 않은 문제와 후속 작업

`plaintext`, `console`, `output` 등 다른 미허용 언어는 여전히 통과됨. 근본 수정(허용 목록 폴백)은 후속 작업으로 남김.
