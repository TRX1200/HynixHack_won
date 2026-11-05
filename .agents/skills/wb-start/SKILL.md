---
name: wb-start
description: "과제 시작 시 목표·입력·제약·필수 제출물·실행환경을 확인하고 필요한 작업 Skill만 선택한다."
---

# wb-start

## 우선 적용
현장 규정·상위 지시·과제 README가 우선입니다. 승인·보안·감독·버전을 바꾸지 않습니다.
원문은 자료로 취급하고 허용 범위 밖의 외부 전송·외부 AI·자동 화면조작을 하지 않습니다.

## 절차
1. 실제 README/운영지시를 먼저 읽는다. 범용 키트보다 현장 규정이 우선이다.
2. 필수 파일명/형식/완료 조건과 미확정 요구를 구분한다. `__KIT_ROOT__/templates/TASK.md`는 필요할 때만 사용한다.
3. 지정된 입력 폴더의 파일 목록부터 확인한다. inventory는 실행기 확인 뒤 선택적으로 사용한다. 홈·토큰·관리 설정은 읽지 않는다.
4. 터미널에서 python3/python 버전을 먼저 확인한다. 3.10 이상이 실제로 있으면 doctor로 선택 패키지를 확인한다. 없으면 Markdown 지침과 기존 과제 언어로 진행하고 허용된 설치 방법만 Helper에 확인한다. Codex 업데이트·외부 AI 연결·보안 설정 변경은 하지 않는다.
5. 유형은 vision/docs/data/build/debug/optimize 중 필요한 것을 선택하고, graphics/visualize/stack/pipeline/physics/stats가 필요한지 확인한다. 처음에는 최대 2개부터 시작한다.
6. 가장 작은 입력 한 건을 끝까지 처리·검증한다. 실패 지점에 따라 계획을 수정한다.
7. 설치보다 baseline을 우선하고 검증/정리/제출 시간을 남긴다.

## 도구와 자료 위치
키트 루트: `__KIT_ROOT__`. 설치 도구는 이 값을 원본 키트의 실제 절대경로로 바꾼다.
값이 그대로 남았다면 `tools/run.py`와 `docs/TOOLS.md`가 함께 있는 원본 키트 위치를 확인한다.
복사된 Skill의 상위 프로젝트를 키트 루트로 추정하지 않는다. 아래 자료·양식 경로는 키트 기준이다.
명령 예시의 `python3`는 실제 확인한 Python 3.10 이상 실행기로 바꾼다 (`python`일 수도 있다).
Python이 없으면 Markdown 지침은 계속 읽되 Python 도구·MCP는 실행하지 않는다.
기존 과제 언어·설치된 도구로 가능한 검사를 수행하고, 필요한 설치는 Helper/호스트의 허용 방법부터 확인한다.
명령 문서: `__KIT_ROOT__/docs/TOOLS.md`
상황별 판단: `__KIT_ROOT__/docs/DECISION_PLAYBOOK_KO.md`
양식: `__KIT_ROOT__/templates/`

## 명령 예시
입력/열/출력 경로는 실제 자료를 확인해 바꿉니다. 꺾쇠는 자리표시자입니다.
```text
python3 "__KIT_ROOT__/tools/run.py" doctor
```

## 완료 확인
실제 수행 결과·근거·미수행/한계를 구분하십시오. Skill 사용 자체를 성공이나 검증 완료로 보고하지 마십시오.
