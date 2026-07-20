# 환경 설정 통합 작업 로그

- **계획 번호:** 002
- **계획 경로:** `plan/002-unify-environment-settings.md`
- **상태:** 완료
- **시작일:** 2026-07-15
- **완료일:** 2026-07-15

## 작업 요약

공통 Pydantic Settings 계약, 제공자 생성, dotenv 마이그레이션, 테스트, 의존성, 문서를 구현하고 검증했습니다. 무시되는 로컬 `.env`에는 현재 사용 중인 공통 키만 있으며 값을 출력하지 않고 이전했습니다.

## 주요 결정과 근거

- 하나의 공통 환경변수 계약 뒤에서 Gemini와 OpenAI 지원을 유지합니다.
- 불완전한 설정이 시작 시점에 실패하도록 제공자와 모델을 명시적으로 요구합니다.
- `AI_BASE_URL`은 OpenAI 호환 endpoint에 선택적으로 사용하고 Gemini에서는 잘못된 설정으로 처리합니다.
- 프로세스 환경변수가 `.env`보다 우선하도록 Pydantic Settings의 dotenv 통합을 사용합니다.
- `.env` 마이그레이션에서는 선택한 제공자의 로컬 값만 유지하고 사용하지 않는 제공자나 embedding 키는 남기지 않습니다.

## 변경 파일

- `plan/002-unify-environment-settings.md`: 승인된 구현 범위와 검증 조건을 기록했습니다.
- `logs/002-unify-environment-settings.md`: 점진적 작업 기록을 생성했습니다.
- `notion_auto_organizer/config.py`: 수동 dotenv 파싱과 기본 설정을 공통 검증 모델로 교체했습니다.
- `notion_auto_organizer/ai_factory.py`, `notion_auto_organizer/openai_client.py`, `notion_auto_organizer/cli.py`: 제공자 생성과 캐시 이름이 공통 설정과 선택적 OpenAI base URL을 사용하도록 변경했습니다.
- `pyproject.toml`: Pydantic Settings와 dotenv 의존성을 선언했습니다.
- `.env.example`, `README.md`, `AGENTS.md`, `docs/`: 공통 설정 계약과 현재 의존성 경계만 설명하도록 문서를 갱신했습니다.
- `tests/`: 새 계약에 맞춰 설정, CLI, 제공자, factory 테스트를 갱신했습니다.
- `.env`(무시됨): 값을 노출하지 않고 선택된 제공자의 값을 공통 키 이름으로 이전했습니다.

## 의미 있는 명령과 결과

- 로컬 `.env` 키 마이그레이션을 성공적으로 완료했습니다. 출력은 키 이름으로 제한됐으며 값은 포함하지 않았습니다.
- `python -m pytest -p no:cacheprovider`(종료 코드 1): 새로 선언한 `pydantic-settings` 의존성이 현재 환경에 설치되지 않아 수집 단계에서 중단됐습니다.
- 첫 번째 `python -m pip install -e ".[dev]"`(종료 코드 1): 제한된 환경에서 패키지 인덱스에 접근하지 못했습니다.
- 승인된 네트워크 접근으로 실행한 `python -m pip install -e ".[dev]"`(종료 코드 0): `pydantic-settings`를 설치하고 editable 프로젝트 설치를 갱신했습니다.
- 두 번째 `python -m pytest -p no:cacheprovider`(종료 코드 1): 테스트 46개가 통과했고 격리된 생성 테스트 5개가 명시적 테스트 값과 함께 실제 `.env`를 읽었습니다.
- 전체 검증 실행: 테스트 51개, Ruff 린트, Ruff 포맷 검사, 제거 대상 이름 검색, diff 검사가 통과했습니다. 추가 로컬 설정 smoke 검사에서 이전된 `.env`의 UTF-8 BOM을 발견했습니다.
- 최종 `python -m pytest -p no:cacheprovider`(종료 코드 0): 서드파티 deprecation 경고 하나와 함께 테스트 51개가 모두 통과했습니다.
- 최종 `python -m ruff check .` 및 `python -m ruff format --check .`(종료 코드 0): 린트가 통과했고 Python 파일 23개가 모두 포맷된 상태였습니다.
- 최종 `git diff --check`(종료 코드 0): 안내용 Git 줄바꿈 경고와 함께 통과했습니다.
- 제거 대상 이름 검색, 로컬 dotenv 로딩, dotenv 키 집합 검증, 추적 대상 diff 비밀값 검사가 모두 통과했으며 비밀값 일치 건수는 0개였습니다.

## 실패, 원인, 해결 방법

- 첫 pytest 수집은 `ModuleNotFoundError: pydantic_settings`로 실패했습니다. 갱신된 개발 의존성을 설치해 수집 문제를 해결했습니다.
- 첫 의존성 설치는 제한된 환경에서 패키지 인덱스에 접근하지 못했습니다. 승인된 네트워크 접근으로 다시 실행해 성공했습니다.
- `Settings(...)` 테스트 fixture가 설정된 `.env`를 상속해 로컬 OpenAI base URL이 Gemini fixture에 포함됐습니다. 테스트 전용 생성에 `_env_file=None`을 전달해 명시적 값을 격리하면서 실제 dotenv 동작은 보존했습니다.
- PowerShell의 첫 UTF-8 쓰기가 첫 dotenv 키 앞에 BOM을 추가해 Pydantic이 `NOTION_TOKEN` 누락을 보고했습니다. 무시되는 `.env`를 BOM 없는 UTF-8로 다시 저장해 로컬 로딩 실패를 해결했습니다.

## 검증 결과

- `python -m pytest -p no:cacheprovider`: 통과, 테스트 51개.
- `python -m ruff check .`: 통과.
- `python -m ruff format --check .`: 통과, 파일 23개가 이미 포맷됨.
- `git diff --check`: 통과.
- 제거 대상 설정 이름 검색: 통과.
- 로컬 `.env` 공통 키와 Pydantic 로딩 검사: 통과.
- 추적 대상 diff 비밀값 검사: 통과, 일치 0건.

## 해결되지 않은 문제와 후속 작업

없음
