# 실제 검증 기록

기준일: 2026-10-29. 버전: 1.0.0.

## 실행 환경
- Python 3.13.5, Linux.
- Pillow 12.3.0.
- PyMuPDF 1.26.7.
- 외부 모델/API나 실제 시험 데이터를 호출하지 않았습니다.

## 확인된 실행
| 검사 | 결과 | 범위 |
|---|---|---|
| `python -m unittest discover -s tests -v` | **66개 통과** | core / CLI / optional image+PDF / MCP dispatch / selected skill installation |
| `python -S -m unittest discover -s tests -v` | **59개 통과, 선택 의존성 7개 skip** | site-packages 없는 조건에서 핵심 기능 유지 |
| `python -S tools/smoke_mcp.py` | **6개 응답/조건 확인** | 실제 subprocess stdio 초기화·목록·검색·조회·통계·없는 ID 거절 |
| `python -m compileall -q workbench tools mcp tests` | 통과 | Python 구문 컴파일 |

## 의도적으로 포함한 실패 사례
중복 헤더, 열 수 불일치, 빈 CSV, 멀티라인 셀, CP949,
앞자리 0 ID, 빈 키, N:M 결합 행 증가, 결측과 0 구분, NaN/Infinity,
이미 있는 파일 덮어쓰기, symlink/경로 이탈, 잘못된 manifest,
순서의 유일/비유일/순환, 근거 없는 fact, 역전된 시행일,
잘못된 근거 참조, 임의 파일명 MCP 요청, 잘못된 도구 인자,
과제 제약 위반 배정, 시간/상태 제한 시 최적성 과장 방지,
HTML escape, 실행 근거 없는 PASS 거절, 이미지 crop 범위·크기 불일치.

## 이 검증이 입증하지 않는 것
- 실제 Cofa/제공 Codex 버전에서 Skill 자동 탐지나 MCP 연결이 된다는 보장은 없습니다.
- Windows 사용자 PC의 게시 스크립트, GitHub 실제 저장소 생성은 아직 실행하지 않았습니다.
- 이 도구가 모델의 정답률이나 평가 점수를 개선한다는 비교 실험은 하지 않았습니다.
- 파일 추출, 구조 검사, 최적화 결과는 업무 의미의 정확성을 보장하지 않습니다.
- 제한된 테스트는 모든 보안 문제·대형 입력 성능을 증명하지 않습니다.
- 별도 AI harness/원격 에이전트 플랫폼을 구현한 것은 아닙니다. 제공 Codex 위에서 쓰는 운영 도구입니다.

최종 제출의 핵심 결과는 원문과 독립 사례로 다시 확인해야 합니다.
