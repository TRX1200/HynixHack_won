# 처음 시작: 전체 목록 대신 필요한 카드만

## 1. 제공 환경의 AI에게 요청하기

터미널의 `user:~$` 같은 입력 위치에서는 `codex`를 실행합니다. 앞에 `/`를 붙이지 않습니다.
Codex가 실행된 뒤 아래처럼 요청하세요. 제공 환경이 허용하는 범위에서 수행합니다.

```text
https://github.com/TRX1200/HynixHack_won
이 공개 저장소를 기존 과제와 구분되는 새 폴더로 clone하고 START_HERE_KO.md만 먼저 읽어줘.
이번 버전은 소스가 직접 들어 있으니 tools/inventory.py가 있는지 확인해줘.
인벤토리 전체와 90개 레시피를 한꺼번에 읽지 마.
실제 과제 README, 기존 코드, 실행 환경을 확인해 문제 유형과 미확정 조건을 정리해줘.
검색기로 관련 카드 최대 6개만 찾고, 고른 카드만 읽어서 작은 구현과 검증에 활용해줘.
```

공개 HTTPS 저장소는 GitHub 로그인/토큰 없이 내려받을 수 있습니다. 실제 환경의 네트워크 허용 여부는 별도입니다.
기존 폴더가 있으면 덮어쓰거나 삭제하지 말고 먼저 현재 내용과 버전을 확인합니다.

## 2. 처음 실행할 것

명령은 **받은 저장소 루트** 기준입니다. Python 3.10+가 있는지 먼저 확인합니다.
`python` 대신 `python3`가 제공될 수 있습니다.

```sh
python tools/inventory.py doctor
python tools/verify_release.py
python tools/inventory.py search "현재 필요한 작업의 짧은 설명" --limit 4 --json
```

검색은 단어·한국어 별칭 기반 후보 찾기이며 점수는 확률이 아닙니다.
카드 ID를 확인하고 `python tools/inventory.py show 카드ID`로 선택한 상세 정보만 읽습니다.
Python이 없으면 `field_inventory/catalog/README.md`에서 해당 분야 인덱스 하나와 카드 몇 개만 읽습니다.

## 3. 구조적 조건으로 선택하기

AI가 실제 요구에서 확인한 사실만으로 로컬 `problem_profile.json`을 작성하게 합니다.
필드 형태는 `field_inventory/schemas/problem_profile.schema.json`과 가장 가까운 합성 프로필 하나를 참고합니다.
확인 못 한 조건은 `unknowns`에 기록합니다.

```sh
python tools/inventory.py plan /실제/로컬/problem_profile.json --limit 6 --json
python tools/contract_factory.py /실제/로컬/problem_profile.json --format json --out /새/로컬/validation_plan.json
```

경로는 실제 값으로 바꿉니다. 프로필·검증 계획·실제 결과는 과제 작업 공간 안에 보관합니다.
`NEEDS_CLASSIFICATION`이면 요구를 더 확인하고, `REVIEW_REQUIRED`이면 충돌을 해결합니다.
검증 계획은 처음에 모두 `NOT_RUN`입니다. 계획 생성 자체로 검증 통과가 되지 않습니다.

## 4. Skills와 실행 예제는 선택해서

처음에는 `.agents/skills/wb-field-inventory/SKILL.md`와 `wb-verify/SKILL.md`만 직접 읽어도 됩니다.
프로젝트 로컬 Skill 등록이 허용되면 필요한 것만 복사할 수 있습니다.

```sh
python tools/install_skills.py --project /실제/과제/루트 --skills wb-field-inventory wb-verify
```

기존 Skill을 덮어쓰지 않습니다. 등록 인식은 실제 제공 Codex에서 확인합니다.
실행 예제는 [docs/ARCHETYPE_DEMOS.md](docs/ARCHETYPE_DEMOS.md)에서 고릅니다.
합성 데모 통과는 실제 과제의 요구를 검증했다는 뜻이 아닙니다.

## 화면이 필요한 경우

[UI_DESIGN_KO.md](UI_DESIGN_KO.md)를 읽고 `wb-ui-design` 또는 `tools/ui_router.py`로 필요한 UI 지침만 고릅니다.
대시보드·관리 화면·입력 폼·지도는 실제 사용자 목표로 선택하고 기존 UI를 우선 유지합니다.
기능 검사와 디자인 검토를 별도로 기록합니다. API/CLI 전용 과제에는 UI를 추가하지 않습니다.

## 5. MCP와 재접속

검색기와 코드 선택기는 CLI이므로 MCP 연결이 필요 없습니다.
MCP가 필요하면 제공 AI에게 현재 실행기·경로·허용 범위에 맞는 설정 JSON을 요청합니다.
기존 서버를 보존해 설정을 저장하고, 호스트 안내에 따라 Codex만 정상 재시작한 뒤 실제 호출로 확인합니다.

`tools/session_state.py --help`를 보고 별도 로컬 파일에 현재 상태와 다음 단계를 기록할 수 있습니다.
이 도구는 저장된 명령을 자동 실행하지 않고, 사용자가 적은 통과 주장도 인증하지 않습니다.
재접속하면 파일·서버·최근 실제 테스트를 확인한 뒤 이어 갑니다.

`toolkit-source.zip`은 전체 소스의 별도 배포본입니다. Clone으로 `tools/`가 있으면 해제하지 않습니다.
ZIP만 받은 경우 `CHECKSUMS.sha256`을 대조하고 새 폴더에 풀어 `_toolkit/`을 루트로 사용합니다.
제한된 응시 환경에는 개인 PC 파일을 업로드하는 방식으로 반입하지 않습니다.
