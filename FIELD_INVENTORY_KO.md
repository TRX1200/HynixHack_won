# 문제를 분류한 뒤 필요한 것만 읽기

검색기·라우터는 Python 표준 라이브러리로 로컬에서 실행합니다. 네트워크·AI API·MCP가 필요 없습니다.
분류기를 실행하기 위해 전체 카탈로그를 AI 대화에 붙여넣지 마세요. 프로그램이 색인을 읽고 작은 결과만 출력합니다.

1. 요구 산출물과 입력을 먼저 확인합니다. 웹, 데이터, 최적화, 통계, 영상, 과학, 문서, 공간, 보고, 통합, 품질/보안의 복합 유형도 가능합니다.
2. `search`로 최대 6개 후보만 찾습니다. 명시한 구조 조건은 `plan`으로 대조합니다.
3. 선정된 ID만 `show`로 열고 레시피의 적용 조건·피해야 할 경우·대체안·검증을 읽습니다.
4. 실제 코드가 있는지 확인합니다. `RECIPE_ONLY`는 구현 지침이지 설치된 솔버가 아닙니다.
5. 최소 구현을 실행합니다. 실제 입력과 요구에서 별도 검증 기준을 만들고 고의 오류도 확인합니다.

| 목적 | 저장소 루트에서의 명령 |
|---|---|
| 환경 확인 | `python tools/inventory.py doctor` |
| 짧은 검색 | `python tools/inventory.py search "CSV 조인 중복" --limit 4 --json` |
| 한 카드 열기 | `python tools/inventory.py show csv-join` |
| 조건 분류 연습 | `python tools/inventory.py plan field_inventory/examples/profiles/data_only.json --limit 4 --json` |
| 검증 계획 연습 | `python tools/contract_factory.py field_inventory/examples/profiles/data_only.json --format json` |
| 구현 예제 | [실행 가능한 7유형](docs/ARCHETYPE_DEMOS.md) |

라우팅은 확정된 사실을 입력받는 휴리스틱입니다. 추천을 강제 실행하지 않으며 패키지나 서비스를 설치하지 않습니다.
실행 예제의 테스트 범위는 `TEST_RESULTS.md`를 따릅니다.
