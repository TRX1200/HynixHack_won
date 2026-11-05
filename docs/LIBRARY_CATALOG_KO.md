# 분야별 라이브러리 카탈로그

기준일: 2026-10-31. 아래는 공식 저장소·문서를 확인한 후보이며, 공식 시험 권장 목록이 아니다.
전체를 설치하지 않는다. 기존 프로젝트와 실행환경을 우선하며, 설치·런타임·리소스·라이선스 검토 후 필요한 것만 선택한다.
본 저장소는 링크와 사용 기준만 제공하며 외부 라이브러리·모델 가중치·폰트 파일을 재배포하지 않는다.
추가 AI나 외부 자료 전송은 도구 공개 여부와 별도로 허용 여부를 확인한다.

## 라이선스 확인
`catalog/libraries.json`의 각 `license_review`에 2026-10-31 확인한 배포 버전과
공식 PyPI/npm 메타데이터 주소를 기록했다. 이 버전을 자동 설치하는 설정은 아니다.
이 키트 자체는 MIT이며, 외부 패키지와 그 의존성은 각자의 라이선스를 따른다.
NumPy/OpenCV/scikit-image/Matplotlib 등은 배포물에 들어 있는 부속 코드의 고지도 함께 확인한다.

선택 PDF 도구인 PyMuPDF 1.26.7은 AGPL-3.0 또는 Artifex 상용 라이선스의 선택 구조다.
공개 소스 경로를 사용할 때는 AGPL 조건을 따르며, 키트의 MIT가 외부 도구에 적용되지는 않는다.
원본 라이선스 메타데이터: https://pypi.org/pypi/PyMuPDF/1.26.7/json

