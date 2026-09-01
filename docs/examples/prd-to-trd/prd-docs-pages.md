# PRD: spec-flow-skills 문서 사이트 (skill guides + worked examples)

> **Status**: Draft v1 (2026-09-01)
> **Owner**: @dEitY719
> **Repo**: dEitY719/spec-flow-skills

## 1. Background

`spec-flow-skills` 는 `spec-flow` 플러그인 하나에 5개 스킬을 담은 단일 플러그인
마켓플레이스 repo 다. 스킬 자체는 `skills/<name>/SKILL.md` 와 각 `references/`
에 문서화되어 있지만, **repo 외부에서 읽을 수 있는 문서 표면이 없다**.

`packaging:structure-check` 감사 결과 이 공백이 정량적으로 확인되었다:

- `M5` FAIL — `docs/skill-guides/`, `docs/skill-output/` 두 디렉터리 모두 부재
- `R1` WARN — 스킬별 guide 페이지 없음 (5개 전부)
- `R2` WARN — 스킬별 usage 페이지 없음 (5개 전부)
- `R3` WARN — README 가 `docs/` 하위 문서로 링크하지 않음
- `R5` WARN — README 에 스킬별 guide+usage 링크 없음

설치 후보자는 현재 README 표 한 줄과 `SKILL.md` 원문 사이에서 스킬을 판단해야
한다. 스킬이 실제로 무엇을 만들어 내는지 — 산출물의 생김새 — 를 보여주는
자료가 전무하다.

## 2. Goals / Non-Goals

### Goals

- 스킬 5개 각각에 대해 "무엇을 하는 스킬인가"(guide)와 "실제로 돌리면 무엇이
  나오는가"(worked example) 두 문서를 제공한다.
- 두 문서를 GitHub Pages 로 발행해 repo 를 클론하지 않고도 읽을 수 있게 한다.
- README 를 그 문서들의 단일 진입점으로 만든다.
- `packaging:structure-check` 의 M5/R1/R2/R3/R5 를 PASS 로 만든다.

### Non-Goals

- 스킬 동작 자체의 변경. 이 PRD 는 문서 레이어만 다룬다.
- 다국어(영문) 병행 문서화. 1차는 한국어 + 기존 영문 README 유지.
- 문서 사이트 프레임워크(MkDocs, Docusaurus) 도입. 정적 HTML 파일로 충분하다.
- 스킬별 API 레퍼런스 자동 생성. `references/` 원문이 이미 그 역할을 한다.

## 3. Decisions

- **D-1** — 문서 레이아웃은 `docs/skill-guides/<skill>.{md,html}` 와
  `docs/skill-output/<skill>-usage.{md,html}` 두 축을 쓴다. 이는
  `packaging:structure-check` 가 R1/R2/R5 에서 기대하는 경로 규약이며, 임의로
  바꾸면 감사에서 WARN 이 남는다.
- **D-2** — Pages 절대 URL 의 owner 부분은 **소문자로 정규화**한다
  (`dEitY719` → `deity719`). GitHub Pages 호스트명은 대문자를 허용하지 않아
  원문 owner 를 그대로 쓰면 전 링크가 404 가 된다.
- **D-3** — HTML 은 `/devx:visualize` 로 md 하나당 한 번씩 생성한다. 수작업
  HTML 편집과 일괄 변환 스크립트는 모두 금지한다.
- **D-4** — worked example 의 입력과 산출물은 `docs/examples/<skill>/` 아래에
  repo 에 보존한다. gitignore 하지 않는다. 문서가 링크하는 결과물이 실재해야
  검증(F-10)이 성립하기 때문이다.
- **D-5** — 산문(md, README)에는 이모지를 쓰지 않는다. repo 의 기존 규칙이며
  예외는 `metrics-footer.md` 와 `decomposition-rules.md` 두 파일뿐이다.
