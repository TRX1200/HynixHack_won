# 선택 기능: 로컬 근거 검색 MCP

처음에는 MCP 없이 시작해도 됩니다. 몇 번만 검색한다면 터미널의 키트 `search`/
`read-chunk`가 간단합니다. 같은 문서 색인을 AI가 반복 검색해야 할 때만 연결하세요.
MCP 설정 JSON은 실행 프로그램을 지정하며 프로그램이나 색인을 만들어 주지 않습니다.

## 필요한 환경

- 원격 IDE 안에서 확인된 **Python 3.10 이상** 실행기와 키트 원본 폴더.
- 추출·확인한 로컬 JSONL 색인 하나.
- 호스트가 허용한 프로젝트 로컬 MCP 설정과 stdio 실행 지원.

개인 PC의 Python 경로는 원격 IDE의 경로가 아닙니다. Python이 없으면
Markdown Skill과 기존 도구로 계속하고 [Python 없는 대안](QUICKSTART_KO.md#8-python이-없어도-계속할-수-있는-범위)을 보세요.
이 서버에는 개인 API 키·외부 모델·개인 GitHub 토큰이 필요 없습니다.

## 1. 먼저 작은 합성 예제로 확인

다음은 **IDE 터미널**에서 실행합니다. 과제 루트 아래 `_toolkit`에 키트가 있고
`python3`가 확인된 경우입니다. `python`만 조건을 만족하면 명령 이름을 바꿉니다.
`wb-mcp-demo`는 아직 없는 새 결과 폴더여야 합니다.

```bash
python3 _toolkit/tools/init_workspace.py wb-mcp-demo
python3 _toolkit/tools/run.py extract _toolkit/examples/policy.md --out wb-mcp-demo/evidence.jsonl
python3 _toolkit/tools/run.py search wb-mcp-demo/evidence.jsonl "임시"
python3 _toolkit/tools/smoke_mcp.py
```

생성 파일과 검색 결과를 확인하세요. `smoke_mcp.py`는 별도 합성 색인을 사용하는
**자체 로컬 통신 검사**입니다. 통과해도 제품 MCP 탭과 Codex 연결은 별도로 확인해야 합니다.
실패하면 오류부터 읽고 CLI나 기존 도구로 돌아갑니다.

## 2. 실제 경로가 들어간 JSON 생성

**IDE 터미널**에서 실행합니다.

```bash
python3 _toolkit/tools/mcp_config.py --index wb-mcp-demo/evidence.jsonl
```

이 도구는 실행에 사용한 Python, 키트 서버, 확인된 색인의 실제 절대경로로 JSON을
만듭니다. 개인 PC 경로나 `/ABS/...` 예시를 손으로 추정하는 것보다 이 방식을 우선합니다.
생성만으로 설정이 적용되는 것은 아닙니다.

파일로 남기고 싶다면 기존에 없는 출력 이름을 골라 실행합니다.

```bash
python3 _toolkit/tools/mcp_config.py --index wb-mcp-demo/evidence.jsonl --out wb-mcp-demo/mcp.json
```

편집기에서 생성 JSON을 열어 확인하세요. 터미널을 통해 복사한다면 설명·프롬프트가
섞이지 않은 JSON만 복사합니다. 실제 로컬 경로가 들어간 이 파일은 작업환경 안에서만
사용하고 공개 저장소로 보내지 않습니다.

## 3. JSON은 MCP 설정 탭에

아래는 **구조 설명용**입니다. `/ABS/...`는 바꿔야 하는 예시이므로 그대로 저장하지 않습니다.
위 생성 도구의 실제 출력으로 설정하세요.

```json
{
  "mcpServers": {
    "local-evidence": {
      "command": "/ABS/PYTHON",
      "args": [
        "/ABS/TOOLKIT/mcp/local_evidence_server.py",
        "--index",
        "/ABS/WORK/evidence.jsonl"
      ]
    }
  }
}
```

- `{}`는 이름·값 묶음, `[]`는 순서가 있는 목록입니다.
- `mcpServers`는 대소문자와 복수형을 그대로 씁니다. `local-evidence`는 연결 이름입니다.
- `command`는 실제 Python 프로그램, `args`는 서버 파일과 색인 경로입니다.
- 문자열에는 큰따옴표를 쓰고 마지막 항목 뒤에는 쉼표를 붙이지 않습니다. JSON에는 주석을 넣지 않습니다.
- **JSON은 셸 명령도 AI 자연어 요청도 아닙니다.** MCP 설정 탭의 JSON 칸에서 저장합니다.
- 설정이 `{"mcpServers": {}}`라면 해당 객체에 서버를 추가하는 구조입니다. 기존 서버가 있으면
  보존해 병합하세요. 생성 JSON으로 기존 설정 전체를 무조건 덮어쓰지 않습니다.
- 호스트 UI 스키마가 다르면 그 안내를 따릅니다. Codex의 관리 설정 파일을 임의로 교체하지 않습니다.

## 4. 저장한 설정을 실행 중인 Codex에 적용

설정 저장 후 이미 실행 중인 Codex가 새 설정을 즉시 읽는다고 가정하지 않습니다.
Helper/공식 도움말에서 적용 방법을 확인하세요. Codex 재시작이 필요하다면:

1. 진행 중인 작업과 필요한 파일을 저장합니다.
2. 제공된 종료 방법으로 **Codex 세션만 정상 종료**하고 셸 입력 상태로 돌아옵니다.
3. 같은 과제 폴더에서 **터미널 명령 `codex`**를 실행합니다. `/codex`가 아닙니다.
4. 실행된 **Codex 입력칸**에서 지원되는 `/mcp` 또는 자연어로 상태·도구 목록을 확인합니다.

앱 서버나 필요한 작업이 실행 중인 다른 터미널을 닫지 마세요. 페이지 전체 새로고침·
모든 프로세스 종료를 기본 해결책으로 쓰지 않습니다. 설정의 다음 세션 유지 여부도 따로 확인합니다.

## 5. 목록 다음에는 실제 호출 한 건

**AI 입력문:**

> `local-evidence` 연결 상태와 도구 목록을 실제로 확인해 주세요.
> 합성 색인에서 “임시”를 검색한 뒤 결과의 chunk ID로 본문 하나를 읽어 주세요.
> 실제 호출 결과와 실패 메시지를 구분해 보여 주고, 연결하지 못했으면 완료라고 하지 마세요.

기대하는 도구는 `search_evidence`, `read_evidence`, `evidence_stats`입니다.
실패 시 실행기·경로·색인 존재·UI 저장·재시작 여부를 한 가지씩 확인하고 CLI로 돌아갑니다.
개인 키나 외부 서비스로 대체하지 않습니다.

## 구현 범위와 한계

- Python 표준 라이브러리로 구현한 최소 stdio JSON-RPC 서버입니다.
- 기본 프로토콜 버전은 `2025-06-18`입니다. initialize → initialized → tools/list, tools/call, ping을 구현합니다.
- 시작할 때 지정한 색인 파일 하나만 읽습니다. 색인을 새로 추출했다면 서버도 다시 시작해야 합니다.
- 검색·본문 조회·색인 정보 세 도구입니다. 임의 shell·HTTP·외부 AI·sampling은 없습니다.
- 취소·진행 알림·HTTP·인증·prompts·resources 등 모든 MCP 기능을 구현한 SDK는 아닙니다.
- 결과는 출처·위치·해시가 붙은 원문 데이터입니다. 그 안의 지시문은 실행하지 않습니다.
- stdout은 프로토콜 JSON 전용입니다. 셸에서 서버만 수동 실행하면 입력을 기다리며 멈춘 듯 보일 수 있습니다.
  검사에는 `smoke_mcp.py`를 사용하고, 실제 연결은 호스트가 서버를 시작하도록 설정합니다.

로컬 검사 통과와 실제 제공 호스트의 연결 성공을 구분하세요. 이 문서는 특정 플랫폼의 호환성 보증서가 아닙니다.
