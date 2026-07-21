# 프로젝트 에이전트 지침

## 목적

이 프로젝트는 하나의 Notion 페이지에서 정리되지 않은 개발 학습 메모를 읽고, 블록을 Markdown으로 변환한 뒤, 선택한 AI 제공자에게 입문자 친화적인 한국어 학습 문서로 정리하도록 요청하고, 정리된 결과로 페이지 내용을 교체합니다.

## 작업 흐름

1. `.env` 설정을 불러옵니다.
2. 대상 Notion 페이지와 블록 트리를 읽습니다.
3. 원본 블록을 Markdown으로 변환합니다.
4. 원본 Markdown을 `backups/`에 저장합니다.
5. 같은 원본에 대한 캐시된 AI 응답이 있으면 재사용하고, 없으면 Markdown을 선택한 AI 제공자에게 전송한 뒤 결과를 캐시에 저장합니다.
6. 정리된 Markdown을 `posts/`에 저장합니다.
7. AI 결과가 성공한 후에만 기존 Notion 하위 블록을 보관 처리하고 새 블록을 추가합니다.

AI 호출이나 정리 단계가 실패하면 Notion 페이지를 교체하지 마세요.

## 주요 파일

- `notion_auto_organizer/cli.py`: 명령줄 진입점입니다. 설정과 클라이언트를 조립하고 `organize_page()`를 호출합니다.
- `notion_auto_organizer/notion.py`: Notion API 클라이언트, 페이지 ID/URL 정규화, 블록 트리 불러오기, 보관 처리, 추가 단위 분할을 담당합니다.
- `notion_auto_organizer/http.py`: `urllib` 기반 경량 JSON HTTP 헬퍼입니다. `notion.py`가 사용합니다.
- `notion_auto_organizer/markdown_convert.py`: Notion 블록과 Markdown 간 변환을 담당합니다.
- `notion_auto_organizer/organizer.py`: 백업, AI 정리, 출력, 페이지 교체 작업 흐름을 담당합니다.
- `notion_auto_organizer/cache.py`: 원본 Markdown 기준 AI 응답 파일 캐시입니다. 같은 입력에 대한 재호출을 막습니다.
- `notion_auto_organizer/ai_client.py`: 공통 `AIClient` 프로토콜, 프롬프트, 구조화 응답 실행 로직을 정의합니다.
- `notion_auto_organizer/note_schema.py`: agent 응답을 고정하는 Pydantic 블록 스키마(`OrganizedNote`)와 Markdown 렌더러를 정의합니다.
- `notion_auto_organizer/gemini_client.py`: LangChain Gemini 제공자 구현입니다.
- `notion_auto_organizer/openai_client.py`: LangChain OpenAI 호환 제공자 구현입니다.
- `notion_auto_organizer/ai_factory.py`: `AI_PROVIDER`를 기준으로 제공자를 선택합니다.
- `notion_auto_organizer/config.py`: Pydantic 기반 `.env` 불러오기와 공통 AI 설정 검증을 담당합니다.

## 문서

- `docs/ARCHITECTURE.md`: 모듈 경계와 전체 데이터 흐름을 설명합니다.
- `docs/AI_PROVIDERS.md`: Gemini/OpenAI 설정과 제공자 계약을 설명합니다.
- `docs/DEVELOPMENT.md`: 설치, 테스트, 실행, 안전 규칙을 설명합니다.
- `docs/planning.md`: 필수 계획 수명 주기, 번호 부여, 실행, 완료 조건을 설명합니다.
- `docs/logging.md`: 필수 점진적 작업 로그 내용, 보안, 완료 규칙을 설명합니다.

아키텍처, AI 제공자, 개발 작업 흐름을 변경하기 전에 관련 문서를 읽으세요.

## 작업 계획과 작업 로그

- 저장소 파일을 변경하기 전에 `plan/TEMPLATE.md`에서 번호가 있는 계획을 만들고 승인을 받으세요. `docs/planning.md`를 읽고 따르세요.
- 승인된 계획이 진행 중 상태가 되면 즉시 `logs/TEMPLATE.md`에서 대응하는 작업 로그를 만드세요. 두 파일에 같은 세 자리 번호와 kebab-case 슬러그를 사용하세요.
- 작업 중에 로그를 계속 갱신하고 마지막에 한꺼번에 재구성하지 마세요. `docs/logging.md`를 읽고 따르세요.
- 문서와 주석 변경을 포함해 저장소를 변경하는 모든 작업에는 계획과 작업 로그가 필요합니다. 읽기 전용 작업은 제외됩니다.
- 코드, 테스트, 의존성, 생성 코드, 런타임에 영향을 주는 설정을 변경하면 `python -m pytest`를 실행하세요.
- 모든 필수 검증이 통과하고 작업 로그가 마무리되며 계획, 작업 로그, 변경 파일, 검증 결과가 서로 일치하기 전에는 작업 로그나 계획을 완료 상태로 표시하지 마세요.

## 제공자 선택

`.env`에서 `AI_PROVIDER`를 설정하세요.

```env
NOTION_TOKEN=...
AI_PROVIDER=gemini
AI_API_KEY=...
AI_MODEL=...
```

OpenAI 호환 프록시를 사용할 때는 다음과 같이 설정하세요.

```env
AI_PROVIDER=openai
AI_API_KEY=...
AI_MODEL=...
AI_BASE_URL=https://your-proxy.example/v1
```

`AI_PROVIDER`에는 기본값이 없습니다. Gemini 또는 OpenAI 공식 endpoint를 사용할 때는 `AI_BASE_URL`을 생략하세요. `.env`를 커밋하거나 API 키를 로그, 테스트, 오류 메시지에 노출하지 마세요.

## 명령어

프로젝트와 개발 의존성을 설치합니다.

```powershell
python -m pip install -e ".[dev]"
```

테스트를 실행합니다.

```powershell
python -m pytest
```

테스트용 Notion 페이지를 정리합니다.

```powershell
python -m notion_auto_organizer --page-id "<PAGE_ID>"
```

캐시된 AI 응답을 무시하고 다시 정리하려면 `--refresh`를 추가하세요.

```powershell
python -m notion_auto_organizer --page-id "<PAGE_ID>" --refresh
```

전체 Notion 페이지를 전송하기 전에 짧은 제공자 프롬프트를 실행하세요. 작업이 성공하면 페이지 내용이 교체되므로 첫 실행에는 테스트 페이지를 사용하세요.

## 코딩 규칙

- **Python** 코드 스타일은 PEP8을 따릅니다.
  - 일관된 스타일을 위해 Black 호환 **ruff format**을 사용하고 린트 검사에는 `ruff check`를 실행하세요.
  - 항상 타입 힌트를 포함하세요.
- 새 AI 제공자는 `AIClient.organize_markdown()`을 구현해야 합니다.
- 제공자별 SDK 코드는 해당 제공자 클라이언트 안에 유지하세요.
- `NotionPageOrganizer`가 선택된 AI 제공자와 독립적이도록 유지하세요.
- 페이지 교체 전에 백업하는 작업 흐름을 보존하세요.
- 생성된 `backups/`와 `posts/` 파일을 소스 제어에 포함하지 마세요.
- 제공자 선택, 응답 추출, Markdown 변환, 실패 안전성을 위한 단위 테스트를 추가하거나 갱신하세요.
- 동작을 문서화하고 실패 경로를 테스트하지 않은 상태로 자동 재시도나 새 외부 도구를 추가하지 마세요.