- **D-6** — 문서 생성 절차는 스킬 이름을 하드코딩하지 않는다. 항상
  `skills/*/` 스캔과 `SKILL.md` frontmatter 읽기로 목록을 얻는다.

## 4. Functional Requirements

- **F-1** — `skills/*/` 를 스캔해 스킬 목록을 얻고, 각 `SKILL.md` frontmatter
  에서 `name:` 과 `description:` 을 읽는다. 하드코딩된 목록을 두지 않는다.
- **F-2** — 스킬마다 `docs/skill-guides/<skill>.md` 를 작성한다. 한 줄 요약,
  사용/비사용 경계(형제 스킬과의 구분), 호출 형식과 옵션, 동작 단계, 제약을
  포함한다.
- **F-3** — 스킬마다 `docs/skill-output/<skill>-usage.md` 를 작성한다. 실행한
  명령 / 입력 / 결과 4단 구조를 지키며, 내용은 실제 1회 실행 기록이어야 한다.
- **F-4** — worked example 의 입력 문서와 산출물을 `docs/examples/<skill>/`
  아래에 보존해 재현 가능하게 한다.
- **F-5** — 작성한 md 를 각각 같은 디렉터리의 HTML 로 렌더링한다.
- **F-6** — 렌더링된 HTML 은 라이트/다크 테마와 모바일 폭에서 모두 읽을 수
  있어야 하며 외부 네트워크 의존 없이 단일 파일로 동작한다.
- **F-7** — README `## Skills` 섹션 아래에 스킬당 정확히 한 줄로 guide 와
  usage 를 함께 링크하는 블록을 둔다.
- **F-8** — 그 링크는 상대경로가 아니라 Pages 절대 URL 을 쓰며, owner 는
  D-2 의 소문자 규칙을 따른다.
- **F-9** — `docs/` 를 GitHub Pages 발행 소스로 설정해 푸시 시 자동 배포한다.
- **F-10** — README 가 링크한 모든 경로가 실제 파일로 존재하는지 검증한다.
- **F-11** — `발견한 스킬 수 x 2 == README 링크 수` 를 검증한다.
- **F-12** — F-10, F-11 검증을 CI(`validate.yml`)에 게이트로 연결해 문서 누락
  상태로 머지되지 않게 한다.
- **F-13** — 스킬이 추가/삭제되었는데 문서가 따라오지 않은 드리프트를 감지해
  CI 에서 실패시킨다.
- **F-14** — `docs/index.html` 랜딩 페이지를 두어 Pages 루트에서 스킬별 문서로
  이동할 수 있게 한다.

## 5. Non-Functional Requirements

- **NF-1** — 문서는 `SKILL.md` 본문을 복제하지 않는다. 스킬 동작의 SSOT 는
  `SKILL.md` 이고 guide 는 그것을 요약/보완한다. 한 번의 스킬 수정이 여러
  파일 편집으로 번지면 안 된다.
- **NF-2** — 문서 빌드는 네트워크 없이 로컬에서 완결되어야 한다.
- **NF-3** — 작업 완료 후 `packaging:structure-check` 가 M5 PASS 및
  R1/R2/R3/R5 PASS 여야 한다.
- **NF-4** — HTML 한 파일은 자체 완결(self-contained)이며 과도하게 무겁지
  않아야 한다.
- **NF-5** — 검증(F-10, F-11)은 사람 눈이 아니라 명령으로 재현 가능해야 한다.
- **NF-6** — 문서 파이프라인은 repo-agnostic 해야 한다. 스킬이 6번째로 추가돼도
  절차 수정 없이 동작한다.

## 6. Open Questions

- **OQ-1** — Pages 발행 소스를 `docs/` 디렉터리로 할지 `gh-pages` 브랜치로 할지.
- **OQ-2** — 문서 HTML 을 repo 에 커밋할지, CI 에서 생성할지. D-3 은 생성
  방법만 정하고 보관 위치는 열어 둔다.
