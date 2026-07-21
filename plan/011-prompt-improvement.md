# 011 정리 프롬프트 개선

- **상태:** 완료

## 동기

현재 `NOTE_ORGANIZER_PROMPT`가 모든 메모를 고정된 구조(핵심 요약 → 개념 정리 → 예시 코드)로 출력해 결과가 항상 비슷하게 보인다. 예시 코드가 별도 섹션으로 분리되어 해당 개념과 떨어지고, 짧은 메모도 불필요한 섹션이 강제된다.

## 목표

프롬프트를 수정해 AI가 메모 내용에 맞는 유연한 구조를 생성하고, 예시 코드가 개념 바로 아래에 배치되도록 한다.

## 범위

- `notion_auto_organizer/ai/client.py` — `NOTE_ORGANIZER_PROMPT` 상수 교체
- 코드, 스키마, 테스트 변경 없음

## 단계

1. `client.py`의 `NOTE_ORGANIZER_PROMPT` 교체

## 검증

1. `python -m pytest` → 57 passed
2. `python -m ruff check .` → 이상 없음
