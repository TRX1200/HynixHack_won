# Python -> JSON -> JavaScript 미니 예제

합성 입력이며 실제 업무/시험 자료가 아니다. Python 3.10+, Node 18+ 후보(실제 테스트 버전은 TEST_RESULTS.md 참조).
추가 npm/pip 설치, 서버, 외부 호출, 브라우저 자동조작 없음.

```bash
python examples/bridge/produce.py examples/bridge/input.json --output /tmp/wb-result.json
node examples/bridge/consume.mjs /tmp/wb-result.json
```

Windows에서는 `/tmp/wb-result.json` 대신 존재하는 연습 폴더의 새 파일 경로를 양쪽 명령에 동일하게 쓴다.
이미 출력이 있으면 덮어쓰기를 거절한다. 별도 새 출력 이름을 사용한다.

출력: 전체 3개 중 유효 2개, 평균 약 27.85 degC. ID의 앞자리 0은 유지하고 null은 평균에서 제외하되 건수에 남긴다.
온도 상한 1,000,000은 예제의 명시적 도메인 제한이며 일반적인 물리 한계가 아니다.
Python: 입력/결과 검증 + 단위 변환 + 유효 표본 평균. Node: 결과 구조와 의미를 다시 검사하고 요약.
`result.schema.json`은 구조 명세이고, 두 프로그램의 명시 검사는 수치·건수·ID 의미를 추가 검증한다.
Node JSON.parse는 중복 JSON key를 독립적으로 탐지하지 않는다. 이 예제는 중복 키를 거절하는 Python 생산자의 출력만 소비한다.
불신 외부 JSON을 추가로 받는 앱으로 확장하면 그 경계의 duplicate-key 정책도 별도로 구현해야 한다.
TypeScript 선언 파일만 붙여도 이 검사가 자동 구현되는 것은 아니다.
