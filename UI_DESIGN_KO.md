# UI를 먼저 선택하고, 필요한 지침만 읽기

웹 화면이 필요한 과제라면 [UI 시작점](docs/ui/README.md)에서 시작합니다.
API/CLI만 요구되면 화면을 추가하지 않습니다. 기존 UI·브랜드·컴포넌트가 있으면 유지합니다.

| 필요 | 읽을 문서 |
|---|---|
| 색·타이포·여백·버튼·카드·테이블 통일 | [Design System](docs/ui/DESIGN_SYSTEM.md) |
| KPI와 분석 결과 배치 | [Dashboard UX](docs/ui/DASHBOARD_UX.md) |
| 운영자/일반 사용자 화면과 권한 | [Admin/User UX](docs/ui/ADMIN_USER_UX.md) |
| 작은 화면·긴 표·지도 대응 | [Responsive](docs/ui/RESPONSIVE.md) |
| 과제에 맞는 화면 선택 | [Decision Router](docs/ui/DECISION_ROUTER.md) |
| 기능 테스트와 별도의 시각 검토 | [Visual Review](docs/ui/VISUAL_REVIEW.md) |

표 전체의 문서를 한 번에 읽지 않습니다. 공통 디자인 기준과 해당 UX 문서부터 선택하고,
구현 후 Visual Review를 읽습니다. 라이브러리가 필요할 때만 [기존 OSS 후보](WEB_UI_KO.md)를 봅니다.

```sh
python tools/ui_router.py examples/ui/dashboard.json --json
```

이 명령은 합성 예제입니다. 실제로는 확인한 요구를 `schemas/ui_profile.schema.json` 형식의
로컬 프로필에 적습니다. 라우터는 UI 유형·이유·읽을 문서를 추천하며 화면을 생성하거나 품질을 인증하지 않습니다.
MCP·API 키·외부 네트워크 없이 실행됩니다. Python이 없으면 Decision Router 문서의 표를 사용합니다.

제공 AI에게 줄 요청:

```text
UI_DESIGN_KO.md를 읽고, 실제 사용자 목표와 기존 화면을 기준으로 UI 유형을 골라줘.
확인한 조건으로 tools/ui_router.py를 실행하고, 선택된 UI 지침만 참고해줘.
색·타이포·간격·버튼·카드·테이블을 하나의 디자인 시스템으로 맞춰줘.
데스크톱과 모바일, loading/empty/error 상태를 확인하고 기능 검증과 시각 검토를 따로 보고해줘.
제공 환경이 허용하는 미리보기와 검사 방법만 사용해줘.
```
