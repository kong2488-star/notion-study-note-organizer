# 프로젝트 개선 로그

- **계획 번호:** 010
- **계획 경로:** `plan/010-project-improvements.md`
- **상태:** 완료
- **시작일:** 2026-07-21
- **완료일:** 2026-07-21

## 작업 요약

4가지 개선을 완료했다. Windows tmp_path 오류를 해결해 로컬 테스트 57개 전부 통과, 커스텀 예외 클래스 계층을 도입했고, AIClient Protocol에 @runtime_checkable을 추가했으며, README에 트러블슈팅 섹션을 추가했다.

## 주요 결정과 근거

- `AIClientError`로 예외 교체 후 `test_ai_failure_does_not_replace_notion_page`가 `RuntimeError`를 기대하고 있어 `AIClientError`로 갱신했다.
- 백업/결과 저장 실패는 Notion/AI와 무관한 파일 I/O 문제이므로 `OrganizationError`(기본 클래스)로 분류했다.

## 변경 파일

- `pyproject.toml` — `addopts = "--basetemp=.pytest_tmp"` 추가
- `.gitignore` — `.pytest_tmp/` 추가
- `notion_auto_organizer/exceptions.py` 신규 — `OrganizationError`, `NotionError`, `AIClientError`
- `notion_auto_organizer/organizer.py` — RuntimeError → 단계별 커스텀 예외, exceptions import 추가
- `notion_auto_organizer/ai/client.py` — `@runtime_checkable` 추가
- `README.md` — Run 섹션 갱신, Troubleshooting 섹션 추가
- `tests/test_organizer.py` — `RuntimeError` → `AIClientError`

## 의미 있는 명령과 결과

```
python -m pytest
```
57 passed, 0 errors (기존 9 errors → 0)

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
