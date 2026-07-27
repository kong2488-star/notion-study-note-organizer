# organizer 안전성 수정 + 에러 문서화 로그

- **계획 번호:** 012
- **계획 경로:** `plan/012-organizer-safety.md`
- **상태:** 완료
- **시작일:** 2026-07-27
- **완료일:** 2026-07-27

## 작업 요약

organizer 버그 수정 4건과 에러 문서 신규 생성을 완료했다.

## 주요 결정과 근거

- append → archive 순서로 뒤집었다. append 실패 시 원본이 보존되고, archive 실패 시 원본+새 블록 공존(수동 정리 가능)이 빈 페이지보다 훨씬 안전하다.
- `HttpError`는 `RuntimeError`를 상속하는 것을 유지했다. `OrganizationError`는 application-level 에러이고 `HttpError`는 transport-level이므로 계층을 섞지 않는다.

## 변경 파일

- `notion_auto_organizer/exceptions.py`: `HttpError(RuntimeError)` 추가
- `notion_auto_organizer/http.py`: `HttpError` 클래스 삭제, `exceptions`에서 import
- `notion_auto_organizer/organizer.py`: 빈 페이지 early return 추가, post 파일명 타임스탬프 추가, append/archive 순서 뒤집기
- `tests/test_organizer.py`: `FailingAppendNotion`, `EmptyNotion` fake 추가, 테스트 2개 추가
- `docs/ERRORS.md`: 에러 레퍼런스 문서 신규 생성

## 의미 있는 명령과 결과

```
python -m pytest -v
59 passed, 3 warnings in 3.35s
```

## 실패, 원인, 해결 방법

없음

## 검증 결과

- `test_append_failure_leaves_page_intact`: `FailingAppendNotion`이 raise하면 archive가 호출되지 않음 — 통과
- `test_empty_page_raises_before_ai_or_notion_write`: 빈 블록 반환 시 `OrganizationError` 발생, Notion 쓰기 호출 없음 — 통과
- 기존 테스트 57개 모두 통과

## 해결되지 않은 문제와 후속 작업

없음
