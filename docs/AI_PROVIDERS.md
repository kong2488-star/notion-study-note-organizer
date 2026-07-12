# AI Providers

## Provider Selection

Choose the provider in `.env` with `AI_PROVIDER`.

```env
AI_PROVIDER=gemini
```

Valid values are currently `gemini` and `openai`. If the variable is omitted, Gemini is used by default.

## Gemini

```env
GEMINI_API_KEY=your-gemini-key
GEMINI_MODEL=gemini-2.5-flash-lite
```

`GeminiClient` uses `langchain-google-genai` and `ChatGoogleGenerativeAI`.

## OpenAI-Compatible Proxy

```env
PROXY_TOKEN=your-proxy-token
CHAT_PROXY_URL=https://your-proxy.example/v1
OPENAI_MODEL=your-model
```

`PROXY_TOKEN` is passed as the API key, and `CHAT_PROXY_URL` is passed as the `base_url` for `ChatOpenAI`. This setup is intended for OpenAI-compatible API endpoints, not a generic HTTP streaming proxy.

## Shared Contract

All providers must implement the following method:

```python
class AIClient(Protocol):
    def organize_markdown(self, markdown: str) -> str:
        ...
```

Provider-specific SDK code should stay inside each provider client. The organizer should only receive the final Markdown string.

## Embeddings

`EMBEDDING_PROXY_URL` and `OPENAI_EMBEDDING_MODEL` are reserved for future embedding-based RAG support. They are not used in the current Notion note organization flow.

## Connection Check

Before sending a real Notion page, verify the provider connection with a short prompt. Run the first test against a sample Notion page, because a successful workflow replaces the page contents.
