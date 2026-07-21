# 009 단계별 에러 컨텍스트 개선

- **상태:** 완료

## 동기

현재 모든 예외가 `cli.py`의 단일 `except Exception`에서 잡혀 "error: Not Found"처럼 어느 단계에서 실패했는지 알 수 없다. Notion API, AI API, 파일 I/O 등 각 단계를 구분할 수 있어야 한다.

## 목표

에러 메시지만 보고 어느 단계(Notion 읽기 / AI 정리 / Notion 쓰기 등)에서 실패했는지 즉시 파악할 수 있다.

## 범위

**포함:**
- `organizer.py`: 각 단계를 try/except로 감싸 컨텍스트 포함 예외로 재발생
- `cli.py`: `--debug` 플래그 추가 (traceback 출력)

**제외:** 예외 종류 추가, 재시도 로직

## 단계

1. `organizer.py` 각 단계 래핑
   - Notion 페이지 정보 조회
   - Notion 블록 읽기
   - 백업 저장
   - AI 정리
   - Notion 기존 블록 보관
   - Notion 새 블록 추가
2. `cli.py` `--debug` 플래그 추가
3. `tests/test_organizer.py` 에러 메시지 검증 갱신
4. `python -m pytest` 실행

## 검증

`python -m pytest tests/test_organizer.py` 통과
