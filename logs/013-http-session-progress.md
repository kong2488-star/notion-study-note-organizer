# HTTP 연결 재사용 + 진행 상황 출력 로그

- **계획 번호:** 013
- **계획 경로:** `plan/013-http-session-progress.md`
- **상태:** 완료
- **시작일:** 2026-07-27
- **완료일:** 2026-07-27

## 작업 요약

`requests.Session` 기반으로 HTTP 연결 재사용을 구현하고, `organizer.py`에 단계별 진행 출력을 추가했다.

## 주요 결정과 근거

- `urllib` 대신 `requests.Session`을 선택했다. stdlib `http.client.HTTPSConnection` 직접 사용은 stale connection 재연결 로직을 직접 구현해야 해 복잡성이 높다. `requests`는 이를 자동으로 처리하며, 이미 LangChain을 통해 환경에 설치되어 있다.
- 세션을 모듈 수준 `_session`으로 둔다. `NotionClient`에 session을 주입하면 `notion.py` 인터페이스가 바뀌고 테스트 구조도 크게 달라지므로, 가장 영향 범위가 작은 방식을 선택했다.
- `test_notion.py`는 `notion_module.request_json`을 monkeypatch하므로 변경 불필요하다.

## 변경 파일

- `pyproject.toml`: `requests>=2,<3` 명시적 의존성 추가
- `notion_auto_organizer/http.py`: `urllib` 제거, `requests.Session` 기반으로 전면 교체
- `tests/test_http.py`: monkeypatch 대상을 `urlopen` → `_session`으로 변경 (4개 테스트), `MagicMock` 활용
- `notion_auto_organizer/organizer.py`: 단계별 진행 출력 4곳 추가

## 의미 있는 명령과 결과

```
python -m pytest -v
59 passed, 3 warnings in 4.17s
```

## 실패, 원인, 해결 방법

없음

## 검증 결과

- `test_http.py` 4개 테스트 — `_session` monkeypatch 방식으로 통과
- `test_notion.py` — 변경 없이 통과 (`notion_module.request_json` monkeypatch 유지)
- 전체 59개 통과

## 해결되지 않은 문제와 후속 작업

없음
