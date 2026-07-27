# 013 HTTP 연결 재사용 + 진행 상황 출력

- **상태:** 완료

## 동기

현재 `http.py`는 `urllib.request.urlopen`을 사용해 요청마다 새 TCP+TLS 연결을 맺는다. 모든 Notion API 호출이 `api.notion.com`으로 가므로 연결 재사용 시 호출당 50-150ms의 핸드셰이크 비용을 절감할 수 있다. 특히 `archive_children`처럼 블록 수만큼 순차 요청하는 메서드에서 효과가 크다.

또한 `organize_page`가 AI 호출(최대 수십 초) 등 긴 단계를 포함함에도 실행 중 아무 출력이 없어 사용자가 진행 여부를 확인할 방법이 없다.

## 목표

- 같은 호스트(`api.notion.com`)로의 Notion API 호출이 하나의 HTTPS 연결을 재사용한다.
- 각 주요 단계 시작 시 진행 메시지가 출력된다.

## 범위

포함:
- `pyproject.toml`: `requests>=2,<3` 추가
- `http.py`: `requests.Session` 기반으로 교체
- `tests/test_http.py`: monkeypatch 대상 변경 (4개 테스트)
- `organizer.py`: 단계별 진행 출력 추가 (4곳)

제외:
- `notion.py`, `test_notion.py`, `test_organizer.py` (변경 불필요)

## 단계

1. `pyproject.toml`에 `requests>=2,<3` 추가
2. `http.py`를 `requests.Session` 기반으로 교체
3. `tests/test_http.py` monkeypatch 대상 변경
4. `organizer.py`에 진행 출력 추가
5. `python -m pytest` 실행 및 통과 확인

## 검증

```powershell
python -m pytest
```

- 전체 59개 테스트 통과
