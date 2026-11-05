# 언어 선택과 단계 간 데이터 계약

이 문서는 도구의 공식 우열이 아니라 제한된 작업시간을 위한 설계 제안이다.

## 기본 선택
| 상황 | 우선 후보 | 바꾸는 조건 |
|---|---|---|
| 제공 프로젝트 있음 | 기존 언어/구조 유지 | 요구 불충족을 입증한 경우만 |
| 수식·통계·이미지 계산 | Python | 제공 환경 또는 실측 성능이 다른 접근을 요구 |
| 브라우저 입력·화면·상호작용 | 기존 JS/TS | 이미 있는 UI를 불필요하게 교체하지 않음 |
| 작은 웹 기능·간단 집계 | JS/TS 하나로 완료 가능성 먼저 | Python 과학 라이브러리가 실질적으로 필요할 때 분리 |
| 여러 표 join/group/조회 | 기존 pandas/SQL, 필요 시 DuckDB | 데이터 크기·설치·메모리 기준으로 선택 |
| 반복 계산이 느림 | profile -> vectorization/알고리즘 개선 | 그래도 병목이면 C++ 등 compiled core 검토 |
| MATLAB/R 코드 제공 | 실행기·라이선스·패키지부터 확인 | 개념이 같아도 blind translation 하지 않음 |

## 가장 작은 연결부터
A: Python 계산 -> result.json -> 정적 HTML/SVG. 서버와 React가 필요 없는지 먼저 본다.
B: 사용자 입력마다 재계산 필요 -> Python 함수 + 로컬 FastAPI -> JS/TS UI. 한 곳에서 계산하고 양쪽에서 입력을 검증한다.
C: 기존 Node 앱 유지 + 계산기 subprocess -> 고정 인자 배열로 Python 호출. stdout JSON, stderr 로그, timeout/exit code 확인.
D: C++와 Python 연동은 빌드·배포·FFI 비용을 포함해 선택한다. 초기 기본안이 아니다.

## 계약 필드
schema_version, ID 문자열, 값 타입, 배열 shape, 단위, 시간대, null 의미, 오류 상태, 사용/누락 표본 수를 정한다.
원본 중복 키와 missing 값을 감추지 않는다. NaN/Infinity는 JSON으로 보내지 않는다.
입력 검증과 업무 의미 검증은 다르다. `value=300`이 number인 것은 확인할 수 있지만 K인지 degC인지는 계약이 필요하다.
TypeScript 타입은 런타임 JSON을 자동 검증하지 않는다. 외부 경계에는 Ajv 등 validator 또는 명시 검사 필요.

## 동작 예제
`examples/bridge`는 합성 온도 3개를 Python에서 검사·변환해 JSON으로 내보내고 Node에서 다시 검증한다.
앞자리 0 ID, null, 전체/유효 개수, 잘못된 단위, bool-as-number, non-finite 값과 합계 불일치를 검사한다.
이 예제는 FastAPI/React 앱도, 일반 JSON Schema 엔진도 아니다. 일반화할 때 schema와 실제 업무 검사를 함께 확장한다.

## 출처
- FastAPI request body: https://fastapi.tiangolo.com/tutorial/body/
- Pydantic strict validation: https://docs.pydantic.dev/latest/concepts/strict_mode/
- Ajv: https://ajv.js.org/guide/getting-started.html
- TypeScript basics/type erasure: https://www.typescriptlang.org/docs/handbook/2/basic-types.html
