# 개발

## 설치

```powershell
python -m pip install -e ".[dev]"
```

Python 3.10 이상이 필요합니다. LangChain 제공자 의존성은 `pyproject.toml`에 정의되어 있습니다.

## 테스트

전체 테스트를 실행합니다.

```powershell
python -m pytest
```

테스트 모음은 제공자 요청을 모의 처리하고 제공자 선택, 에이전트 출력 추출, Markdown 변환, Notion 단위 분할, AI 정리 실패 시의 안전성을 검증합니다.

단위 테스트에는 실제 API 호출이 포함되지 않으므로 전체 작업 흐름을 실행하기 전에 항상 짧은 프롬프트로 연결을 확인하세요.

## 실행

```powershell
notion-auto-organizer "<PAGE_ID>"
```

페이지 ID 자체나 전체 Notion 페이지 URL을 입력할 수 있습니다.

실행 중에는 원본 내용을 백업하고 AI 정리를 수행하며, 정리 결과가 성공한 후에만 Notion 페이지를 교체합니다. 원본 Markdown은 `backups/`에, AI가 생성한 결과는 `posts/`에 저장합니다.

## 안전 규칙

- `.env` 파일, 토큰, 키를 커밋하지 마세요.
- 첫 실행에는 테스트용 Notion 페이지를 사용하세요.
- AI 호출이 실패하면 기존 Notion 페이지를 교체하지 마세요.
- 백업과 출력 파일을 소스 제어에서 제외하세요.
- 제공자 구현을 변경할 때는 제공자 클라이언트와 관련 config/factory 테스트를 함께 갱신하세요.