| 역할 | 패키지 / import | 공식 GitHub | 문서 | 주의점 |
|---|---|---|---|---|
| 이미지 입출력·crop·주석·래스터 그리기 | `Pillow` / `PIL` | [python-pillow/Pillow](https://github.com/python-pillow/Pillow) | [공식 문서](https://pillow.readthedocs.io/en/stable/reference/ImageDraw.html) | 의미 이해·전문 결함 판정 엔진 아님 |
| 정렬·윤곽·측정·기하 변환 | `opencv-python-headless` / `cv2` | [opencv/opencv-python](https://github.com/opencv/opencv-python) | [공식 문서](https://docs.opencv.org/) | cv2 패키지 변형을 중복 설치하지 않기; 의미 판정 아님 |
| 분할·영역 측정·영상처리 실험 | `scikit-image` / `skimage` | [scikit-image/scikit-image](https://github.com/scikit-image/scikit-image) | [공식 문서](https://scikit-image.org/docs/stable/) | dtype/range/좌표·threshold 근거 확인 |
| 배열·선형대수·벡터 계산 | `numpy` / `numpy` | [numpy/numpy](https://github.com/numpy/numpy) | [공식 문서](https://numpy.org/doc/stable/) | shape/broadcast/float 오차 확인 |
| ODE·최적화·signal·stats | `scipy` / `scipy` | [scipy/scipy](https://github.com/scipy/scipy) | [공식 문서](https://docs.scipy.org/doc/scipy/) | solver 성공과 모형 타당성 분리 |
| 기호 식 정리·방정식·미적분 | `sympy` / `sympy` | [sympy/sympy](https://github.com/sympy/sympy) | [공식 문서](https://docs.sympy.org/latest/) | 가정/특이점/원식 재대입; 불신 문자열 eval 금지 |
| 단위 변환·차원 점검 | `pint` / `pint` | [hgrecco/pint](https://github.com/hgrecco/pint) | [공식 문서](https://pint.readthedocs.io/en/stable/) | 물리 법칙/가정의 정당성은 별도 검증 |
| 표·join·groupby·시계열 처리 | `pandas` / `pandas` | [pandas-dev/pandas](https://github.com/pandas-dev/pandas) | [공식 문서](https://pandas.pydata.org/docs/) | 중복키·결측·분모·시간대 확인 |
| 로컬 SQL 표 집계·결합 | `duckdb` / `duckdb` | [duckdb/duckdb](https://github.com/duckdb/duckdb) | [공식 문서](https://duckdb.org/docs/stable/) | 네트워크 확장/원격 파일/auto-download 사용 경로 별도 확인 |
| 통계모형·회귀·시계열·진단 | `statsmodels` / `statsmodels` | [statsmodels/statsmodels](https://github.com/statsmodels/statsmodels) | [공식 문서](https://www.statsmodels.org/stable/) | 모형 가정·의존성·인과 한계 명시 |
| 예측·전처리·Pipeline·교차검증 | `scikit-learn` / `sklearn` | [scikit-learn/scikit-learn](https://github.com/scikit-learn/scikit-learn) | [공식 문서](https://scikit-learn.org/stable/common_pitfalls.html) | train/test 누수·그룹/시간 경계·baseline |
| 수치 그래프·PNG/SVG/PDF | `matplotlib` / `matplotlib` | [matplotlib/matplotlib](https://github.com/matplotlib/matplotlib) | [공식 문서](https://matplotlib.org/stable/) | 축·단위·폰트·렌더링 확인; 증거 수치 보존 |
| 대화형 HTML·확대·tooltip | `plotly` / `plotly` | [plotly/plotly.py](https://github.com/plotly/plotly.py) | [공식 문서](https://plotly.com/python/interactive-html-export/) | JS를 로컬 포함; CDN과 외부 통신 기본 제외 |
| Python 계산기 로컬 API | `fastapi` / `fastapi` | [fastapi/fastapi](https://github.com/fastapi/fastapi) | [공식 문서](https://fastapi.tiangolo.com/tutorial/body/) | 서버가 꼭 필요한지 먼저; auth/CORS/입력 제한 |
| Python 입력·출력 구조 검사 | `pydantic` / `pydantic` | [pydantic/pydantic](https://github.com/pydantic/pydantic) | [공식 문서](https://docs.pydantic.dev/latest/concepts/strict_mode/) | 엄격 타입과 의미/단위 검사를 별도로 수행 |
| JS JSON Schema 런타임 검증 | `ajv` / `AJV JS import` | [ajv-validator/ajv](https://github.com/ajv-validator/ajv) | [공식 문서](https://ajv.js.org/guide/getting-started.html) | npm 의존성/버전·schema 초안·업무 검증 별도 |

## 가져오는 전략
- 내 준비 저장소에는 어떤 작업에 무엇을 쓸지, 설치명/import명, 최소 예제, 검증 기준, fallback을 보관한다.
- 외부 프로젝트 소스 전체를 모두 clone하지 않는다. 허용된 환경이면 패키지의 배포물을 쓰는 편이 단순할 수 있다. 소스 수정이 필요할 때만 특정 commit을 검토한다.
- 자동 설치, 임의 curl-pipe-shell, 전역 runtime 업데이트를 하지 않는다. 기존 패키지와 충돌하면 중단하고 범위를 줄인다.
- 잠금 파일은 실제 검증한 환경에 대한 기록이다. OS/Python/아키텍처가 달라져도 동일하게 동작한다고 보장하지 않는다.
- 공개 저장소라는 이유만으로 안전·라이선스·과제 적합성이 보장되지 않는다. 외부 통신, telemetry, model download, 실행 hook을 확인한다.
- 로컬 메타데이터 확인: `python tools/library_inventory.py` (설치·네트워크·모듈 import를 하지 않음).

## 상태 표기
공식 문서 확인 / 현재 컨테이너에서 특정 기능 실행 / 실제 제공 환경에서 연결 확인은 서로 다르다.
실제 실행 범위는 TEST_RESULTS.md를 따른다. 목록에 있다고 전체 기능을 시험한 것은 아니다.
