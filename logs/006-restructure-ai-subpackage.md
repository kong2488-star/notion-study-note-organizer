# AI 서브패키지 분리 로그

- **계획 번호:** 006
- **계획 경로:** `plan/006-restructure-ai-subpackage.md`
- **상태:** 완료
- **시작일:** 2026-07-21
- **완료일:** 2026-07-21

## 작업 요약

`notion_auto_organizer/ai/` 서브패키지를 신규 생성하고 AI 관련 파일 5개를 이동했다. `organizer.py`, `cli.py`, 테스트 5개의 import를 갱신하고 기존 플랫 파일을 삭제했다. `AGENTS.md`와 `docs/ARCHITECTURE.md`의 파일 경로 참조도 갱신했다.

## 주요 결정과 근거

- `ai/__init__.py`에서 모든 public 심볼을 재수출해 외부 코드가 `from .ai import AIClient` 등으로 단일 진입점을 사용할 수 있도록 했다.
- 내부 파일 간에는 상대 import를 사용했다(`factory.py`에서 `..config`).
- 파일명에서 `_client` 접미사를 제거했다(`gemini_client.py` → `gemini.py`). 서브패키지 컨텍스트에서 접미사가 불필요하다.

## 변경 파일

**신규 생성:**
- `notion_auto_organizer/ai/__init__.py`
- `notion_auto_organizer/ai/client.py`
- `notion_auto_organizer/ai/schema.py`
- `notion_auto_organizer/ai/gemini.py`
- `notion_auto_organizer/ai/openai.py`
- `notion_auto_organizer/ai/factory.py`

**수정:**
- `notion_auto_organizer/organizer.py` — `.ai_client` → `.ai`
- `notion_auto_organizer/cli.py` — `.ai_factory` → `.ai`
- `tests/test_ai_client.py` — import 경로 갱신
- `tests/test_ai_factory.py` — import 경로 갱신
- `tests/test_note_schema.py` — import 경로 갱신
- `tests/test_gemini_client.py` — import 경로 갱신
- `tests/test_openai_client.py` — import 경로 갱신
- `AGENTS.md` — 주요 파일 섹션 경로 갱신
- `docs/ARCHITECTURE.md` — 모듈 경계 섹션 경로 갱신

**삭제:**
- `notion_auto_organizer/ai_client.py`
- `notion_auto_organizer/note_schema.py`
- `notion_auto_organizer/ai_factory.py`
- `notion_auto_organizer/gemini_client.py`
- `notion_auto_organizer/openai_client.py`

## 의미 있는 명령과 결과

```
python -m pytest
```
- 57개 수집
- 48개 통과, 9개 ERROR (모두 `tmp_path` 픽스처의 Windows 권한 문제 — `PermissionError: [WinError 5]`, 이번 변경과 무관한 기존 환경 오류)
- AI 관련 테스트(`test_ai_client`, `test_ai_factory`, `test_note_schema`, `test_gemini_client`, `test_openai_client`) 전원 통과

## 실패, 원인, 해결 방법

`test_cache.py`, `test_config.py`, `test_organizer.py`에서 `tmp_path` 픽스처 setup 단계에 `PermissionError: [WinError 5]` 발생.
원인: pytest가 `C:\Users\User\AppData\Local\Temp\pytest-of-User` 디렉토리에 접근 불가 — Windows 권한 문제로 이번 변경 이전부터 존재하던 환경 오류.
해결: 이번 작업 범위 밖. 별도 대응 필요.

## 검증 결과

- AI 관련 테스트 9개(`test_ai_client` 3, `test_ai_factory` 2, `test_note_schema` 3, `test_gemini_client` 1, `test_openai_client` 2) 전원 통과 ✅
- 기타 비AI 테스트(`test_cli` 5, `test_http` 4, `test_markdown_convert` 3, `test_notion` 11) 전원 통과 ✅
- `tmp_path` 의존 테스트 9개는 기존 환경 오류로 제외

## 해결되지 않은 문제와 후속 작업

- `test_cache.py`, `test_config.py`, `test_organizer.py`의 `tmp_path` 권한 오류 미해결 — 별도 계획 필요
