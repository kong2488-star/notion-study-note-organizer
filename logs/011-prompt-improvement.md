# 정리 프롬프트 개선 로그

- **계획 번호:** 011
- **계획 경로:** `plan/011-prompt-improvement.md`
- **상태:** 완료
- **시작일:** 2026-07-21
- **완료일:** 2026-07-21

## 작업 요약

`NOTE_ORGANIZER_PROMPT`를 교체해 고정 구조 대신 메모 내용에 맞는 유연한 구조를 생성하도록 했다. 예시 코드는 개념 바로 아래에 배치, paragraph/bullet 구분, heading level 기준, 메타 섹션 금지 규칙을 추가했다. ruff E501 대응으로 `pyproject.toml`에 `per-file-ignores` 추가.

## 주요 결정과 근거

- 프롬프트 내 한국어 문장은 구조상 100자를 넘기 쉬우므로, `client.py`에 한정해 E501을 `per-file-ignores`로 예외 처리했다. 다른 파일에는 영향 없음.

## 변경 파일

- `notion_auto_organizer/ai/client.py` — `NOTE_ORGANIZER_PROMPT` 교체
- `pyproject.toml` — `[tool.ruff.lint.per-file-ignores]` 추가

## 의미 있는 명령과 결과

```
python -m pytest
```
57 passed, 3 warnings

```
python -m ruff check .
```
All checks passed!

## 실패, 원인, 해결 방법

없음

## 검증 결과

없음

## 해결되지 않은 문제와 후속 작업

없음
