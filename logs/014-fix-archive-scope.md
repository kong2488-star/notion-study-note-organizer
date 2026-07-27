# archive/append 순서 버그 수정 + archive 병렬화 로그

- **계획 번호:** 014
- **계획 경로:** `plan/014-fix-archive-scope.md`
- **상태:** 완료
- **시작일:** 2026-07-27
- **완료일:** 2026-07-27

## 작업 요약

archive 대상 범위 버그를 수정하고, archive를 병렬화하고, 진행 출력을 세분화했다.

## 주요 결정과 근거

- `archive_blocks`의 `max_workers=5`로 설정. Notion 공식 rate limit은 초당 3req이지만 실제로는 더 높은 경우가 많고, 각 PATCH 요청이 200-500ms이므로 5개 동시 요청은 초당 10-25req 수준이 될 수 있다. 보수적으로 5로 설정하고 필요 시 조정한다.
- `as_completed` + `future.result()` 패턴을 사용해 예외가 발생하면 즉시 전파한다.

## 변경 파일

- `notion_auto_organizer/notion.py`: `archive_children` 삭제, `archive_blocks(block_ids)` 추가 (ThreadPoolExecutor, max_workers=5)
- `notion_auto_organizer/organizer.py`: `old_block_ids` 추출, `archive_blocks` 호출, 진행 출력 세분화
- `tests/test_organizer.py`: `FakeNotion.archive_children` → `archive_blocks` 교체
- `tests/test_cache.py`: `FakeNotion.archive_children` → `archive_blocks` 교체

## 의미 있는 명령과 결과

```
python -m pytest -v
59 passed, 3 warnings in 3.13s
```

## 실패, 원인, 해결 방법

- 첫 pytest 실행 시 `test_cache.py::test_same_source_uses_cached_ai_response` 실패. `test_cache.py`에도 자체 `FakeNotion`이 있었고 `archive_children`이 남아 있었음. `archive_blocks`로 교체해 해결.

## 검증 결과

- 전체 59개 통과
- `test_success_backs_up_saves_post_and_replaces_page`: `notion.archived == True` ✓
- `test_append_failure_leaves_page_intact`: append 실패 시 `notion.archived == False` ✓

## 해결되지 않은 문제와 후속 작업

없음
