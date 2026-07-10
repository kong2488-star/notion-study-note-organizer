# AI Providers

## Provider Selection

`.env`의 `AI_PROVIDER`로 사용할 provider를 선택한다.

```env
AI_PROVIDER=gemini
```

지원 값은 `gemini`와 `openai`다. 생략하면 Gemini가 기본값으로 사용된다.

## Gemini

```env
GEMINI_API_KEY=your-gemini-key
GEMINI_MODEL=gemini-2.5-flash-lite
```

`GeminiClient`는 `langchain-google-genai`의 `ChatGoogleGenerativeAI`를 사용한다.

## OpenAI-Compatible Proxy

```env
PROXY_TOKEN=your-proxy-token
CHAT_PROXY_URL=https://your-proxy.example/v1
OPENAI_MODEL=your-model
```

`PROXY_TOKEN`은 API key로 전달되고, `CHAT_PROXY_URL`은 `ChatOpenAI`의 `base_url`로 전달된다. 이 설정은 HTTP 네트워크 proxy가 아니라 OpenAI-compatible API endpoint를 의미한다.

## Shared Contract

모든 provider는 다음 메서드를 제공해야 한다.

```python
class AIClient(Protocol):
    def organize_markdown(self, markdown: str) -> str:
        ...
```

provider-specific SDK와 응답 형식은 각 client 내부에서 처리하고, organizer에는 정리된 Markdown 문자열만 반환한다.

## Embeddings

`EMBEDDING_PROXY_URL`과 `OPENAI_EMBEDDING_MODEL`은 향후 검색/RAG 기능을 위한 설정이다. 현재 Notion note organization 경로에서는 사용하지 않는다.

## Connection Check

전체 Notion 페이지를 보내기 전에 짧은 prompt로 provider 연결을 확인한다. 실제 페이지 실행은 테스트용 Notion 페이지에서 먼저 수행한다.
