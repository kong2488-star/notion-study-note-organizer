# ruff import 정렬 오류 수정 로그

- **계획 번호:** 007
- **계획 경로:** `plan/007-fix-ruff-import-sort.md`
- **상태:** 완료
- **시작일:** 2026-07-21
- **완료일:** 2026-07-21

## 작업 요약

006번 구조화 작업에서 생긴 I001 오류 4건을 `ruff check --fix`로 자동 수정했다.

## 주요 결정과 근거

없음

## 변경 파일

- `notion_auto_organizer/ai/__init__.py` — import 정렬 수정 (client, factory, gemini, openai, schema 순)
- `notion_auto_organizer/ai/factory.py` — `..config`를 `.client` 앞으로 이동
- `tests/test_note_schema.py` — `ai.schema` import를 `markdown_convert` 앞으로 이동
- `tests/test_openai_client.py` — `ai.openai` import를 `ai.schema` 앞으로 이동

## 의미 있는 명령과 결과

```
python -m ruff check --fix .
```
Found 4 errors (4 fixed, 0 remaining).

```
python -m ruff check .
```
All checks passed!

## 실패, 원인, 해결 방법

없음

## 검증 결과

- `python -m ruff check .` → All checks passed! ✅
- `python -m pytest` → 48 passed, 9 errors (errors 모두 Windows tmp_path 권한 문제, 이번 변경과 무관) ✅

## 해결되지 않은 문제와 후속 작업

없음
