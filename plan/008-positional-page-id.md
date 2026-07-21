# 008 page-id를 위치 인자로 변경

- **상태:** 완료

## 동기

`--page-id` 플래그가 필수 옵션으로 되어 있어 명령어가 불필요하게 길다.
위치 인자로 바꾸고 스크립트 명령을 함께 사용하면 최단 명령이 가능하다.

```
# 변경 전
python -m notion_auto_organizer --page-id "<PAGE_ID>"

# 변경 후
notion-auto-organizer "<PAGE_ID>"
```

## 목표

`page_id`를 위치 인자로 받아 명령어를 단축한다.

## 범위

**포함:**
- `cli.py`: `--page-id` → 위치 인자 `page_id`
- `tests/test_cli.py`: 호출부와 에러 메시지 검증 갱신
- `AGENTS.md`: 명령어 예시 갱신
- `docs/DEVELOPMENT.md`: 명령어 예시 갱신

**제외:** 나머지 로직 변경 없음

## 단계

1. `cli.py` `--page-id` → `page_id` 위치 인자로 변경
2. `tests/test_cli.py` 호출부 3곳 갱신, 에러 메시지 검증 갱신
3. `AGENTS.md` 명령어 예시 갱신
4. `docs/DEVELOPMENT.md` 명령어 예시 갱신
5. `python -m pytest` 실행

## 검증

`python -m pytest` 통과
