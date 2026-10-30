# 추가 MCP를 고를 때

이 문서는 후보 검토이며 호스트의 허가서나 연결 성공 기록이 아닙니다.
기본 키트에는 추가 AI, 원격 계산 서비스, 외부 전송 기능이 없습니다.
외부 도구를 연결할 때는 라이선스뿐 아니라 실행 위치, 전송 내용, 인증, telemetry,
관리 설정 변경 여부를 따로 확인합니다. 공개 코드를 내려받는 것과 작업 데이터를
외부로 보내는 것은 서로 다릅니다.

## 바로 유용한 후보: Playwright MCP

- 쓰임새: 개발한 웹앱의 버튼, 입력, 페이지 이동, 오류 흐름을 실제 브라우저로 확인.
- 원본: https://github.com/microsoft/playwright-mcp
- 라이선스: Apache-2.0. 이 키트에는 서버 코드나 브라우저를 재배포하지 않습니다.
- 예시 버전: `@playwright/mcp@0.0.83`. 배포된 의존성 기준 Node 20 이상과 호환 브라우저/OS 라이브러리가 필요합니다.
- 설정 예시: `configs/mcp-playwright.example.json`. 기존 서버와 병합하고 호스트 안내에 따라 저장/재실행합니다.
- `--headless`는 별도 화면 창 없이 실행, `--isolated`는 별도 임시 프로필 사용입니다.
  개인 PC의 로그인 브라우저 세션이 자동 공유되는 것이 아닙니다.
- 브라우저/런타임 설치와 실제 호스트 연결은 미검증입니다. 제공된 브라우저 도구가 충분하면 먼저 그것을 씁니다.

호스트가 허용하는 개발 서비스 주소에서 합성 입력 한 건으로 확인합니다.
문제·코드·비공개 데이터를 외부 웹사이트의 폼이나 URL에 넣지 않습니다.
원격 브라우저 서비스·계정 로그인·제한 우회 옵션을 기본 구성에 추가하지 않습니다.
다른 브라우저 MCP를 동시에 여러 개 설치할 필요는 없습니다.

## 데이터 문제에서 검토할 후보: DuckDB 로컬 MCP

- 쓰임새: 큰 CSV/Parquet, 로그, join/group/window 집계를 SQL 안에서 수행.
- 원본: https://github.com/motherduckdb/mcp-server-motherduck
- 서버 라이선스: MIT. 검토 배포 버전 `mcp-server-motherduck==1.1.0`, Python 3.10 이상/uvx 필요.
- 로컬 DuckDB는 개인 토큰 없이 쓸 수 있습니다. MotherDuck `md:`나 S3 등 원격 접속은 다른 기능입니다.
- 이 키트에서는 활성 설정을 제공하지 않습니다. 실제 설치·호스트 호출·접근 제한은 미검증입니다.

`:memory:`나 read-only는 외부 통신 금지를 보장하지 않습니다. SQL 엔진은 HTTP/S3와
확장 기능으로 접근할 수도 있습니다. 실제 허용 데이터 폴더, 외부 접근/확장 기능 비활성화,
설정 잠금을 검증한 경우에만 별도로 검토합니다. Python/SQL 스크립트로 같은 집계를
수행할 수 있다면 별도 MCP 없이 그 방법을 먼저 씁니다.

공식 제한 안내:
https://duckdb.org/docs/1.5/operations_manual/securing_duckdb/overview
https://duckdb.org/docs/1.5/operations_manual/securing_duckdb/securing_extensions

## 기본 구성에서 제외한 후보

- GitHub 쓰기 MCP/원격 업로드/원격 배포 도구: 공개 Clone에는 필요하지 않습니다.
- 개인 키가 필요한 외부 AI·검색·원격 브라우저 서비스: 별도 허용 없이는 사용하지 않습니다.
- 오래된 `semgrep-mcp`: 보관된 별도 구현입니다. 현재 방식과 혼동하지 않습니다.
- Semgrep Registry 규칙 전체: 엔진의 LGPL과 규칙 라이선스는 다릅니다. 모든 규칙을 OSS로 간주하지 않습니다.
  현재 MCP의 추적/메트릭과 개별 규칙 라이선스까지 검토하지 않은 구성은 제공하지 않습니다.
- Chrome DevTools MCP 추가 설치: Playwright와 역할이 겹치며 통계/외부 URL 조회 설정을 별도로 검토해야 합니다.

공식 근거:
https://github.com/semgrep/mcp
https://github.com/semgrep/semgrep-rules/blob/develop/LICENSE
https://github.com/ChromeDevTools/chrome-devtools-mcp

## 기본 선택 순서

제공된 도구 확인 → 필요한 기능 하나 → 라이선스/실행/통신 범위 확인 →
작은 합성 입력으로 실제 호출 → 이번 작업에 필요한 경우에만 유지합니다.
도구가 많다는 이유로 정확성이나 평가 결과가 보장되지는 않습니다.
