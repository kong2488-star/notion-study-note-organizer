# 환경 설정 통합

- **상태:** 완료

## 동기

제공자별 환경변수와 사용하지 않는 환경변수 때문에 설정을 이해하기 어렵고 제공자 분기가 중복됩니다. 또한 프로젝트가 자체 dotenv 파서를 유지하며 설정이 불완전할 때 기본 제공자를 자동으로 선택합니다.

## 목표

Pydantic Settings와 python-dotenv를 통해 하나의 공통 환경변수 계약을 읽고 검증하며, AI 제공자를 명시적으로 요구하고, 선택한 제공자에서 사용하는 값만 유지합니다.

## 범위

- 자체 dotenv 파서와 dataclass 설정을 Pydantic Settings로 교체합니다.
- `NOTION_TOKEN`, `AI_PROVIDER`, `AI_API_KEY`, `AI_MODEL`, 선택적인 `AI_BASE_URL`을 사용합니다.
- 제공자별 변수, embedding 변수, 기본 제공자를 제거합니다.
- AI factory, CLI 캐시 namespace, 로컬 dotenv 파일, 테스트, 의존성, 현재 문서를 갱신합니다.
- Gemini와 OpenAI 호환 제공자를 모두 유지합니다.
- AI 응답 구조 변경, Notion SDK 마이그레이션, async 처리, 실제 API 호출은 제외합니다.

## 단계

1. Pydantic Settings와 dotenv 의존성을 추가하고 통합된 검증 설정 모델을 구현합니다.
2. 제공자 생성과 캐시 이름이 공통 설정 필드를 사용하도록 갱신합니다.
3. 값을 노출하지 않고 로컬 `.env`를 이전하고 `.env.example`과 문서를 갱신합니다.
4. dotenv 우선순위, 검증, 제공자 생성, CLI 동작의 단위 테스트를 갱신합니다.
5. 필수 테스트와 정적 검증을 실행하고 작업 로그를 마무리한 뒤 계획을 완료 상태로 표시합니다.

## 검증

- `python -m pytest`를 실행합니다.
- `python -m ruff check .`을 실행합니다.
- `python -m ruff format --check .`을 실행합니다.
- `git diff --check`를 실행합니다.
- 제거 대상 변수명이 활성 코드, 테스트, 설정 예제, 현재 문서에 없는지 확인합니다.
- diff나 작업 로그에 비밀값이 없는지 확인합니다.
