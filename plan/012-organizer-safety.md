# 012 organizer 안전성 수정 + 에러 문서화

- **상태:** 완료

## 동기

코드베이스 분석에서 발견된 실질적인 버그와 구조 불일치를 수정한다.

- `archive_children` 성공 후 `append_children` 실패 시 Notion 페이지가 빈 상태로 남는 데이터 손실 위험이 있다.
- 빈 페이지에서 AI를 호출하면 빈 문자열이 그대로 전달된다.
- post 파일은 타임스탬프 없이 덮어써지는 반면 backup은 타임스탬프로 보존된다.
- `HttpError`가 `exceptions.py`가 아닌 `http.py`에 정의되어 예외 계층이 두 군데에 분산되어 있다.
- 에러 발생 조건과 각 실패 시나리오에서의 Notion 페이지 상태가 문서화되어 있지 않다.

## 목표

- `organize_page`의 Notion 교체 단계가 실패해도 원본 페이지 콘텐츠가 보존된다.
- 빈 페이지 실행 시 AI 호출 없이 명확한 에러가 발생한다.
- backup과 post 파일이 같은 타임스탬프 기반 명명 규칙을 따른다.
- 예외 클래스가 `exceptions.py` 한 곳에 모인다.
- `docs/ERRORS.md`에 에러 계층과 각 실패 시나리오가 문서화된다.

## 범위

포함:
- `organizer.py`: append/archive 순서 뒤집기, 빈 페이지 early return, post 타임스탬프 추가
- `exceptions.py`: `HttpError` 추가
- `http.py`: `HttpError` 클래스 삭제 후 `exceptions`에서 import
- `tests/test_organizer.py`: 테스트 2개 추가
- `docs/ERRORS.md`: 신규 생성

제외:
- `--refresh` 범위 문제 (항목 3), heading 처리 (항목 4), 진행 출력 (항목 5) 등 나머지 개선 사항

## 단계

1. `exceptions.py`에 `HttpError` 추가
2. `http.py`에서 `HttpError` 클래스 삭제, `exceptions`에서 import
3. `organizer.py` 수정 (append/archive 순서, 빈 페이지 체크, post 타임스탬프)
4. `tests/test_organizer.py`에 테스트 2개 추가
5. `docs/ERRORS.md` 신규 생성
6. `python -m pytest` 실행 및 통과 확인

## 검증

```powershell
python -m pytest
```

- `test_append_failure_leaves_page_intact`: archive가 호출되지 않았는지 확인
- `test_empty_page_raises_before_ai_or_notion_write`: `OrganizationError` 발생 확인
- 기존 테스트 5개 모두 통과
