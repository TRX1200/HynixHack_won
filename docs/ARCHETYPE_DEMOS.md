# 실행 가능한 작은 문제 유형 예제

이 폴더는 **합성 입력으로 실제 실행되는 교육용 예제**입니다. 문제 분류 카드 전체,
실제 과제, 생산 서비스, 대규모 최적화 문제의 검증 완료를 의미하지 않습니다.
추가 패키지, API 키, 외부 서비스가 필요하지 않습니다. Python 3.10 이상과 현재
툴킷의 로컬 `workbench` 모듈을 사용합니다.

## 처음 실행하기

Clone한 저장소 루트(또는 묶음 파일의 `_toolkit`)에서 실행합니다. 이 위치에는
`field_inventory/`, `workbench/`, `tests/`가 함께 있습니다. `python`이 없다면 호스트에서
제공한 Python 실행 이름을 확인하세요. 아래 `work/demo-001`은 **아직 없는 폴더**여야 합니다.

```sh
python field_inventory/tools/archetypes.py demo all --out work/demo-001
```

한 유형만 실행할 수도 있습니다.

```sh
python field_inventory/tools/archetypes.py demo data --out work/data-001
python field_inventory/tools/archetypes.py demo assignment --out work/assignment-001
python field_inventory/tools/archetypes.py demo timeseries --out work/timeseries-001
python field_inventory/tools/archetypes.py demo image --out work/image-001
python field_inventory/tools/archetypes.py demo rc --out work/rc-001
python field_inventory/tools/archetypes.py demo documents --out work/documents-001
```

`demo` 명령은 저장소의 `examples/archetypes/`에 있는 고정 합성 입력을 사용합니다.
임의의 실제 데이터 파일을 받아 해결하는 범용 명령은 아닙니다. 실제 문제에
적용하려면 스키마, 경계 조건, 정답 기준을 다시 정의하고 해당 함수와 검증기를
작업 폴더에서 수정해야 합니다. 공개 저장소에 실제 입력이나 산출물을 넣지 마세요.

## 산출물과 PASS의 뜻

유형별 새 출력 폴더에 다음 파일이 생깁니다.

```text
input.json                 실제로 사용한 합성 입력
result.json                해당 구현을 실행한 결과
validation.json            실행한 검사, 기대값, 실제 판정과 근거 파일
cases/positive-oracle.json 정상 결과를 독립 계산과 대조한 기록
cases/negative-1.json      의도적으로 틀린 결과와 검증기 오류
cases/negative-2.json      다른 틀린 결과와 검증기 오류
cases/boundary.json        경계 입력과 실행 결과
```

데이터 예제에는 원본 및 조인 결과 CSV, 문서 예제에는 실제 텍스트와 JSONL 색인도
생깁니다. 기존 출력 폴더나 파일을 덮어쓰지 않습니다. `all` 실행의 최상위
`summary.json`은 여섯 유형의 24개 실행 검사 결과를 묶습니다.

음성 사례의 `PASS`는 **틀린 산출물을 검증기가 실제로 거부했다**는 뜻입니다.
틀린 산출물 자체가 통과했다는 뜻이 아닙니다. `expected: REJECT`, `actual: REJECT`,
`validator_errors`를 함께 읽으세요. 종료 코드 0은 이 합성 예제 검사 통과, 1은
검사 실패, 2는 실행/입력 오류입니다. 다른 업무에 대한 자동 PASS 증명은 아닙니다.

## 여섯 유형의 구현 범위

| 유형 | 실행 구현 | 별도 검증 방법 | 두 가지 반례 | 경계 |
|---|---|---|---|---|
| data | 기존 CSV 조인 감사·집계 모듈과 작은 left join | 별도 CSV 파서와 `Fraction`으로 원본 쌍·그룹 합계 계산 | 조인 행 수 위조, 그룹 합계 위조 | 헤더만 있는 두 CSV |
| assignment | 기존 유한 전수 열거 배정기 | 원본 조건을 직접 확인하는 별도 유리수 전수 열거 | 비용 0 위조, 용량/기능 위반 배정 | 필요한 기능이 없는 불가능 입력 |
| timeseries | 시간 순 holdout과 마지막 관측값 고정 예측 | 훈련 마지막 값·근거 시점·평가 오차 재계산 | 미래 시점 사용, 평가 정답을 복사한 예측 | 훈련 1개·평가 1개·값 0 |
| image | 정수 grayscale 행렬의 차이 mask와 작은 평행 이동 탐색 | 별도 픽셀 좌표·유리수 탐색·면적 계산 | 변화 픽셀 수 위조, 이동 좌표 위조 | 1×1, threshold 255의 포함 경계 |
| rc | RC 방전 전진 Euler와 절반 시간 간격 실행 | 해석해 및 이산 닫힌식으로 전체 trace 대조 | trace 값 위조, 해석해 위조 | 초기 전압 0 |
| documents | 적용 날짜로 고른 원문의 로컬 literal 색인 검색 | 날짜·실제 파일 hash·행 위치·원문 발췌 대조 | 만료 문서 포함 주장, 출처 hash 위조 | 적용 시작일 포함 |

### data

`001`과 같은 ID는 문자열로 보존합니다. 빈 키는 SQL처럼 서로 일치하지 않고,
여러 개씩 대응하는 키의 행 증식을 그대로 계산합니다. 고정 예제는 inner join
5행, left join 6행입니다. A 그룹 합계는 정확히 `0.6`, B는 `0.5`, 빈 측정값만
있는 C의 합계·평균은 `null`입니다. 분모나 누락값을 임의로 바꾸지 않습니다.

