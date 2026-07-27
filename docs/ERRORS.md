# 에러 레퍼런스

이 문서는 `notion-auto-organizer`가 발생시키는 에러 클래스, 발생 조건, 각 실패 시나리오에서의 Notion 페이지 상태를 설명한다.

## 에러 클래스 계층

```
Exception
├── OrganizationError          # 모든 정리 작업 실패의 기반 클래스
│   ├── NotionError            # Notion API 호출 실패
│   └── AIClientError          # AI 제공자 호출 실패
└── RuntimeError
    └── HttpError              # HTTP 전송 계층 실패 (NotionError의 원인으로 연결됨)
```

`HttpError`는 `urllib` 수준의 실패를 감싸며, `NotionClient`가 `NotionError`를 raise할 때 `__cause__`로 연결된다. 직접 catch할 필요는 없다.

## 단계별 에러 발생 조건

| 단계 | 발생 에러 | 조건 |
|------|-----------|------|
| page_id 정규화 | `ValueError` | page_id에서 32자리 hex를 추출할 수 없음 |
| Notion 페이지 읽기 | `NotionError` | API 호출 실패 (인증, 네트워크, 권한 오류) |
| 빈 페이지 검사 | `OrganizationError` | 페이지에 블록이 없어 Markdown이 비어있음 |
| 백업 파일 저장 | `OrganizationError` | 파일 시스템 쓰기 실패 |
| AI 정리 | `AIClientError` | AI 제공자 응답 실패 또는 스키마 불일치 |
| 결과 파일 저장 | `OrganizationError` | 파일 시스템 쓰기 실패 |
| 새 블록 추가 | `NotionError` | `append_children` API 호출 실패 |
| 기존 블록 보관 | `NotionError` | `archive_children` API 호출 실패 |

CLI는 모든 `Exception`을 잡아 exit code 1로 종료하고 에러 메시지를 출력한다. `--debug` 플래그를 추가하면 전체 traceback이 출력된다.

## 실패 시나리오별 Notion 페이지 상태

Notion 페이지 교체는 **새 블록 추가(append) → 기존 블록 보관(archive)** 순서로 실행된다. 이 순서는 append 실패 시 원본 콘텐츠를 보존하기 위해 의도적으로 선택된 것이다.

| 실패 지점 | Notion 페이지 상태 | 복구 방법 |
|-----------|-------------------|-----------|
| page_id 정규화 실패 | 변경 없음 | 올바른 page_id 사용 |
| 페이지 읽기 실패 | 변경 없음 | 인증 토큰·권한 확인 |
| 빈 페이지 | 변경 없음 | 페이지에 내용 추가 후 재실행 |
| 백업 저장 실패 | 변경 없음 | 파일 시스템 권한 확인 |
| AI 호출 실패 | 변경 없음 | API 키·모델 설정 확인, `--refresh`로 재시도 |
| 결과 파일 저장 실패 | 변경 없음 | 파일 시스템 권한 확인 |
| **새 블록 추가 실패** | **원본 보존** | Notion API 상태 확인 후 재실행 |
| **기존 블록 보관 실패** | **원본+새 블록 공존** | Notion에서 원본 블록 수동 삭제 |

## 안전 보장

- AI 호출이나 파일 저장이 실패하면 Notion 페이지는 **절대 변경되지 않는다.**
- 새 블록 추가가 실패해도 원본 블록이 보존된다 (archive는 append 성공 후에만 실행됨).
- 기존 블록 보관(archive) 실패는 원본+새 블록 공존 상태를 만들지만, 원본 데이터는 손실되지 않는다.
- 모든 경우에 로컬 `backups/` 파일이 먼저 저장되므로 원본 Markdown은 항상 복구 가능하다.
