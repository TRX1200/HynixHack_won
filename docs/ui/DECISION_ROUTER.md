# 목적에 맞는 화면과 문서 선택하기

화면 종류를 고르기 전에 요구사항과 기존 코드를 확인한다. 선택 도구는 제공한 프로필에 근거한 휴리스틱이며, 필요한 UI·기술·권한을 자동으로 확정하거나 구현하지 않는다. 모르는 값은 `unknown` 또는 `null`로 남긴다.

## 입력 프로필

```json
{
  "primary_goal": "manage",
  "ui_required": true,
  "geo_is_primary": false,
  "roles": ["viewer", "editor"],
  "records_volume": "large",
  "existing_ui": "현재 프로젝트의 목록 화면과 스타일 유지",
  "constraints": ["기존 스택 유지", "새 외부 서비스 추가 안 함"]
}
```

| 필드 | 허용 값·의미 |
| --- | --- |
| `primary_goal` | `analyze`, `manage`, `submit`, `locate`, `explore`, `present`, `unknown` |
| `ui_required` | `true` / `false` / `null`; 화면 필요 여부 확인 |
| `geo_is_primary` | `true` / `false` / `null`; 위치 판단이 핵심인지 |
| `roles` | 문자열 배열; 실제 요구된 역할만 기록, 미확인은 빈 배열 |
| `records_volume` | `small`, `large`, `unknown`; 임의의 고정 건수 기준은 없음 |
| `id` | 선택 문자열; 로컬 프로필을 구별하는 이름 |
| `existing_ui` | 선택 문자열; 현재 화면·스타일 설명 |
| `constraints` | 선택 문자열 배열; 확인된 제약 |

프로필은 허용된 로컬 작업 폴더에 일반 JSON 파일로 저장한다. 비밀·실제 개인정보를 넣지 않는다. 도구가 일반 문자열로 된 제약을 모두 해석·집행한다고 가정하지 않는다.

## 선택적 실행

키트 루트의 **터미널**에서 실행한다. 이 명령은 AI 채팅 입력이나 `/` 명령이 아니다.

```sh
python tools/ui_router.py path/to/profile.json
python tools/ui_router.py path/to/profile.json --json
```

`path/to/profile.json`은 저장한 실제 프로필 경로로 바꾼다. 환경에 따라 감지된 `python3`를 사용한다. Python이 없거나 실행이 허용되지 않으면 설치 성공을 가정하지 말고 아래 표를 문서로 읽어 선택한다. 이 CLI를 쓰기 위해 새 UI 라이브러리나 서버를 설치할 필요는 없다.

결과의 `DRAFT_UI_PLAN`은 초안 추천, `NEEDS_CLASSIFICATION`은 결정에 필요한 정보 확인 필요, `REVIEW_REQUIRED`는 충돌이나 기존 UI 검토 필요를 뜻한다. 기록량 미확인은 추가 질문으로 남기며, 확인된 주목표의 기본 흐름 선택까지 막지 않는다. `locate`에서 지리적 우선순위가 `null`이면 위치 탐색인지 확인한 뒤 선택한다. 다른 명시적 목표는 그 목표를 기준으로 시작하고 미확인 사항을 별도로 확인한다. `existing_ui`가 있으면 기존 화면을 확인하도록 검토 상태를 반환할 수 있다. `ERROR`가 나오면 입력 JSON과 필드 값을 고친다. 실행 성공 자체가 UI 구현 완료를 뜻하지 않는다.

## 추천을 판단하는 기준

| 확인된 요구 | 우선 검토할 흐름·문서 |
| --- | --- |
| UI 불필요 | 계산·CLI·기존 출력부터 완료; UI 문서·카드 추천 없음 |
| `analyze` | 질문→지표→비교→상세, [대시보드](DASHBOARD_UX.md) |
| `manage` | 목록→상세→작업, [운영자와 사용자](ADMIN_USER_UX.md) |
| `submit` | 입력→확인→결과, [운영자와 사용자](ADMIN_USER_UX.md) |
| 위치 판단이 핵심 | 지도와 목록 연결 검토; [반응형](RESPONSIVE.md)의 국소 스크롤 확인 |
| 위치는 부가 정보 | 기본 업무·탐색 흐름 유지; 좌표만으로 지도 기본 화면 확정 금지 |
| `explore` / `present` | 찾을 정보·읽기 순서·다음 행동부터; [디자인 기본값](DESIGN_SYSTEM.md) |
| 목표·필요 여부 미확인 | 관련 요구부터 확인하고 작은 기존 화면 유지; 추천을 확정안으로 취급 금지 |

여러 역할이 있으면 실제 서버 권한을 별도로 검증한다. 많은 기록은 검색·필터·상세 범위를 먼저 설계하며 특정 프레임워크 설치를 뜻하지 않는다. 기존 UI 설명은 존중할 맥락이며 자동 코드 변경 지시가 아니다.

처음에는 [디자인 기본값](DESIGN_SYSTEM.md)과 목표에 맞는 UX 문서 하나만 읽는다. 반응형 문제가 있으면 해당 문서를 추가하고, 구현 뒤 [시각 검토](VISUAL_REVIEW.md)를 별도로 진행한다.

CLI의 `documents`는 초기 설계 참고, `review_documents`는 구현 후 검토 단계의 참고다. 후속 검토까지 한 번에 읽지 말고 현재 단계에 맞는 2~3개부터 선택한다. `inventory_cards`는 최대 3개 참고 카드이며 구현·설치 명령이 아니다.

## 근거 범위

이 문서의 추천 분기는 이 키트의 설계 휴리스틱이다. W3C가 화면 종류나 이 라우터를 승인한 것은 아니다. 접근성 수치와 지원 범위는 [디자인 기본값](DESIGN_SYSTEM.md#출처) 및 [반응형](RESPONSIVE.md#출처)를 참고한다.
