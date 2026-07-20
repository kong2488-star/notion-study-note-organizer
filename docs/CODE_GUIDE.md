# 코드 가이드 (CODE_GUIDE)

이 문서는 `notion_auto_organizer`의 모든 소스 코드를 파일 단위로 설명합니다.
코드를 처음 읽는 사람이 "어떤 파일이 무슨 일을 하고, 왜 그렇게 작성됐는지"를 이해할 수 있도록 작성했습니다.

## 목차

1. [프로젝트 개요와 전체 흐름](#1-프로젝트-개요와-전체-흐름)
2. [파일별 상세 설명](#2-파일별-상세-설명)
   - [`__init__.py` / `__main__.py`](#__init__py--__main__py--패키지-선언과-실행-진입점)
   - [`cli.py`](#clipy--명령줄-인터페이스)
   - [`config.py`](#configpy--환경변수-로딩과-검증)
   - [`organizer.py`](#organizerpy--핵심-워크플로우)
   - [`ai_client.py`](#ai_clientpy--ai-provider-공용-계층)
   - [`ai_factory.py`](#ai_factorypy--provider-선택-팩토리)
   - [`gemini_client.py` / `openai_client.py`](#gemini_clientpy--openai_clientpy--provider-구현체)
   - [`notion.py`](#notionpy--notion-api-클라이언트)
   - [`markdown_convert.py`](#markdown_convertpy--블록--markdown-양방향-변환)
   - [`cache.py`](#cachepy--ai-응답-파일-캐시)
   - [`http.py`](#httppy--경량-http-헬퍼)
3. [테스트 요약](#3-테스트-요약)
4. [설정 및 기타 파일](#4-설정-및-기타-파일)

---

## 1. 프로젝트 개요와 전체 흐름

이 프로젝트는 **대충 적어둔 Notion 개발 학습 메모를 AI로 정리해서, 구조화된 학습 노트로 페이지를 교체하는 CLI 도구**입니다.

### 실행 진입점

두 가지 방법으로 실행할 수 있고, 둘 다 결국 같은 함수(`cli.main()`)에 도달합니다.

```
python -m notion_auto_organizer --page-id <ID또는URL>
  └→ __main__.py  →  cli.main()

notion-auto-organizer --page-id <ID또는URL>     (pyproject.toml의 [project.scripts]로 설치된 콘솔 명령)
  └→ cli.main()
```

### 모듈 의존 그래프

화살표는 "import 한다"는 뜻입니다. 위쪽이 상위 계층, 아래쪽이 하위 계층입니다.

```
__main__.py
    └── cli.py
          ├── config.py          (설정 로딩)
          ├── ai_factory.py      (AI provider 선택)
          │     ├── gemini_client.py ─┐
          │     └── openai_client.py ─┤── ai_client.py (공용 프롬프트/Protocol)
          ├── notion.py ── http.py    (Notion REST API)
          └── organizer.py            (핵심 워크플로우)
                ├── ai_client.py      (AIClient Protocol에만 의존)
                ├── cache.py
                ├── markdown_convert.py
                └── notion.py
```

핵심 설계 포인트:

- `organizer.py`는 Gemini인지 OpenAI인지 전혀 모릅니다. `AIClient`라는 Protocol(인터페이스)에만 의존하고, 실제 구현체는 `cli.py`가 `ai_factory`를 통해 주입합니다. 덕분에 새 AI provider를 추가해도 핵심 워크플로우 코드는 바뀌지 않습니다.
- `config.py`는 Pydantic Settings와 python-dotenv만 사용하고, provider SDK 의존성은 `gemini_client.py`/`openai_client.py` 두 파일에 격리되어 있습니다. `http.py`, `cache.py`, `markdown_convert.py`, `notion.py`는 표준 라이브러리만 사용합니다.

### 한 번 실행하면 일어나는 일 (파이프라인)

`organizer.NotionPageOrganizer.organize_page()`가 아래 순서로 진행합니다.

1. **ID 정규화** — 입력이 URL이든 하이픈 붙은 UUID든 32자리 페이지 ID를 추출 (`notion.normalize_page_id`)
2. **페이지 로드** — 제목과 전체 블록 트리를 Notion API로 가져옴
3. **Markdown 변환** — 블록 트리를 Markdown 텍스트로 변환 (`markdown_convert.blocks_to_markdown`)
4. **백업** — 원본 Markdown을 `backups/제목-타임스탬프.md`로 저장
5. **AI 정리** — 캐시에 같은 원본에 대한 응답이 있으면 재사용, 없으면 AI 호출 후 캐시에 저장
6. **결과 저장** — 정리된 Markdown을 `posts/제목-organized.md`로 저장
7. **페이지 교체** — 정리된 Markdown을 다시 Notion 블록으로 변환한 뒤, 기존 블록을 모두 아카이브하고 새 블록을 추가

**안전 설계의 핵심**: 백업(4단계)은 AI 호출보다 먼저 일어나고, 페이지 교체(7단계)는 AI가 성공한 뒤에만 일어납니다. AI가 어떤 이유로든 실패하면 예외가 발생해서 7단계에 도달하지 못하므로, **원본 Notion 페이지는 절대 훼손되지 않습니다.**

---

## 2. 파일별 상세 설명

### `__init__.py` / `__main__.py` — 패키지 선언과 실행 진입점

- [`__init__.py`](../notion_auto_organizer/__init__.py): 패키지 버전 상수 `__version__ = "0.1.0"`만 정의합니다.
- [`__main__.py`](../notion_auto_organizer/__main__.py): `python -m notion_auto_organizer`로 실행될 때의 진입점입니다. 전체 코드가 4줄입니다.

```python
from .cli import main

if __name__ == "__main__":
    raise SystemExit(main())
```

`main()`이 반환하는 정수(0 = 성공)를 `SystemExit`으로 감싸 프로세스 종료 코드로 사용합니다. 셸 스크립트나 CI에서 성공/실패를 판단할 수 있게 하는 CLI 관례입니다.

### `cli.py` — 명령줄 인터페이스

사용자 입력을 받아 필요한 객체들을 조립하고 워크플로우를 실행하는 **오케스트레이터**입니다. 비즈니스 로직은 없습니다.

**`build_parser()`** — argparse 파서를 만듭니다. 옵션은 딱 두 개입니다.

| 옵션 | 설명 |
|---|---|
| `--page-id` (필수) | 정리할 Notion 페이지의 ID 또는 URL |
| `--refresh` (플래그) | 캐시된 AI 응답을 무시하고 새로 정리 |

**`main(argv=None) -> int`** — 실제 흐름은 다음과 같습니다.

```python
settings = load_settings()                        # .env → Settings
organizer = NotionPageOrganizer(
    NotionClient(settings.notion_token.get_secret_value()),
    create_ai_client(settings),                   # provider에 맞는 AI 클라이언트 주입
    cache_namespace=settings.cache_namespace,
)
if args.refresh:
    organizer.ai_cache.clear()
result = organizer.organize_page(args.page_id)
```

전체가 하나의 `try/except Exception`으로 감싸져 있어서, 설정 누락·API 오류·AI 실패 등 어떤 예외든 `parser.exit(1, f"error: {exc}\n")`로 변환됩니다. 사용자에게는 스택 트레이스 대신 `error: ...` 한 줄이 보이고, 종료 코드는 1이 됩니다.

`argv` 매개변수를 받는 이유: 테스트에서 `cli.main(["--page-id", "..."])`처럼 인자를 직접 넘길 수 있게 하기 위해서입니다. `None`이면 argparse가 `sys.argv`를 사용합니다.

**`settings.cache_namespace`** — `"gemini-gemini-2.5-flash"`처럼 provider와 모델명을 합친 캐시 파일명 접두사입니다. 모델을 바꾸면 다른 모델의 응답을 잘못 재사용하지 않습니다.

### `config.py` — 환경변수 로딩과 검증

**`Settings`** — Pydantic Settings 모델입니다. python-dotenv를 통해 `.env`를 읽고 타입, 필수값, provider별 제약을 검증합니다. 실제 시스템 환경변수가 `.env`보다 우선합니다.

| 필드 | 환경변수 | 용도 |
|---|---|---|
| `notion_token` | `NOTION_TOKEN` | Notion API 토큰 (항상 필수) |
| `ai_provider` | `AI_PROVIDER` | 필수, `gemini` 또는 `openai` |
| `ai_api_key` | `AI_API_KEY` | 선택한 provider의 API 키 (필수, 로그에서 마스킹) |
| `ai_model` | `AI_MODEL` | 선택한 모델 (필수) |
| `ai_base_url` | `AI_BASE_URL` | OpenAI-compatible endpoint에만 선택적으로 사용 |

**`load_settings(env_file=Path(".env")) -> Settings`** — Pydantic Settings가 dotenv 파일과 프로세스 환경을 결합하고 검증합니다. provider와 모델에는 기본값이 없으며 Gemini에서 `AI_BASE_URL`을 설정하면 오류가 발생합니다.

### `organizer.py` — 핵심 워크플로우

이 프로젝트의 심장입니다. "1. 프로젝트 개요"에서 설명한 7단계 파이프라인이 [`organize_page()`](../notion_auto_organizer/organizer.py#L39-L69)에 그대로 들어 있습니다.

**`OrganizeResult`** — frozen dataclass. 처리 결과(제목, 백업 경로, post 경로, 추가된 블록 수)를 담아 `cli.py`가 출력에 사용합니다.

**`NotionPageOrganizer`** — 생성자에서 `NotionClient`와 `AIClient`를 **주입받습니다**(직접 생성하지 않음). 이 의존성 주입 덕분에 테스트에서는 가짜(Fake) 객체를 넣어 실제 API 호출 없이 전체 흐름을 검증할 수 있습니다. `backups_dir`/`posts_dir`/`cache_dir`도 키워드 인자로 바꿀 수 있어서 테스트가 임시 폴더를 사용합니다.

**`organize_page(page_id)`** — 순서가 곧 안전장치입니다.

```python
page_id = normalize_page_id(page_id)      # (1) 검증 실패 시 Notion 호출 자체가 없음
...
backup_path.write_text(original_markdown) # (4) AI 호출 전에 백업부터

organized_markdown = self.ai_cache.get(original_markdown)
if organized_markdown is None:
    organized_markdown = self.ai_client.organize_markdown(original_markdown)  # (5) 여기서 실패하면
    self.ai_cache.set(original_markdown, organized_markdown)                  #     아래로 내려가지 않음
...
self.notion.archive_children(page_id)     # (7) AI 성공 후에만 페이지 교체
self.notion.append_children(page_id, new_blocks)
```

캐시 키가 **원본 Markdown 전체**라는 점도 중요합니다. 페이지 내용이 한 글자라도 바뀌면 캐시 미스가 나서 AI를 다시 호출하고, 내용이 같으면 (예: 이전 실행이 페이지 교체 직전에 실패해서 재시도하는 경우) AI 호출 없이 이어서 진행됩니다.

**`slugify(value)`** — 페이지 제목을 파일명으로 쓸 수 있게 바꿉니다. 정규식 `[^\w가-힣.-]+`로 영숫자·언더스코어·한글·점·하이픈만 남기고 나머지를 하이픈으로 치환한 뒤, 연속 하이픈을 하나로 합칩니다. 결과가 비면 `"notion-page"`를 반환해 파일명이 빈 문자열이 되는 것을 막습니다.

### `ai_client.py` — AI provider 공용 계층

provider들이 공유하는 세 가지가 들어 있습니다: 시스템 프롬프트, 인터페이스 정의, 응답 추출 로직.

**`NOTE_ORGANIZER_PROMPT`** — AI에게 주는 한국어 시스템 프롬프트입니다. "한국어 입문자용 개발 학습 노트 편집자" 역할을 부여하고, 출력 형식을 지정합니다:

- `# 제목 / ## 핵심 요약 / ## 개념 정리 / ## 예시 코드` 섹션 구조 사용
- `markdown_to_blocks`가 실제로 인식하는 문법(제목 1~3단계, 문단, 중첩 없는 목록, 체크박스, 인용, 코드펜스, 구분선)만 쓰도록 제한
- 굵게(`**`)·기울임(`*`)·취소선(`~~`)·인라인 코드(`` ` ``)·링크(`[]()`) 등 모든 인라인 서식 금지 — `markdown_to_blocks`의 `rich_text()`는 inline 서식을 파싱하지 않고 텍스트를 그대로 담기 때문에, 이런 문법을 쓰면 Notion에 리터럴 문자(`**`, `` ` `` 등)로 그대로 노출됨
- 표와 중첩 리스트 금지 — `markdown_to_blocks`가 들여쓰기나 표 문법을 추적하지 않아 구조가 깨짐
- 원본에서 언어/프레임워크를 추론하고, 이해를 돕는 짧은 예시 코드 추가. 확실하지 않은 내용은 지어내지 않기
- 전체 답변을 코드펜스로 감싸지 말 것 (감싸면 `markdown_to_blocks`가 전부를 하나의 code 블록으로 잘못 해석)

**`AIClient`** (Protocol) — `organize_markdown(markdown: str) -> str` 메서드 하나만 요구하는 인터페이스입니다. Python의 `Protocol`은 **구조적 타이핑**이라서, 상속 없이도 이 시그니처의 메서드를 가진 클래스는 전부 `AIClient`로 취급됩니다. `GeminiClient`/`OpenAIClient`는 물론 테스트의 Fake 클래스도 상속 선언 없이 그대로 사용됩니다.

**`organize_with_agent(agent, markdown, *, provider)`** — 두 provider가 공유하는 실행 로직입니다. LangChain agent에 사용자 메시지로 Markdown을 넘기고, 응답 텍스트를 추출합니다. 빈 응답이면 `RuntimeError`를 던집니다 — 조용히 빈 문자열을 반환하면 organizer가 Notion 페이지를 **빈 내용으로 교체**해버리기 때문에, 반드시 실패로 처리해야 합니다.

**`extract_agent_text(result)` / `_content_to_text(content)`** — LangChain agent의 응답 형태가 일정하지 않은 문제를 흡수하는 계층입니다. messages 리스트를 **역순으로** 훑어 (마지막 AI 응답이 최종 결과이므로) 처음 만나는 텍스트를 반환합니다. message가 객체일 수도 dict일 수도 있고, content가 문자열일 수도 `{"text": ...}` dict 청크의 리스트일 수도 있어서 모든 경우를 처리합니다.

### `ai_factory.py` — provider 선택 팩토리

19줄짜리 파일이지만 역할이 분명합니다. `settings.ai_provider` 값에 따라 알맞은 구현체를 만들어 반환합니다.

```python
def create_ai_client(settings: Settings) -> AIClient:
    api_key = settings.ai_api_key.get_secret_value()
    if settings.ai_provider == "gemini":
        return GeminiClient(api_key, settings.ai_model)
    if settings.ai_provider == "openai":
        return OpenAIClient(api_key, settings.ai_model, base_url=settings.ai_base_url)
    raise ValueError(f"Unsupported AI_PROVIDER: {settings.ai_provider}")
```

"어떤 provider를 쓸지"에 대한 지식을 이 파일 하나에 모아둔 팩토리 패턴입니다. 새 provider를 추가하려면 ① 새 클라이언트 클래스 작성 → ② 여기에 분기 추가 → ③ `config.py`에 필요한 환경변수 검증 추가, 세 곳만 고치면 됩니다.

### `gemini_client.py` / `openai_client.py` — provider 구현체

두 파일은 거의 같은 구조입니다. 차이는 **어떤 LangChain 챗 모델을 쓰느냐**뿐입니다.

| | `GeminiClient` | `OpenAIClient` |
|---|---|---|
| 챗 모델 | `ChatGoogleGenerativeAI` | `ChatOpenAI` |
| 인증 | `google_api_key` | `api_key` + 선택적 `base_url` |
| 용도 | Google Gemini 직접 호출 | OpenAI 공식 또는 호환 endpoint 호출 |

공통 구조 (생성자):

```python
chat_model = ChatOpenAI(..., temperature=0.3)      # 또는 ChatGoogleGenerativeAI
self.agent = create_agent(
    model=chat_model,
    tools=[],                                       # 도구 없이 텍스트 재작성만
    system_prompt=NOTE_ORGANIZER_PROMPT,
    name="note_organizer_agent",
)
```

- `temperature=0.3`: 창의성보다 일관된 정리 결과를 원하므로 낮게 설정.
- `tools=[]`: 검색·계산 같은 도구가 필요 없는 순수 텍스트 변환 작업이라 비워둡니다.

`organize_markdown()`은 둘 다 한 줄로, `ai_client.organize_with_agent()`에 위임합니다. `provider="Gemini"` 같은 이름은 오류 메시지에 어느 provider가 실패했는지 표시하는 용도입니다.

### `notion.py` — Notion API 클라이언트

Notion REST API 호출을 담당합니다. 공식 SDK 대신 `http.request_json` 헬퍼로 직접 호출합니다.

상수:

- `NOTION_VERSION = "2022-06-28"` — 모든 요청의 `Notion-Version` 헤더에 들어가는 API 버전 고정값.
- `NOTION_PAGE_ID_PATTERN` — 32자리 16진수(`abc123...`) **또는** 하이픈 UUID(`8-4-4-4-12`) 형식을 찾는 정규식.

**`NotionClient(token)`** — 생성자에서 `Authorization: Bearer <token>`과 `Notion-Version` 헤더를 만들어두고 모든 메서드가 재사용합니다.

| 메서드 | HTTP | 하는 일 |
|---|---|---|
| `retrieve_page(page_id)` | GET `/pages/{id}` | 페이지 메타데이터 조회 |
| `get_page_title(page_id)` | (retrieve_page 사용) | properties에서 `type == "title"`인 속성을 찾아 제목 추출. 없으면 page_id를 그대로 반환 (파일명 생성이 실패하지 않도록 하는 fallback) |
| `list_block_children(block_id)` | GET `/blocks/{id}/children` | 자식 블록 목록. **커서 페이지네이션**: `page_size=100`으로 요청하고 `has_more`가 참인 동안 `next_cursor`로 반복 요청해 전부 수집 |
| `list_block_children_tree(block_id)` | (재귀) | `has_children`인 블록을 재귀적으로 파고들어 `child["children"]`에 붙여 전체 트리 구성 |
| `archive_block(block_id)` | PATCH `/blocks/{id}` | `{"archived": true}` — Notion은 진짜 삭제 대신 아카이브(휴지통 이동)를 사용하므로 실수해도 복구 가능 |
| `append_children(block_id, children)` | PATCH `/blocks/{id}/children` | **100개씩 잘라서** 여러 번 요청 — Notion API가 요청당 블록 100개로 제한하기 때문 |
| `archive_children(block_id)` | (조합) | 최상위 자식을 모두 조회해 하나씩 아카이브 — "페이지 비우기"에 해당 |

**`normalize_page_id(page_id)`** — 클래스 밖 모듈 함수입니다. 사용자가 무엇을 넘기든 정규식으로 페이지 ID만 추출합니다:

- `3969cc0317cf8024b936dc7874b3ccf3` → 그대로
- `3969cc03-17cf-8024-b936-dc7874b3ccf3` → 그대로 (하이픈 형식도 API가 허용)
- `https://www.notion.so/My-Page-3969cc03...ccf3?v=123` → URL에서 ID만 추출
- 빈 문자열이나 ID가 없는 문자열 → `ValueError`

`organize_page()`가 **모든 Notion 호출보다 먼저** 이 함수를 호출하므로, 잘못된 입력은 API 요청이 나가기 전에 걸러집니다.

### `markdown_convert.py` — 블록 ↔ Markdown 양방향 변환

Notion 블록(JSON)과 Markdown 텍스트를 양방향으로 변환합니다. 이 프로젝트에서 가장 긴 파일이지만, 절반은 "블록 타입별 분기"라 구조는 단순합니다.

#### 블록 → Markdown (`blocks_to_markdown`)

블록 리스트를 순회하며 타입별로 Markdown 줄을 만듭니다:

| Notion 블록 | Markdown 출력 |
|---|---|
| `paragraph` | 일반 텍스트 |
| `heading_1~3` | `#`, `##`, `###` |
| `bulleted_list_item` | `- 항목` |
| `numbered_list_item` | `1. 항목` (번호는 항상 1 — Markdown 렌더러가 자동 번호 매김) |
| `to_do` | `- [ ]` / `- [x]` |
| `quote` | `> 인용` |
| `code` | ` ```언어 ` 코드펜스 |
| `divider` | `---` |
| `image`/`file`/`pdf`/`video` | `![캡션](url)` 또는 `[캡션](url)` |
| `toggle`/`callout` | `> [Toggle] 라벨` 형태의 인용 (Markdown에 대응 문법이 없어 근사 표현) |
| `bookmark` | `[캡션](url)` |
| `unsupported` | `> Unsupported Notion block was omitted.` 안내문 |

`has_children`이고 타입이 `SUPPORTED_CHILD_TYPES`(paragraph, 리스트류, to_do, toggle, quote, callout)에 속하면 자식 블록을 `depth + 1`로 **재귀 호출**해 2칸 들여쓰기로 붙입니다.

보조 함수:

- `rich_text_to_plain(parts)` — 서식 없이 `plain_text`만 이어붙임 (코드 블록 내용처럼 서식이 의미 없는 곳에 사용)
- `rich_text_to_markdown(parts)` — Notion의 annotations(code/bold/italic/strikethrough)와 링크를 `` `x` ``, `**x**`, `*x*`, `~~x~~`, `[x](url)`로 변환

#### Markdown → 블록 (`markdown_to_blocks`)

줄 단위로 파싱하는 상태 기계입니다. 각 줄을 위에서부터 패턴 매칭합니다: 코드펜스 → 헤딩(`#{1,3}`) → 구분선(`---`) → to_do(`- [ ]`) → 불릿(`-`, `*`) → 번호 리스트 → 인용(`>`) → 그 외는 문단.

문단만 특별하게 처리합니다. 연속된 일반 텍스트 줄을 `paragraph_lines`에 모아두었다가, 빈 줄이나 다른 블록 패턴을 만나는 순간 `flush_paragraph()`로 하나의 paragraph 블록으로 합칩니다. Markdown에서 "붙어 있는 줄들은 한 문단"이라는 규칙을 구현한 것입니다.

코드펜스는 시작 ` ``` `을 만나면 닫는 ` ``` `이 나올 때까지 안의 줄을 그대로(파싱하지 않고) 모아 하나의 code 블록으로 만듭니다.

#### 블록 생성 헬퍼와 Notion API 제한 대응

- `text_block` / `todo_block` / `code_block` — Notion API가 요구하는 `{"object": "block", "type": ..., <type>: {...}}` JSON 구조를 만드는 헬퍼.
- **`split_text(text, size=1900)`** — Notion API는 rich_text 하나의 content를 **2000자로 제한**합니다. 1900자 단위로 잘라 여유를 두고, `rich_text()`와 `text_to_paragraph_blocks()`가 이를 사용해 긴 텍스트도 API 오류 없이 올라가게 합니다.
- **`normalize_code_language(language)`** — Notion code 블록은 정해진 언어 이름만 허용합니다. `js → javascript`, `py → python`, `sh → bash` 같은 흔한 별칭을 정식 이름으로 바꾸고, 빈 값은 `"plain text"`로 대체합니다. 잘못된 언어 이름은 API 400 오류를 일으키기 때문에 필요한 방어입니다.

### `cache.py` — AI 응답 파일 캐시

같은 원본에 대해 AI를 반복 호출하지 않기 위한 파일 기반 캐시입니다. AI 호출은 느리고 비용이 들기 때문입니다.

**`AIResponseCache(directory, namespace="default")`**

- `get(source_markdown)` — 캐시 파일이 있으면 내용을 반환, 없거나 읽기 오류면 `None` (= 캐시 미스로 처리).
- `set(source_markdown, organized_markdown)` — 캐시 파일 저장.
- `clear()` — 해당 네임스페이스의 캐시 파일(`{namespace}-*.md`)을 모두 삭제. `--refresh` 옵션이 호출합니다.

**캐시 키 생성** (`_path_for`):

```python
cache_key = hashlib.sha256(f"{self.namespace}\0{source_markdown}".encode()).hexdigest()
return self.directory / f"{self._safe_namespace()}-{cache_key}.md"
```

네임스페이스와 원본 전체를 `\0`(널 문자)로 이어붙여 SHA-256 해시를 만듭니다. `\0` 구분자는 서로 다른 (네임스페이스, 원본) 조합이 우연히 같은 문자열이 되는 것을 막습니다. 파일명에는 사람이 읽을 수 있는 네임스페이스 접두사도 붙어서, `cache/` 폴더만 봐도 어느 모델의 캐시인지 알 수 있습니다.

**설계 의도 — 오류를 조용히 무시하는 이유**: `get`/`set`/`clear` 모두 `OSError`를 잡아서 그냥 넘어갑니다. 코드 주석에도 있듯이 *"캐시는 최적화일 뿐, 페이지 정리 작업을 깨뜨려서는 안 된다"*는 원칙입니다. 디스크가 가득 차서 캐시 저장에 실패해도 정리 자체는 정상 완료됩니다.

### `http.py` — 경량 HTTP 헬퍼

requests 같은 외부 라이브러리 없이 표준 라이브러리 `urllib`만으로 JSON API를 호출하는 헬퍼입니다.

**`request_json(method, url, *, headers, body, query) -> dict`**

- `query`가 있으면 URL에 쿼리스트링으로 인코딩하되, **값이 `None`인 키는 제거** — `list_block_children`이 첫 요청에서 `start_cursor=None`을 넘겨도 쿼리에 포함되지 않게 하는 처리입니다.
- `body`가 있으면 JSON으로 직렬화하고 `Content-Type: application/json`을 자동 설정 (이미 지정돼 있으면 존중 — `setdefault`).
- 타임아웃 60초.
- 빈 응답 본문은 `{}`로 반환 (호출부의 `.get(...)` 접근이 안전하도록).

**`HttpError(RuntimeError)`** — `urllib`의 `HTTPError`(4xx/5xx 응답)와 `URLError`(네트워크 실패)를 잡아 이 커스텀 예외로 다시 던집니다. 특히 `HTTPError`의 경우 **응답 본문을 읽어 메시지에 포함**시킵니다. Notion API는 오류 원인을 응답 본문 JSON에 담아주므로, 이렇게 해야 `error: PATCH ... failed: HTTP 400 {"message": "..."}` 같은 진단 가능한 메시지가 사용자에게 전달됩니다.

---

## 3. 테스트 요약

`tests/` 폴더는 소스 파일과 거의 1:1로 대응합니다. 모든 외부 호출(Notion API, AI)은 monkeypatch나 Fake 객체로 대체되어 네트워크 없이 실행됩니다.

| 테스트 파일 | 검증 내용 |
|---|---|
| `test_organizer.py` | **가장 중요한 안전성 테스트.** AI가 실패하면 페이지가 교체되지 않고(archive 호출 없음) 백업 파일은 남는지, 성공 시 백업/post 저장과 페이지 교체가 모두 일어나는지, URL이 모든 Notion 호출 전에 정규화되는지, 잘못된 page_id가 Notion 호출 없이 거부되는지, `slugify` 케이스들을 검증합니다. |
| `test_cli.py` | `main` 성공 시 결과 출력, `--refresh`가 캐시 clear를 호출하는지, 설정 실패 시 종료 코드 1과 `error:` 메시지, `--page-id` 누락 시 실패, provider별 cache namespace를 검증합니다. |
| `test_config.py` | 공통 dotenv 설정, 환경변수 우선순위, 필수값과 provider 검증, secret 마스킹 및 기존 변수명 미지원을 검증합니다. |
| `test_ai_factory.py` | 공통 API key, 모델 및 선택적 base URL이 provider 구현체로 전달되는지 검증합니다. |
| `test_notion.py` | `append_children`이 205개 블록을 [100, 100, 5]로 나누는지, 커서 페이지네이션이 `next_cursor`를 따라가는지, 제목 추출과 page_id fallback, `normalize_page_id`의 ID/UUID/URL 처리와 잘못된 값 거부를 검증합니다. |
| `test_markdown_convert.py` | 블록→Markdown 기본 변환, Markdown→블록의 타입 판별과 코드 언어 정규화(js→javascript), 긴 문단의 분할을 검증합니다. |
| `test_cache.py` | 캐시 hit/miss 동작과, 같은 원본으로 두 번 실행하면 AI가 한 번만 호출되는지(호출 횟수 카운팅)를 검증합니다. |
| `test_http.py` | 쿼리 인코딩과 `None` 값 제거, JSON body와 Content-Type 자동 설정, `HTTPError`/`URLError`가 응답 본문을 포함한 `HttpError`로 래핑되는지 검증합니다. |
| `test_gemini_client.py` | `ChatGoogleGenerativeAI`와 `create_agent`에 전달되는 인자(모델명, API 키, temperature 0.3, tools=[])를 캡처해 검증합니다. |
| `test_openai_client.py` | `ChatOpenAI`의 공통 API key, 모델, 선택적 base URL과 리스트형 content(`{"text": ...}`) 추출을 검증합니다. |

실행: `python -m pytest`

---

## 4. 설정 및 기타 파일

### `pyproject.toml`

- **의존성**: LangChain provider 패키지와 환경 설정용 `pydantic`, `pydantic-settings`, `python-dotenv`를 사용합니다. Notion API는 표준 라이브러리로 직접 호출하며 개발용(`[dev]`)으로 `pytest`, `ruff`를 추가합니다.
- **`[project.scripts]`**: `notion-auto-organizer = "notion_auto_organizer.cli:main"` — 설치하면 콘솔 명령이 생기는 부분입니다.
- **도구 설정**: pytest는 `tests/`만 수집, ruff는 줄 길이 100 / Python 3.10 기준 / E·F·I·W·UP·B 규칙 활성화.
- 요구 Python 버전: **3.10 이상**.

### `.env.example`

`.env`를 만들 때 복사하는 템플릿입니다. 실제 `.env`는 `.gitignore`에 포함되어 커밋되지 않습니다.
필수 공통 설정 네 개와 OpenAI-compatible endpoint에만 사용하는 선택적 `AI_BASE_URL`을 안내합니다.

### `.github/workflows/ci.yml`

GitHub Actions CI 설정입니다. `master` 브랜치 push와 모든 PR에서 실행되며, Python **3.10과 3.12** 두 버전 매트릭스로:

1. `pip install -e ".[dev]"` — editable 설치
2. `ruff check .` + `ruff format --check .` — 린트와 포맷 검사
3. `python -m pytest` — 테스트

를 순서대로 수행합니다. 로컬에서 커밋 전에 같은 명령을 돌려보면 CI 실패를 미리 잡을 수 있습니다.

### 런타임 생성 폴더 (git 제외)

| 폴더 | 내용 |
|---|---|
| `backups/` | 페이지 교체 전 원본 Markdown (`제목-타임스탬프.md`) |
| `posts/` | AI가 정리한 결과 Markdown (`제목-organized.md`) |
| `cache/` | AI 응답 캐시 (`네임스페이스-해시.md`) |
