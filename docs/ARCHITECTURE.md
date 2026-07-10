# Architecture

## Purpose

이 프로젝트는 하나의 Notion 페이지에 작성된 개발 공부 메모를 읽어 구조화된 Markdown 학습 노트로 만들고, 성공한 결과만 같은 페이지에 다시 작성한다.

## Data Flow

```text
Notion page
  -> NotionClient: block tree 읽기
  -> blocks_to_markdown: 원본 Markdown 변환
  -> backups/: 원본 저장
  -> AIClient: 선택된 LangChain agent 호출
  -> posts/: 정리 결과 저장
  -> markdown_to_blocks: Notion block 변환
  -> NotionClient: 기존 children archive 후 새 block append
```

AI 호출 또는 Markdown 변환이 실패하면 archive 단계에 도달하지 않으므로 기존 페이지 내용은 유지된다.

## Module Boundaries

- `notion.py`: Notion API 요청과 block pagination/chunking만 담당한다.
- `markdown_convert.py`: Notion block과 Markdown 사이의 변환만 담당한다.
- `organizer.py`: 백업, AI 호출, 결과 저장, 페이지 교체 순서를 조정한다.
- `ai_client.py`: provider 공통 Protocol, prompt, agent 결과 추출을 제공한다.
- `gemini_client.py`: LangChain Gemini chat model과 agent를 만든다.
- `openai_client.py`: OpenAI-compatible proxy용 LangChain chat model과 agent를 만든다.
- `ai_factory.py`: `AI_PROVIDER` 설정에 따라 provider 구현체를 생성한다.
- `config.py`: `.env` 로딩과 provider별 필수 설정 검증을 담당한다.

새 provider를 추가할 때 `NotionPageOrganizer`를 수정하지 않고 `AIClient`를 구현한 client와 factory 분기만 추가한다.
