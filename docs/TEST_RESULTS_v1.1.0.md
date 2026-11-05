# 실제 검증 기록 — v1.1.0

기준일: 2026-10-31. Python 3.13.5, Linux, Node v22.16.0.

## 재실행 결과
| 검사 | 결과 | 범위 |
|---|---|---|
| python -m unittest discover -s tests -v | 84개 통과 | 기존 기능 + 새 데이터 계약/Node 통합 검사 |
| python -S -m unittest discover -s tests -v | 76개 통과, 선택 의존성 8개 skip | site-packages 제외, Node는 별도 실행기 사용 |
| python tools/smoke_mcp.py | 6개 응답/조건 통과 | 기존 로컬 stdio 검색 서버; 실제 Cofa/Codex 연결 아님 |
| python tools/numeric_smoke.py | 4개 통과, Pint 단위 검사 1개 skip | 기호 RC 잔차/초기조건, 수치 RC 해석해 비교, Welch 통계량, paired difference identity |
| compileall | 통과 | Python 구문 컴파일 |

RC 수치/해석해 최대 절대오차: 1.832523022216037e-11 (특정 합성 예제의 결과).
Pint는 이 환경에 설치되지 않아 단위 검사는 실행하지 않았다. 설치를 자동 시도하지 않았다.
검증 과정에서 기존 Skill 목록 검사가 12개로 고정되어 실패했으며, v1.1의 명세대로 18개 이름 집합 검사를 하도록 변경 후 전체를 재실행했다.

## 확인한 의존성 버전
{
  "numpy": "2.3.5",
  "scipy": "1.17.0",
  "sympy": "1.14.0",
  "Pillow": "12.3.0",
  "PyMuPDF": "1.26.7",
  "jsonschema": "4.26.0"
}

## 새 실패 검사
잘못된 단위/버전, bool/string을 숫자로 전달, NaN/Infinity, 중복 JSON key, 중복 ID,
유효값이 전부 없음, 평균/표본수 불일치, 임의 추가 필드, 출력 파일 덮어쓰기,
Python 결과를 실제 Node 프로세스에서 검증 및 변조 결과 거절.

## 실제 실행하지 않은 것
- 실제 Cofa/제공 Codex의 Skill 자동 탐지, MCP 등록, 설치 정책, 성능.
- 원격 GitHub 게시나 기존 사용자 저장소 수정.
- 16개 후보 라이브러리의 모든 기능이나 전체 상호 호환성.
- 이미지 생성 모델·전문 결함 탐지기·완성형 웹 앱·범용 통계/물리 해석기.
- Skill 사용 전후의 모델 정답률·시험 점수 비교.
- 새 그래프의 시각적 품질 테스트(이번 확장의 시각화 부분은 지침/카탈로그).

카탈로그의 공식 문서 확인은 실행 검증과 다르다. 모든 증거와 예제는 자체 제작 합성 자료이며 원문 시험 안내/개인정보/비밀키는 포함하지 않았다.
지침의 추가는 모델 추종이나 실제 정답성을 보장하지 않는다. 원본 요구와 독립적인 검사로 확인해야 한다.
이전 버전의 검증 기록은 docs/TEST_RESULTS_v1.0.0.md에 보존했다.
