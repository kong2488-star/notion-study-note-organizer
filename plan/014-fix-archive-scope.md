# 014 archive/append 순서 버그 수정 + archive 병렬화

- **상태:** 완료

## 동기

012에서 append → archive 순서로 바꿨지만, `archive_children`이 내부적으로 `list_block_children`을 다시 호출하기 때문에 append 이후 시점의 전체 블록(구 블록 + 새 블록)을 모두 가져와 전부 archive한다. 페이지가 빈 상태가 되는 실제 데이터 손실 버그다.

추가로, archive를 순차 실행하는 것이 느리므로 `ThreadPoolExecutor`로 병렬화한다.

## 목표

- append 이후 archive가 구 블록 ID만 대상으로 동작한다.
- archive 병렬 실행으로 속도가 개선된다.
- 단계별 진행 출력이 블록 수를 포함해 더 구체적으로 표시된다.

## 범위

포함:
- `notion.py`: `archive_children` 삭제, `archive_blocks(block_ids)` 추가 (ThreadPoolExecutor)
- `organizer.py`: `old_block_ids` 추출, `archive_blocks` 호출, 진행 출력 세분화
- `tests/test_organizer.py`: `FakeNotion.archive_children` → `archive_blocks` 교체

제외: 다른 파일

## 단계

1. `notion.py`: `archive_children` 삭제, `archive_blocks` 추가
2. `organizer.py`: `old_block_ids` 추출, 진행 출력 개선, `archive_blocks` 호출
3. `tests/test_organizer.py`: `FakeNotion` 메서드 교체
4. `python -m pytest` 실행 및 통과 확인

## 검증

```powershell
python -m pytest
```

- 전체 59개 통과
