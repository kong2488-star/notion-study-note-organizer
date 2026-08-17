# 016 네이티브 Claude Code Skill로 Notion 정리 제공 로그

- **계획 번호:** 016
- **계획 경로:** `plan/016-notion-organize-skill.md`
- **상태:** 완료
- **시작일:** 2026-08-17
- **완료일:** 2026-08-17

## 작업 요약

기존 Python 앱의 정리 워크플로우를 외부 AI 제공자 없이 Claude + Notion MCP로
수행하는 네이티브 skill(`.claude/skills/notion-organize/SKILL.md`)을 추가한다.
기존 Python 코드는 변경하지 않는다.

## 주요 결정과 근거

- 정리 규칙은 `client.py`의 `NOTE_ORGANIZER_PROMPT` 전문을 그대로 이식. crown jewel.
- Pydantic 스키마/렌더러는 이식하지 않음: Claude가 Markdown을 직접 생성하고 MCP가
  Markdown을 소비하므로 결정적 고정 장치가 불필요.
- 캐시 미이식: Claude 인라인 정리에는 유료 API 재호출 비용이 없어 YAGNI.
- 페이지 교체는 `notion-update-page` `replace_content`/`new_str` 사용. 스키마상
  전체 내용 교체이며 `allow_deleting_content` 기본 false라 하위 페이지가 있으면
  덮어쓰지 않고 에러 → 안전 기본값이므로 미설정 유지.
- 정리 결과 `posts/` 로컬 저장은 제거(사용자 요청). 원본 백업만 유지.

## 변경 파일

- `plan/016-notion-organize-skill.md`: 신규 계획.
- `logs/016-notion-organize-skill.md`: 본 로그.
- `.claude/skills/notion-organize/SKILL.md`: skill 본체(정리 규칙 + 안전 워크플로우).
- `AGENTS.md`: skill 사용법 한 줄 추가.

## 의미 있는 명령과 결과

- `python -m pytest -q` → `60 passed` (기존 테스트 전부 통과, 회귀 없음).
- `git diff --stat -- notion_auto_organizer/` → 변경 없음(Python 코드 무손상 확인).

## 실패, 원인, 해결 방법

없음

## 검증 결과

- 기존 앱 무손상: `python -m pytest` 60 passed. 통과.
- Python 코드 변경 없음: `git status`상 변경은 `AGENTS.md`, `.claude/skills/`,
  `plan/016`, `logs/016`뿐. 통과.
- MCP 교체 안전성: `notion-update-page` 스키마에 `replace_content`/`new_str`(전체
  내용 교체), `allow_deleting_content` 기본 false(하위 페이지 보호) 확인. 통과.
- 엔드투엔드 실행: 통과. 테스트 페이지 "기획 3번째 강의"
  (`3bf9cc0317cf80dea5d9d5b461bf6462`)로 실행 →
  `notion-fetch`로 원본 읽기 →
  `backups/기획-3번째-강의-20260817-124450.md`에 원본 백업 생성 →
  정리 규칙대로 다듬어 `notion-update-page`(`replace_content`)로 교체 →
  재조회로 반영 확인. level 1은 전체 제목에만, 개념 heading 아래 code 블록 + 설명,
  본문 인라인 서식 없음 등 규칙 준수 확인.

## 해결되지 않은 문제와 후속 작업

없음
