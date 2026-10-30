# HynixHack_won — Open Workbench Kit

웹·API·버그 수정·데이터·문서·기초 회로/공정 계산을 위한 **MIT 공개 준비 도구**입니다.
특정 문제의 답안이나 공식 운영진의 권장 도구가 아닙니다. 실제 과제 README와 제공 환경의 규정을 우선합니다.

**처음이면 [START_HERE_KO.md](START_HERE_KO.md)부터 읽으세요.**

| 파일 | 내용 |
|---|---|
| [toolkit-source.zip](toolkit-source.zip) | 전체 소스·18개 Skills·MCP·테스트·합성 예제. 압축 안의 `_toolkit/`이 실제 키트 루트 |
| [CHECKSUMS.sha256](CHECKSUMS.sha256) | 소스 압축파일 SHA-256 |
| [WEB_UI_KO.md](WEB_UI_KO.md) | UI·아이콘·차트 OSS 후보와 라이선스/선택 기준 |
| [EXTRA_MCP_KO.md](EXTRA_MCP_KO.md) | Playwright 선택 예시, 로컬 SQL 후보와 사용 조건 |
| [ELECTRONICS_CALCULATORS_KO.md](ELECTRONICS_CALCULATORS_KO.md) | 기초 계산 6개, 단위·가정·검산값·공식 출처 |
| [LICENSE](LICENSE) | 키트의 MIT 라이선스. 외부 라이브러리는 각 라이선스 적용 |

## 제공된 AI에게 줄 첫 요청

```text
https://github.com/TRX1200/HynixHack_won
이 공개 저장소를 과제와 구분되는 새 폴더에 clone하고 START_HERE_KO.md를 읽어줘.
실행기와 압축 해제 도구를 확인하고 toolkit-source.zip의 체크섬을 확인해줘.
기존 파일을 덮어쓰지 말고 새 _toolkit 폴더로 안전하게 풀어줘.
실제 과제 루트에서 wb-start와 wb-verify만 먼저 적용하고 인식 여부를 확인해줘.
Python이 없으면 Markdown 지침과 기존 프로젝트 언어로 시작해줘.
MCP는 필요한 것만 검토하고 설정 JSON을 만들어줘. 설정 탭 저장은 내가 할게.
개인 키/외부 AI를 연결하거나 문제·파일·결과를 외부로 보내지 마.
```

## 포함된 기능

- **Skills 18개:** 시작·요구 확인·웹/API 구현·버그 조사·검증·데이터·문서·최적화·보고서·물리/통계 등.
- **로컬 문서 검색 MCP:** 검색/본문 조회/색인 정보. 키트 안의 Python 서버와 명시한 색인만 사용.
- **기초 계산 6개:** Ohm/전력, RC, 평행판 정전용량, 박막/면저항, Arrhenius 온도비, 1D 확산 RMS.
- **검사 도구:** CSV/조인/집계, 문서 추출, 작은 배정, 이미지 차이, 보고서 구조 확인.
- **선택 자료:** Playwright 설정 예시, UI 및 라이브러리 카탈로그. 외부 패키지는 포함하거나 자동 설치하지 않음.

## 실제 검증과 범위

v1.2.0, 2026-10-31 Windows/Python 3.12.14/Node v24.13.0에서
130개 테스트 중 **127개 통과, 3개 미실행, 실패 0개**. 로컬 MCP smoke 6개 통과.
자세한 실행·제외 항목은 압축 안의 TEST_RESULTS.md에 있습니다.

실제 제공 Codex의 Skill 탐지, MCP 연결, Playwright 브라우저, 설치 정책은 별도 확인해야 합니다.
개인 PC의 VS Code/Python 설치 여부와 원격 브라우저 IDE의 실행 환경은 다릅니다.
회로/공정 계산은 단위·가정이 명시된 교육용 모델이며 SPICE/TCAD/PDK가 아닙니다.

이 저장소에는 비공개 안내, 사진, 문제, 개인 데이터, 작업 결과물, 키/토큰이 없습니다.
사용 중인 과제별 데이터와 결과를 이 저장소에 올리지 마세요. 공개 자료 가져오기와 외부 전송은 구분합니다.
