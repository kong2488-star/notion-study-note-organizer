# AI 제공자

## 공통 설정

애플리케이션은 Pydantic Settings와 python-dotenv를 통해 `.env`를 읽습니다. 프로세스 환경변수가 `.env`의 값보다 우선합니다.

```env
NOTION_TOKEN=your-notion-token
AI_PROVIDER=gemini
AI_API_KEY=your-provider-key
AI_MODEL=your-model
```

네 값은 모두 필수입니다. `AI_PROVIDER`에는 기본값이 없으며 현재 `gemini` 또는 `openai`를 허용합니다.

## Gemini

`gemini`를 선택하고 공통 필드에 Gemini API 키와 모델을 입력하세요.

```env
AI_PROVIDER=gemini
AI_API_KEY=your-gemini-key
AI_MODEL=gemini-2.5-flash-lite
```

Gemini에는 `AI_BASE_URL`을 설정하지 마세요. `GeminiClient`는 `langchain-google-genai`와 `ChatGoogleGenerativeAI`를 사용합니다.

## OpenAI와 호환 endpoint

OpenAI 공식 endpoint를 사용할 때는 `AI_BASE_URL`을 생략하세요.

```env
AI_PROVIDER=openai
AI_API_KEY=your-openai-key
AI_MODEL=your-model
```

OpenAI 호환 endpoint를 사용할 때는 base URL을 추가하세요.

```env
AI_PROVIDER=openai
AI_API_KEY=your-provider-key
AI_MODEL=your-model
AI_BASE_URL=https://your-proxy.example/v1
```

`AI_BASE_URL`이 있을 때만 `ChatOpenAI`에 전달됩니다.

## 공통 계약

모든 제공자는 다음 메서드를 구현합니다.

```python
class AIClient(Protocol):
    def organize_markdown(self, markdown: str) -> str:
        ...
```

제공자별 SDK 코드는 각 제공자 클라이언트 안에 유지합니다. organizer는 최종 Markdown 문자열만 받습니다.

## 연결 확인

실제 Notion 페이지를 전송하기 전에 짧은 프롬프트로 제공자 연결을 확인하세요. 작업이 성공하면 페이지 내용이 교체되므로 첫 테스트에는 샘플 Notion 페이지를 사용하세요.
