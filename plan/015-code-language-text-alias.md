# 015 code 블록 language "text" 별칭 추가

- **상태:** 초안

## 동기

AI가 코드펜스 언어로 `text`를 지정하면 `normalize_code_language()`가 아는 별칭에 `text`가 없어 그대로 통과시키고, Notion API가 허용 목록에 없는 값이라며 HTTP 400 validation_error를 반환한다. 이로 인해 새 블록 추가가 실패한다.

## 목표

`text` 언어가 Notion 허용 값인 `plain text`로 정규화되어 400 없이 code 블록이 추가되는 것. 성공 조건: 해당 별칭 매핑 단위 테스트 통과, 전체 `pytest` 통과.

## 범위

- `notion_auto_organizer/markdown_convert.py`의 `normalize_code_language()` `aliases`에 `"text": "plain text"` 추가.
- 제외: 허용 목록 전체 검증(폴백) 방식은 이번 작업에서 다루지 않음.

## 단계

1. `aliases`에 `"text": "plain text"` 추가 → 검증: 코드 리뷰로 한 줄 변경 확인.
2. `text`가 `plain text`로 정규화되는지 확인하는 테스트 추가 → 검증: 해당 테스트 통과.

## 검증

- `python -m pytest` 전체 통과.
