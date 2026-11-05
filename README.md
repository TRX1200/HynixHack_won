# HynixHack_won · Open Workbench 2.1

**문제를 분류하고, 필요한 카드 2~6개만 찾아 쓰는 MIT 범용 개발 도구.**
공개 준비용 코드·설명서·합성 예제입니다. 실제 문제·답안은 포함하지 않으며 특정 평가의 공식 허가를 대신하지 않습니다.

처음에는 [START_HERE_KO.md](START_HERE_KO.md)만 읽으세요.
웹 화면이 필요하면 [UI_DESIGN_KO.md](UI_DESIGN_KO.md)로 UI 유형과 관련 지침을 선택하세요.
v2부터 실행 소스가 저장소에 직접 들어 있습니다. **Clone 후 압축 해제가 필요 없습니다.**

## 제공된 AI에게 줄 첫 요청

```text
이 저장소의 START_HERE_KO.md를 읽어줘.
인벤토리 전체나 90개 카드를 한꺼번에 읽지 마.
먼저 실제 요구사항과 현재 실행 환경을 확인해서 문제 유형을 분류해줘.
tools/inventory.py로 관련 카드 최대 6개만 찾고, 선택한 카드만 상세히 읽어줘.
기존 코드와 스택을 유지하며 작은 기능부터 실행하고 검증해줘.
모호한 요구는 추측하지 말고 질문으로 남겨줘.
```

## 들어 있는 것

| 구성 | 실제 범위 |
|---|---|
| 검색·선택 CLI | 11개 문제 유형, 90개 카드, 29개 구조 조건, 16개 코드 구성 후보 |
| 선택 카드 | 카드 자체는 `RECIPE_ONLY`; 구현·설치 완료를 뜻하지 않음 |
| 실행 예제 7유형 | CSV, 작은 배정, 시계열 기준 예측, 이미지 행렬, RC 방전, 문서 검색, 로컬 HTTP/UI |
| Skills 20개 | 기존 18개 + `wb-field-inventory` + `wb-ui-design`; 필요한 것만 적용 |
| 기존 도구 | 문서·CSV·집계·회로 계산 6종·로컬 문서 MCP 보존 |
| 검증 계획·복구 | 요구별 `NOT_RUN` 계획 생성, 원본 대조/반례 검사, 로컬 세션 상태 기록 |
| UI 설계·검토 | 실행형 UI Router, 디자인 시스템, Dashboard/Admin/User UX, 반응형, 별도 시각 검토 |
| UI·MCP 참고 | [UI 후보](WEB_UI_KO.md), [선택 MCP](EXTRA_MCP_KO.md); 자동 설치 없음 |

## 짧은 실행 예

저장소 루트에서 Python 3.10+를 사용합니다. 환경에 따라 `python`을 `python3`로 바꾸세요.

```sh
python tools/inventory.py doctor
python tools/inventory.py search "CSV 조인 누락 중복" --limit 4 --json
python tools/inventory.py show csv-join
python tools/inventory.py plan field_inventory/examples/profiles/data_only.json --limit 4 --json
```

`search`는 작은 메타데이터 목록을 출력합니다. `show`와 해당 `field_inventory/recipes/<id>.md`는 선택된 카드에만 사용합니다.
`plan`은 명시한 문제 구조를 조건과 대조하는 휴리스틱 보조 도구이며 자동 정답/정확도 확률이 아닙니다.
미분류는 `NEEDS_CLASSIFICATION`, 상충하는 조건은 `REVIEW_REQUIRED`로 남깁니다.

## 필요한 경우에만 더 읽기

- [선택 흐름](FIELD_INVENTORY_KO.md): 문제 프로필 → 조건 확인 → 카드 → 실행 → 검증.
- [실행 예제 7유형](docs/ARCHETYPE_DEMOS.md): 입력·출력·반례와 적용 한계.
- [문제 분류 기준](field_inventory/docs/PROBLEM_CLASSIFICATION.md).
- [기초 회로·공정 계산](ELECTRONICS_CALCULATORS_KO.md): 단위·모델 가정 포함.
- [실제 테스트 결과](TEST_RESULTS.md), [변경 내용](CHANGELOG.md), [공개 범위](field_inventory/docs/PUBLICATION_AND_COMPLIANCE.md), [MIT 라이선스](LICENSE).

Python이 없으면 선택한 Markdown 카드만 읽고 기존 프로젝트의 실행기를 사용합니다.
MCP 없이 검색·선택·기본 예제를 실행할 수 있습니다. 제한된 환경에서는 허용된 도구와 자료 반입 방식만 사용하세요.
실제 과제 파일·개인정보·답안·로그는 이 공개 저장소로 보내지 않습니다.
