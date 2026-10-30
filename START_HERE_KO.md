# 처음 시작할 때

이 파일은 개인 준비용 설명입니다. 현장 규정·과제 README·제공 환경의 안내가 우선입니다.

## 1. 입력하는 칸부터 구분

| 현재 상태 | 넣을 것 |
|---|---|
| 터미널에 `user:~$` 같은 표시 | `codex` — 앞에 `/` 없음 |
| Codex가 실행된 AI 입력창 | 한국어 요청, 지원되는 `/mcp`·`/skills`·`/model` |
| MCP 설정 탭 | JSON만 |

터미널에서 `/codex`나 `/model`을 입력해 파일 오류가 나면 먼저 입력 칸을 확인합니다.
브라우저 IDE에 이미 편집기와 터미널이 있으면 개인 PC에 VS Code를 별도로 설치할 필요는 없습니다.

## 2. 저장소와 압축 안의 소스를 구분

이 저장소 루트에는 이 안내와 **toolkit-source.zip**이 있습니다.
실행할 Python 코드와 Skills는 압축 안의 **_toolkit/**에 있습니다.
Clone만 하고 `_prep_repo/tools/run.py`를 찾으면 없습니다. 압축을 먼저 풀어야 합니다.

실제 과제 루트에서 아직 없는 새 폴더 이름을 사용합니다. 제공된 AI에게 수행을 맡길 수 있습니다.

```sh
git clone --depth 1 https://github.com/TRX1200/HynixHack_won.git _prep_repo
```

제공된 AI에게 `CHECKSUMS.sha256`과 파일의 해시를 대조하고, 압축 항목에 절대경로·상위폴더 탈출·
심볼릭링크가 없는지 확인한 뒤 새 `_toolkit`으로 해제하도록 요청합니다.
`unzip`, Python 등의 허용된 압축 해제 도구를 먼저 확인합니다. 도구가 없으면 제공 Helper의 안내를 따릅니다.
기존 `_toolkit`이 있으면 덮어쓰거나 삭제하지 말고 위치/내용부터 확인합니다.

## 3. Python은 원격 환경에서 확인

AI에게 다음처럼 요청합니다.

```text
현재 과제 위치와 Python3/python, Node 실행 여부를 확인해줘.
Python 3.10 이상이 있으면 실제 명령으로 _toolkit/tools/run.py doctor를 실행해줘.
없으면 설치가 됐다고 가정하지 말고, Markdown Skill과 기존 프로젝트 언어로 시작해줘.
모든 선택 패키지를 설치하지 말고 꼭 필요한 것만 알려줘.
```

`python`이 없어도 `python3`는 있을 수 있습니다. 둘 다 없으면 이 키트의 Python 도구와
로컬 Python MCP는 실행할 수 없지만, AI는 Markdown Skill을 읽을 수 있습니다.
기존 프로젝트가 JS/TS이면 그 구조와 실제 설치된 실행기를 먼저 사용합니다.
Python이 꼭 필요하면 허용된 설치 방법을 Helper에 확인하고 실제 버전/작은 실행까지 검증합니다.

## 4. Skill은 두 개부터

AI에게 `_toolkit/.agents/skills/wb-start/SKILL.md`와 `wb-verify/SKILL.md`를 읽게 합니다.
Python과 설치가 허용되면 과제 루트에서 다음 설치를 맡길 수 있습니다.

```sh
python3 _toolkit/tools/install_skills.py --project . --skills wb-start wb-verify
```

실제 실행기 이름이 `python`이면 바꿉니다. 기존 Skill은 덮어쓰지 않습니다.
지원되는 `/skills`에서 인식을 확인하고, 안 되면 원본 SKILL.md를 경로로 읽도록 합니다.

## 5. MCP는 필요한 경우 연결

- 문서 반복 검색: 압축 안 `docs/MCP.md` 순서로 합성 색인을 만들고 `tools/mcp_config.py`로 실제 경로 JSON 생성.
- 웹 UI 검증: 제공 도구를 먼저 확인하고, 필요하면 `configs/mcp-playwright.example.json`과 실행 환경 확인.
- JSON은 MCP 설정 탭에 기존 서버를 보존해 병합·저장합니다. 호스트 안내에 따라 Codex 세션만 정상 재시작합니다.
- 실행된 Codex의 `/mcp`와 작은 실제 도구 호출로 확인합니다. 이름만 보이는 것은 호출 성공이 아닙니다.

문제·파일·결과물을 외부 서비스로 보내거나 개인 AI 키를 연결하지 않습니다.
차단된 설정·접속·업로드를 다른 경로로 우회하지 않습니다. 현장 안내에서 허용하지 않은 연결은 추가하지 않습니다.

## 6. 실제 요구를 받은 뒤

```text
과제 README를 읽고 필수 행동, 입력, 출력, 제출물을 먼저 정리해줘.
기존 스택을 유지하고 가장 작은 동작 한 건을 실제 실행해서 검증해줘.
오류가 나면 재현 조건부터 확인하고 최소 수정 후 같은 검사를 다시 해줘.
완료한 것, 실제 검사 결과, 아직 못 한 것을 구분해줘.
```

유형을 미리 맞히는 대신 필요한 작업 Skill 한두 개만 선택합니다.
기초 계산은 단위·가정이 일치할 때만 사용하고, UI 자료는 요구에 맞는 구성 요소를 선택하는 데 씁니다.
실제 문제와 작업 결과는 허용된 환경 안에 보관합니다. 준비 공개 저장소를 답안 전달 경로로 쓰지 않습니다.
