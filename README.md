# Notion Developer Study Note Organizer

Notion page의 개발 공부 메모를 읽고 LangChain agent로 입문-초급 학습 노트 Markdown을 만든 뒤, 결과를 같은 Notion page에 다시 작성하는 Python CLI입니다.

## Documentation

- [Architecture](docs/ARCHITECTURE.md)
- [AI Providers](docs/AI_PROVIDERS.md)
- [Development](docs/DEVELOPMENT.md)

## Supported AI Providers

`AI_PROVIDER`로 사용할 provider를 선택합니다.

```env
NOTION_TOKEN=
AI_PROVIDER=gemini

GEMINI_API_KEY=
GEMINI_MODEL=gemini-2.5-flash-lite

PROXY_TOKEN=
CHAT_PROXY_URL=
OPENAI_MODEL=

EMBEDDING_PROXY_URL=
OPENAI_EMBEDDING_MODEL=
```

Gemini는 `GEMINI_API_KEY`와 `GEMINI_MODEL`을 사용합니다. OpenAI-compatible proxy는 `PROXY_TOKEN`, `CHAT_PROXY_URL`, `OPENAI_MODEL`을 사용합니다. Embedding 설정은 현재 기능에서 사용하지 않습니다.

## Installation

Python 3.10 이상이 필요합니다.

```powershell
python -m pip install -e ".[dev]"
python -m pytest
```

## Notion Integration

1. Notion integrations에서 integration을 생성합니다.
2. integration token을 `.env`의 `NOTION_TOKEN`에 입력합니다.
3. 대상 Notion page에서 integration을 공유합니다.
4. page를 읽고 수정할 수 있는 권한을 부여합니다.

## Run

```powershell
python -m notion_auto_organizer --page-id "NOTION_PAGE_ID"
```

`pip install -e .` 후에는 콘솔 명령으로도 실행할 수 있습니다. `--page-id`에는 페이지 ID 또는 Notion page URL을 그대로 넣을 수 있습니다.

```powershell
notion-auto-organizer --page-id "https://www.notion.so/workspace/페이지제목-1a2b3c..."
```

실행 순서는 원본 백업, AI 정리, 결과 저장, Notion page 교체입니다.

## Output and Safety

- `backups/`: 교체 전 Notion 원본 Markdown
- `posts/`: AI가 생성한 정리 결과 Markdown
- `.env`: 실제 token과 key를 저장하며 Git에 포함하지 않습니다.

AI 호출 또는 정리 결과 생성에 실패하면 기존 Notion page를 교체하지 않습니다. 처음에는 테스트용 page에서 실행하세요.
