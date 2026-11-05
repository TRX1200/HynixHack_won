# 계산·이미지·시각화·언어 연결·물리·통계 대비

## 이번 확장의 성격
범용 지침 6개, 공식 라이브러리 카탈로그, 작은 데이터 계약 예제, 수치 검증 예제를 추가했다.
임의 결함탐지 시스템·범용 통계 자동판정·고급 물리 해석기·생성형 이미지 모델을 완성한 것은 아니다.

## 공통 라우팅
작업 요구 -> 허용 도구/자원 -> 작은 baseline -> 선택 라이브러리 -> 코드/파일 실행 -> 검증 -> 설명.
라이브러리는 실제 계산, Skill은 선택·절차, MCP는 반복 호출 인터페이스이다. 모든 기능을 MCP로 포장하지 않는다.

## 이미지 생성/분석
- 생성형 모델 이미지: 호스트가 명시적으로 제공·허용하는 기능인지 먼저 확인. 공개 model repo라도 자동 허용 아님.
- 코드 기반 이미지: SVG/Pillow/Matplotlib로 모식도·주석·정량 그래프를 구성한다. 실측 사진처럼 제시하지 않는다.
- 이미지 분석: 촬영·정렬·크기·좌표를 확인하고 전처리와 물리 판정을 분리한다. 실제 판정 label 없으면 accuracy를 주장하지 않는다.
- 준비 예제: 위치만 이동한 정상상태 vs 실제 결함, crop 좌표 round trip, 입력 누락/손상.

## 데이터 시각화
질문부터 선택: 시간 변화/집단 차이/분포/관계/오차. 평균만으로 분포를 대체하지 않는다.
실측/계산/모의/불확실성을 구분한다. 축·단위·표본 수·분모·결측 처리와 source를 함께 남긴다.
정적 Matplotlib PNG/SVG 또는 자체완결 Plotly HTML부터. 웹앱을 만드는 것은 필요할 때만.

## 수식·물리
기호표·단위·convention·적용 법칙·가정·초기/경계조건을 먼저 기록한다.
기호해 -> 원식 대입/초기조건/특이점. 수치해 -> 수렴/잔차/해석해/보존법칙 중 유효한 검사.
단위 검사와 solver success가 모형의 물리적 타당성을 보장하지 않는다.
RF 예: Hz/rad·s^-1, degree/radian, peak/RMS, amplitude/power, 복소 켤레·부호 convention을 혼용하지 않는다.

## 통계
연구 질문 -> 독립 표본단위 -> 설계 -> 기술통계/추론/예측/인과 구분 -> 방법 -> 진단 -> 효과·구간·한계.
반복 측정과 서로 다른 대상의 비교를 구분한다. 그룹/시간 의존 데이터는 split과 재표집 단위를 맞춘다.
함수를 호출할 수 있다는 것과 그 방법이 적절하다는 것은 다르다. 원인 주장은 설계/가정 없이는 하지 않는다.
분석 계획과 사후 변경 이력을 남기며 p값만으로 성공/실패를 판정하지 않는다.

## 예시 복합문제 (자체 제작 가상 상황)
제품 이미지와 장비 로그로 재검사 증가 원인을 분석하고 현업이 쓸 도구를 만든다.
1. 목표가 결함 누락 감소인지 재검사 감소인지 확인.
2. 이미지 단위가 시편/프레임 중 무엇인지, 로그 join 키와 시간 정렬이 맞는지 확인.
3. 밝기/정렬/촬영 배율과 실제 결함을 분리해 검토.
4. 라벨이 최종 판정인지 1차 검사기의 신호인지 확인.
5. 동일 로트 반복 표본을 독립 데이터로 세지 않고 통계 계획 수립.
6. Python 분석 -> 단위/ID/결측 계약 JSON -> 필요한 JS/TS 화면.
7. 대표 원문·원본과 계산, 실패 입력, UI 표시 단위를 다시 확인.
8. 결과, 실제 검증, 알려진 한계를 설명.

## 확장 순서
기존 wb-start/verify -> 필요한 새 Skill 한두 개 -> 최소 예제 -> 실제 제공 환경 확인.
MCP 서버를 늘리기 전에 일반 스크립트로 기능과 검증을 완성한다.
범용 지침을 읽었다고 문제를 이해한 것으로 간주하지 않는다. 사용자가 핵심 가정·선택·검증을 직접 설명해야 한다.

## 공식 근거
- Pillow drawing: https://pillow.readthedocs.io/en/stable/reference/ImageDraw.html
- Matplotlib: https://matplotlib.org/stable/
- Plotly offline HTML: https://plotly.com/python/interactive-html-export/
- SymPy numerical solving: https://docs.sympy.org/latest/guides/solving/solve-numerically.html
- SciPy ODE: https://docs.scipy.org/doc/scipy/reference/generated/scipy.integrate.solve_ivp.html
- Pint units: https://pint.readthedocs.io/en/stable/getting/tutorial.html
- Welch / independent samples: https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.ttest_ind.html
- statsmodels diagnostics: https://www.statsmodels.org/stable/diagnostic.html
- prediction leakage: https://scikit-learn.org/stable/common_pitfalls.html
