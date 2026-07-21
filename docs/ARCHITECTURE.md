# 아키텍처

## 목적

이 프로젝트는 Notion 페이지에서 정리되지 않은 개발 학습 메모를 읽고, 블록 트리를 Markdown으로 변환하고, 선택한 AI 제공자를 통해 입문자 친화적인 한국어 학습 문서로 내용을 정리한 뒤, 정리된 결과로 페이지 내용을 교체합니다.

## 데이터 흐름

```text
Notion page
  -> NotionClient: load block tree
  -> blocks_to_markdown: convert original content to Markdown
  -> backups/: save original Markdown
  -> AIClient: call the selected LangChain agent
  -> posts/: save organized result
  -> markdown_to_blocks: convert organized Markdown back to Notion blocks
  -> NotionClient: archive existing children and append new blocks
```

AI 호출이나 Markdown 정리 단계가 실패하면 보관 처리 단계가 실행되지 않으므로 기존 Notion 페이지 내용은 그대로 유지됩니다.

## 모듈 경계

- `notion.py`: Notion API 요청, 블록 트리 불러오기, 보관 처리, 추가 단위 분할을 담당합니다.
- `markdown_convert.py`: Notion 블록과 Markdown 간 변환을 담당합니다.
- `organizer.py`: 백업, AI 호출, 출력 저장, 페이지 교체를 조정합니다.
- `ai/client.py`: 공통 `AIClient` 프로토콜, 프롬프트, 구조화 응답 실행 로직을 정의합니다.
- `ai/schema.py`: agent 응답을 고정하는 Pydantic 블록 스키마(`OrganizedNote`)와 이를 Markdown으로 렌더링하는 함수를 정의합니다.
- `ai/gemini.py`: LangChain Gemini 채팅 모델과 에이전트를 구현합니다.
- `ai/openai.py`: OpenAI 호환 LangChain 채팅 모델과 에이전트를 구현합니다.
- `ai/factory.py`: `AI_PROVIDER`를 기준으로 제공자 구현을 선택합니다.
- `config.py`: Pydantic Settings를 통해 `.env`를 읽고 공통 제공자 설정을 검증합니다.

새 제공자를 추가할 때는 `AIClient.organize_markdown()`을 구현하고 제공자별 클라이언트 로직을 해당 제공자 모듈 안에 격리하세요. `NotionPageOrganizer`는 선택된 AI 제공자와 독립적이어야 합니다.
