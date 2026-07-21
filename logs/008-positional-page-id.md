# page-id 위치 인자 변경 로그

- **계획 번호:** 008
- **계획 경로:** `plan/008-positional-page-id.md`
- **상태:** 완료
- **시작일:** 2026-07-21
- **완료일:** 2026-07-21

## 작업 요약

`--page-id` 옵션을 위치 인자 `page_id`로 변경해 `notion-auto-organizer "<PAGE_ID>"` 형태로 실행할 수 있게 됐다.

## 주요 결정과 근거

없음

## 변경 파일

- `notion_auto_organizer/cli.py` — `--page-id` 필수 옵션 → `page_id` 위치 인자
- `tests/test_cli.py` — 호출부 3곳 갱신, 에러 메시지 검증 `--page-id` → `page_id`
- `AGENTS.md` — 명령어 예시 갱신
- `docs/DEVELOPMENT.md` — 명령어 예시 갱신

## 의미 있는 명령과 결과

```
python -m pytest tests/test_cli.py -v
```
5 passed

## 실패, 원인, 해결 방법

없음

## 검증 결과

- `python -m pytest tests/test_cli.py -v` → 5 passed ✅

## 해결되지 않은 문제와 후속 작업

없음
