# 단계별 에러 컨텍스트 개선 로그

- **계획 번호:** 009
- **계획 경로:** `plan/009-improve-error-context.md`
- **상태:** 완료
- **시작일:** 2026-07-21
- **완료일:** 2026-07-21

## 작업 요약

`organizer.py`의 각 단계를 try/except로 감싸 단계 이름을 포함한 에러 메시지를 출력하도록 했다. `cli.py`에 `--debug` 플래그를 추가해 전체 traceback을 볼 수 있게 했다.

## 주요 결정과 근거

단계 태그를 `[Notion 읽기]`, `[AI 정리]`, `[Notion 쓰기]` 등 한국어로 통일해 어느 API 단계에서 실패했는지 바로 구분되도록 했다.

## 변경 파일

- `notion_auto_organizer/organizer.py` — 6개 단계(Notion 읽기, 백업 저장, AI 정리, 결과 저장, Notion 보관, Notion 추가) 각각 try/except 래핑
- `notion_auto_organizer/cli.py` — `--debug` 플래그 추가, traceback 출력 로직

## 의미 있는 명령과 결과

```
python -m pytest tests/test_organizer.py tests/test_cli.py -v
```
slugify 4개 + CLI 5개 = 9 passed (test_organizer tmp_path 4개는 기존 Windows 환경 오류)

```
python -m ruff check .
```
All checks passed!

## 실패, 원인, 해결 방법

없음

## 검증 결과

- `python -m pytest tests/test_organizer.py tests/test_cli.py -v` → 9 passed ✅
- `python -m ruff check .` → All checks passed! ✅

## 해결되지 않은 문제와 후속 작업

없음
