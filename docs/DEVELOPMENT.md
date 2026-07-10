# Development

## Setup

```powershell
python -m pip install -e ".[dev]"
```

Python 3.10 이상이 필요하다. LangChain provider 의존성은 `pyproject.toml`에 정의되어 있다.

## Tests

전체 테스트:

```powershell
python -m pytest
```

테스트는 provider 요청을 mock하고 provider 선택, agent 결과 추출, Markdown 변환, Notion chunking, AI 실패 시 페이지 교체 방지를 검증한다.

실제 API 호출 테스트는 unit test에 넣지 않고 짧은 prompt로 별도 확인한다.

## Run

```powershell
python -m notion_auto_organize --page-id "<PAGE_ID>"
```

실행 순서는 원본 백업, AI 정리, 결과 저장, Notion 페이지 교체다. `backups/`에는 원본이, `posts/`에는 AI 결과가 저장된다.

## Safety Rules

- `.env`의 token과 key를 commit하거나 로그에 출력하지 않는다.
- 첫 실행은 테스트용 Notion 페이지에서 수행한다.
- AI 호출이 실패하면 기존 Notion page를 교체하지 않는다.
- 백업과 결과 파일은 source control에 포함하지 않는다.
- provider 구현 변경 시 해당 client와 config/factory 테스트를 함께 수정한다.
