# 007 ruff import 정렬 오류 수정

- **상태:** 완료

## 동기

006번 AI 서브패키지 구조화 작업에서 import 순서를 잘못 배치해 `ruff check`가 I001(import 정렬) 오류 4건을 잡아냈다. CI Lint 단계가 실패해 테스트 단계까지 도달하지 못하고 있다.

## 목표

`ruff check .`가 오류 없이 통과한다.

## 범위

**포함:**
- `notion_auto_organizer/ai/__init__.py` import 정렬 수정
- `notion_auto_organizer/ai/factory.py` import 정렬 수정
- `tests/test_note_schema.py` import 정렬 수정
- `tests/test_openai_client.py` import 정렬 수정

**제외:** 로직 변경 없음

## 단계

1. `python -m ruff check --fix .` 실행 (4건 자동 수정)
2. `python -m ruff check .` 재실행으로 오류 없음 확인
3. `python -m pytest` 실행으로 회귀 없음 확인

## 검증

`python -m ruff check .` 오류 0건
