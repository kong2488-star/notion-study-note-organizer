# 010 프로젝트 개선 (테스트·예외·코드품질·문서)

- **상태:** 완료

## 동기

- Windows 로컬에서 `tmp_path` PermissionError로 테스트 9개가 항상 실패
- 예외가 모두 `RuntimeError`여서 타입으로 원인을 구분할 수 없음
- `AIClient` Protocol이 런타임 검증 불가
- README에 자주 겪는 오류 설명 없음

## 목표

`python -m pytest` ERROR 0개, 이전 통과 테스트 모두 유지.

## 범위

1. `pyproject.toml` + `.gitignore` — basetemp 로컬 설정
2. `notion_auto_organizer/exceptions.py` 신규 — 커스텀 예외 계층
3. `notion_auto_organizer/organizer.py` — RuntimeError → NotionError/AIClientError
4. `notion_auto_organizer/ai/client.py` — `@runtime_checkable` 추가
5. `README.md` — 트러블슈팅 섹션 추가

## 단계

1. pyproject.toml addopts 추가, .gitignore 추가
2. exceptions.py 생성
3. organizer.py 예외 교체
4. ai/client.py @runtime_checkable 추가
5. README.md 트러블슈팅 섹션 추가
6. python -m pytest 실행

## 검증

`python -m pytest` → 0 errors
