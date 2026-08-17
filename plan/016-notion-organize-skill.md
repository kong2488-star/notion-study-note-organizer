# 016 네이티브 Claude Code Skill로 Notion 정리 제공

- **상태:** 진행 중

## 동기

기존 Python CLI 앱은 Notion 페이지를 읽어 외부 AI 제공자(Gemini/OpenAI)에게
"입문자 친화 한국어 학습 문서"로 정리를 맡기고 페이지를 교체한다. 이 정리 작업을
Claude Code에서 직접 수행하려면 정리 AI를 Claude 본인이 담당하고 Notion 읽기/쓰기를
연결된 Notion MCP로 처리하는 네이티브 skill이 필요하다. 이렇게 하면 외부 AI
제공자·API 키·`ai/` 서브패키지·블록 변환/append/archive 기계장치 없이 같은 결과를
얻을 수 있다. 기존 Python 앱은 그대로 유지한다(공존).

## 목표

- `.claude/skills/notion-organize/SKILL.md` 하나로 다음 워크플로우를 제공한다:
  Notion MCP로 페이지 읽기 → 원본 로컬 백업 → Claude가 프롬프트 규칙대로 정리 →
  성공 시에만 Notion MCP로 페이지 내용 교체.
- 외부 AI 제공자·API 키 없이 동작한다.
- 기존 Python 코드/테스트는 변경하지 않는다.

**성공 기준:** 테스트 페이지에서 (a) 원본 백업 파일 생성, (b) 프롬프트 규칙에 맞는
정리본으로 페이지 교체, (c) 정리 실패 시 페이지 미교체.

## 범위

포함:
- 신규 `.claude/skills/notion-organize/SKILL.md` (지시문만).
  - `notion_auto_organizer/ai/client.py:7-23`의 `NOTE_ORGANIZER_PROMPT` 전문 이식.
  - Markdown 서식 규칙(schema 렌더러 대체): heading `#/##/###`, bullet `- `,
    numbered `1. `, todo `- [ ]/[x]`, quote `> `, code fence, divider `---`.
    text에 인라인 서식(`**` `*` `~~` 백틱 링크) 금지.
  - 안전 워크플로우: fetch → 백업 저장 → 정리 → 성공 시에만 교체.
  - 백업 규칙: `backups/{slug}-{YYYYMMDD-HHMMSS}.md` (원본만).
  - 교체: `notion-update-page` `command=replace_content`, `new_str=<정리 Markdown>`,
    `allow_deleting_content` 미설정(기본 false)으로 하위 페이지 보호.
- `AGENTS.md`에 skill 사용법 한 줄 추가.

제외:
- 캐시, Pydantic 스키마/블록 변환, `--refresh` 이식 (불필요).
- 기존 Python 코드 삭제/수정/리팩토링.
- 정리 결과의 `posts/` 로컬 저장 (제거하기로 결정).

## 단계

1. 저장소 규칙 파일 생성: `plan/016`, `logs/016`.
2. MCP 교체 의미 확인: `notion-update-page` 스키마의 `replace_content`/`new_str`가
   전체 내용 교체임을 확인(스키마 검증 완료).
3. `.claude/skills/notion-organize/SKILL.md` 작성.
4. `AGENTS.md`에 skill 사용법 한 줄 추가.
5. 엔드투엔드 실행(사용자 제공 테스트 페이지)과 실패 안전 확인.

## 검증

- 정상 경로: 테스트 페이지 실행 후 `backups/`에 원본 백업 존재, 페이지가 규칙에 맞게
  교체됨(level 1은 제목만, 개념 아래 code 블록, 인라인 서식 없음).
- 실패 안전: 빈 페이지/백업 실패 상황에서 페이지 미교체 확인.
- 기존 앱 무손상: `python -m pytest` 통과, `git diff --stat`에
  `notion_auto_organizer/` 아래 변경 없음.