### assignment

항목별 단가, 기능, 옵션 용량, 허용 옵션만 포함한 작은 모델입니다. 고정 예제
최적 비용은 `60`이며 동일 비용의 다른 최적 배정도 허용합니다. 독립 oracle은
항목 7개, 옵션 6개, 후보 20,000개 이내만 지원합니다. 이 범위를 넘으면 오류로
중단합니다. 고정비, 최소 구매, 경로, 일정, 일반 MILP나 전역 최적화는 구현하지 않습니다.

### timeseries

원본 날짜가 이미 엄격히 증가해야 합니다. 자동 정렬하거나 같은 날짜를 합치지
않습니다. 앞 4개 관측값만 쓰고 뒤 2개를 한 번 평가합니다. 예측은 `[13, 13]`,
MAE는 `2.5`입니다. 이 값은 예제의 실행 결과이며 예측력이 좋다는 증거가 아닙니다.
학습 모델, 통계적 유의성, 튜닝, rolling backtest, 인과 추정은 포함하지 않습니다.
신뢰구간, calibration, 집단 단위 분할(grouped split)은 미구현이며 `NOT_RUN`입니다.

### image

Pillow나 이미지 파일 디코더 없이 0..255 정수 행렬만 받습니다. 각 축 128픽셀,
정수 이동 반경 4 이하이며 겹치는 면적이 원본의 60% 이상인 후보만 비교합니다.
고정 예제는 target이 오른쪽 1픽셀 이동했습니다. 정렬 전 변화 픽셀은 25개,
정렬 후 비교 가능한 20픽셀의 변화는 0개이고 경계 5픽셀은 **미비교**입니다.
target 좌표는 reference의 `(x+dx, y+dy)`입니다. 미비교 영역은 mask의 `null`로
남기며 이미지 전체가 동일하다고 주장하지 않습니다. 회전·부분 픽셀·조명 보정,
AI 분할, 실제 결함 검출, 물리 크기 보정은 구현하지 않습니다.

### rc

단위는 Ω, F, V, s입니다. 이상적인 일정 R/C의 무부하 방전만 다루고
`V(t)=V0*exp(-t/(R*C))`와 비교합니다. 고정 예제의 τ는 0.001s, 0.003s의
해석 전압은 약 0.24893534V입니다. 시간 간격을 절반으로 줄인 Euler 결과의
마지막 오차가 줄어드는지 확인합니다. 시간 간격은 τ 이하로 제한하고,
τ가 0/비유한이 되거나 절반 시간 간격이 0으로 underflow하면 오류로 중단합니다.
큰 `V/τ` 중간 계산의 overflow를 피하도록 갱신식을 배치했습니다. 매우 긴 방전은
binary64에서 해석해와 수치해가 0이 될 수 있어, 오차 0이 수학적 정확성의 증거는
아닙니다. SPICE·TCAD·재료/공정 정확성 검증은 아닙니다.

### documents

2025년/2026년의 서로 다른 가상 규칙 중 지정 날짜에 유효한 문서만 검색합니다.
날짜 구간의 양 끝은 포함합니다. `source_sha256`, `locator`, `line_start`,
`line_end`, `snippet`을 실제 로컬 원문과 확인합니다. 문서 안의 지시문처럼 보이는
문장은 실행하지 않습니다. 적용 날짜 자체는 제공한 manifest 정보이므로 진위를
보증하지 않습니다. PDF/OCR/임베딩, 의미 검색, 법적 효력 판정은 이 예제 범위 밖입니다.
서로 다른 문장 사이의 의미적 모순 자동 판정도 미구현이며 `NOT_RUN`입니다.

## 일곱 번째 유형: 로컬 HTTP 웹/API

웹/API는 별도의 서버 예제로 실행합니다.

```sh
python field_inventory/tools/web_demo.py --port 8765
```

기본 주소는 `127.0.0.1`입니다. 제공 환경의 미리보기 연결에 필요할 때만
`--host 0.0.0.0`을 사용하는 안내를 따릅니다. 터미널에 출력된 현재 실행의
reader/writer 토큰을 예제 UI에 입력합니다. 토큰은 공개 예제에 고정해서 넣지 않습니다.

이 서버는 메모리 내 최대 20개 레코드의 교육용 구현이며, 생산 인증·TLS·영구
저장소는 제공하지 않습니다. 실제 HTTP 테스트 및 브라우저 form에서
writer POST 201, 계산된 area 6, reader POST 403, GET 200으로 저장값 조회를
확인하는 별도 검사가 있습니다. 여섯 유형의 `demo all` 결과만 보고 웹/API까지
검증됐다고 판단하지 마세요. 별도 웹 테스트 명령은 다음과 같습니다.

```sh
python -m unittest discover -s field_inventory/tests -p test_web_demo.py -v
```

## 회귀 검사

```sh
python -m unittest discover -s tests -p test_archetypes.py -v
```

기본 24개 사례 외에도 큰 배정 비용의 정확성, 날짜 역전/중복, holdout 누락,
행렬 크기/boolean 오류, 가짜 unaligned 결과, RC 극단값·시간 간격,
가짜 발췌문, 날짜 종료일/만료 다음 날, 출력 보존과 다른 현재 폴더에서의 CLI
실행을 검사합니다. 실제 출력 로그와 `validation.json`을 근거로 상태를 판단하세요.
