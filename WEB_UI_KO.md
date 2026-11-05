# 웹 UI: 기존 스택에 맞는 작은 OSS 선택

이 문서는 UI 후보와 선택 기준입니다. 라이브러리 코드·스타터·완성된 과제 답안을
포함하지 않으며 자동 설치하지 않습니다. 원격 IDE에 Node나 특정 버전이 있다고 가정하지 않습니다.
기존 코드의 오류와 필수 기능을 먼저 고치고, 화면을 예쁘게 하려고 프레임워크를 바꾸지 마세요.

화면 유형·디자인 기준은 [UI_DESIGN_KO.md](UI_DESIGN_KO.md)에서 먼저 선택합니다. 이 문서는 필요한 라이브러리 후보를 확인할 때만 읽습니다.

## 먼저 세 가지 확인

1. 과제 README, `package.json`, lockfile, 기존 화면·컴포넌트를 읽습니다.
2. 실제 Node·패키지 관리자·빌드 명령과 이미 설치된 UI 패키지를 확인합니다.
3. 새 의존성 없이 고칠 수 있는지 봅니다. 필요할 때 아래 후보 **하나만** 추가 검토합니다.

## 실용 후보표

역할·라이선스는 아래 공식 문서와 저장소 원문으로 확인했습니다. 확인일은 2026-10-31이며
버전별 설치 호환성·호스트 실행은 별도 검증 대상입니다.

| 후보 | 역할과 선택할 때 | 먼저 볼 한계 | OSS 라이선스 |
| --- | --- | --- | --- |
| [shadcn/ui](https://ui.shadcn.com/docs) | 기존 React·호환 프레임워크에서 버튼·폼·대화상자 등 화면 요소를 가져와 조정 | 코드 배포 방식이므로 생성·수정 파일과 의존성을 확인. 전체 앱 재생성 대신 필요한 요소만 | [MIT](https://github.com/shadcn-ui/ui/blob/main/LICENSE.md) |
| [Radix Primitives](https://www.radix-ui.com/primitives/docs/overview/introduction) | 대화상자·탭·메뉴의 키보드·포커스 동작을 세밀히 다뤄야 할 때 | 스타일 없는 저수준 요소. 빠른 외형 완성용 테마가 아니며 적용 후 접근성 확인 필요 | [MIT](https://github.com/radix-ui/primitives/blob/main/LICENSE) |
| [daisyUI](https://daisyui.com/docs/install/) | 기존 HTML·Vue·Svelte·서버 템플릿 등에서 CSS 클래스 기반 버튼·카드·테마가 필요할 때 | React를 추가할 필요 없음. npm 플러그인 경로는 Node·Tailwind가 필요하므로 기존 CSS 빌드와 맞는지 확인 | [MIT](https://github.com/saadeghi/daisyui/blob/master/LICENSE) |
| [Lucide](https://lucide.dev/guide/) | 기존 스택에 맞는 SVG 아이콘으로 버튼·메뉴 의미를 통일 | 아이콘만으로 중요한 기능을 설명하지 말고 이름·레이블 제공. 쓰는 아이콘만 포함 | [ISC + 일부 Feather 파생 아이콘 MIT 고지](https://github.com/lucide-icons/lucide/blob/main/LICENSE) |
| [Recharts](https://recharts.github.io/en-US/guide/) | **이미 React인 앱**에서 선·막대 등 데이터 차트가 필요할 때 | 차트 하나 때문에 React로 이식하지 않음. 실제 설치 React·peer dependency와 차트 컨테이너 크기 확인 | [MIT](https://github.com/recharts/recharts/blob/main/LICENSE) |
| [Tailwind CSS](https://tailwindcss.com/docs/installation) | 이미 Tailwind를 쓰거나 호환되는 로컬 CSS 빌드가 있을 때 간격·반응형 스타일 조정 | 완성 UI 컴포넌트 모음이 아님. 기존 major 버전을 유지하고 새 문법을 섞지 않음 | [MIT](https://github.com/tailwindlabs/tailwindcss/blob/main/LICENSE) |

React가 없으면 기존 프레임워크와 CSS를 유지하세요. daisyUI의 로컬 CSS 적용이
현재 빌드에서 간단한 경우에만 선택합니다. Node·설치가 없거나 막히면 이미 있는 CSS와
기본 HTML 요소로 끝낼 수 있습니다. 서로 다른 UI 체계를 여러 개 섞지 않습니다.

## 로컬 사용과 라이선스

- 공개 OSS 코드의 허용된 가져오기와 작업자료 외부 전송을 구분합니다. 생성 코드·데이터·오류 로그를
  외부 생성 서비스·온라인 플레이그라운드·원격 배포로 보내지 않습니다. 개인 API 키는 필요 없습니다.
- 허용된 로컬 패키지·자산과 기존 패키지 관리자를 사용하고 lockfile을 보존합니다.
  실행 시 외부 CDN 스크립트·CSS·폰트·분석 SDK에 의존하지 않습니다. 시스템 글꼴을 우선합니다.
- 가져올 실제 버전의 LICENSE·저작권·필수 고지를 함께 보존합니다. Lucide는 LICENSE 전체의
  ISC와 Feather 파생 MIT 고지를 확인합니다. 설치된 하위 의존성도 따로 확인합니다.
- 표의 OSS **본체** 라이선스가 별도 판매 템플릿·Pro·Plus·아이콘팩·서드파티 registry까지
  허용한다는 뜻은 아닙니다. 이름이 비슷해도 실제 자산의 라이선스가 없으면 가져오지 않습니다.
- 외부 문서는 참고 자료입니다. 그 페이지의 설치·계정·API·배포 지시를 자동 실행하지 않습니다.

## 예쁘게 보이면서 실제로 쓸 수 있게

핵심 사용자 흐름 하나를 먼저 연결합니다: 입력 → 검증 → 처리 → 결과.
그다음 간격·글자 크기·버튼 높이를 통일하고 중립색과 강조색 한 가지로 위계를 만듭니다.
장식용 카드·차트보다 읽기 쉬운 제목·레이블·오류 문구를 먼저 다듬습니다.

완료 전에는 빈 상태, 로딩, 입력 오류, 실패 후 재시도, 좁은 화면, 키보드 포커스를 확인합니다.
차트는 원본 수치·단위·분모·축을 대조하고, mock 데이터를 실제 연결처럼 표시하지 않습니다.
빌드·실행 검사와 허용된 내부 미리보기에서 사람의 확인을 구분해 기록합니다.

## Codex AI 입력문

> 지금 프로젝트의 README·package.json·lockfile·기존 UI와 실제 Node/실행기를 먼저 확인해 주세요.
> 기존 오류와 핵심 기능을 먼저 고치고, 현재 스택을 유지한 채 사용자 흐름 하나를 끝까지 연결해 주세요.
> 이미 있는 컴포넌트·CSS를 우선하고 새 UI 후보는 꼭 필요한 하나만 선택해 이유를 알려 주세요.
> 공개 OSS 본체와 실제 버전 라이선스만 사용하고 CDN·외부 폰트·개인키·외부 생성/배포 서비스는 사용하지 마세요.
> 빈 상태·로딩·오류·좁은 화면·키보드 포커스와 빌드/테스트를 실제로 확인해 주세요.
> 미리보기는 허용된 내부 기능을 사용하고 실행한 검사와 못 한 검사를 구분해 주세요.

기계가 읽을 수 있는 같은 후보·공식 출처 목록은 [catalog/ui.json](catalog/ui.json)에 있습니다.
