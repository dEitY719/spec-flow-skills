# Phase 03 — 문서 링크 무결성 CI 게이트 (Codex 01)

## Goal

`skills/*/` 를 스캔해 스킬 목록을 동적으로 얻고, 각 스킬의 guide/usage 문서
4종(md/html)이 실재하는지와 README 의 Pages 링크가 실제 파일 및 스킬 수와
일치하는지 검사하는 셸 스크립트를 만든다. 그 스크립트를 기존
`.github/workflows/validate.yml` 에서 실행되게 연결한다. 사람이 눈으로 잡던
문서 드리프트(직전 감사의 R1/R2/R5 WARN)를 CI 가 잡게 만드는 것이 목적이다.

## Inputs / References

- `docs/examples/claude-to-codex/phase-03-docs-ci-gate.md` (원본 phase 문서, 읽기 전용)
- `CLAUDE.md` (레포 규약: 이모지 금지, 레이아웃, 공유 CI 는 harness-skills 소유)
- `.github/workflows/validate.yml` (현재 워크플로 — 아래 Assumptions 확인 필수)
- 대상 PRD 항목: F-10, F-11, F-12, F-13 / 제약: NF-5, NF-6
- 선행 phase: Phase 01(문서 작성), Phase 02(HTML 렌더링) 완료 가정

## Scope

- `scripts/check-docs-links.sh` 신규 작성.
- 스킬 목록을 `skills/*/` 디렉터리 스캔으로 동적 획득 (NF-6, repo-agnostic).
- 스킬당 4개 파일 존재 검사: guide md, guide html, usage md, usage html.
- README 의 Pages URL 추출 → 각 URL 의 경로 부분이 실제 파일과 대응되는지 검사.
- README Pages 링크 개수가 스킬 수의 정확히 2배인지 검사 (F-11).
- Pages URL 의 owner 세그먼트가 소문자인지 검사.
- `[OK]` / `[FAIL]` 출력 관례, exit 0 / 1.
- `.github/workflows/validate.yml` 에서 이 스크립트를 실행하도록 연결.

## Out of scope

- HTML 내부 링크(문서 → 문서 링크)를 따라가는 검사. 이번 phase 범위 밖.
- Pages 배포 성공 여부를 원격에서 확인하는 것. 네트워크 의존이 생기고 NF-2 와 충돌한다.
- `docs/examples/` 아래 파일 검증. 그곳은 worked example 산출물 보관소이며 스킬 목록과 1:1 대응이 아니다.
- 별도 워크플로 파일 신규 생성.
- 세분화된 exit code 체계.
- repo 루트 밖에서도 실행 가능하게 만드는 경로 자동 탐색.
- `harness-skills` 의 공유 `skill-check.yml` 수정.

## Files to create or modify

- `scripts/check-docs-links.sh` — NEW
- `.github/workflows/validate.yml` — MODIFY

## Implementation instructions

1. `scripts/check-docs-links.sh` 를 새로 만들고 `#!/usr/bin/env bash` 와
   `set -euo pipefail` 로 시작하라. 스크립트는 repo 루트에서 실행되는 것을
   전제한다. 실행 위치를 자동 보정하지 마라.
2. 스킬 목록을 `skills/*/` 디렉터리 이름 스캔으로 채워라. 스킬 이름을
   스크립트 안에 하드코딩하지 마라 (NF-6).
3. 스킬 목록이 비어 있으면 `[FAIL]` 을 출력하고 exit 1 하라. 빈 목록을
   통과로 처리하지 마라.
4. 각 스킬에 대해 다음 4개 경로의 존재를 검사하라:
   `docs/skill-guides/<skill>.md`, `docs/skill-guides/<skill>.html`,
   `docs/skill-output/<skill>.md`, `docs/skill-output/<skill>.html`.
   하나라도 없으면 없는 경로를 한 줄로 출력하고 실패로 기록하라.
5. `README.md` 에서 Pages URL 을 추출하라. 추출한 각 URL 의 경로 부분을
   레포 상대 경로로 환산해 해당 파일이 실제로 존재하는지 검사하고, 없으면
   URL 과 기대 경로를 한 줄로 출력하고 실패로 기록하라.
6. 추출한 Pages 링크 개수가 스킬 수의 정확히 2배인지 검사하라 (F-11).
   불일치 시 기대값과 실제값을 모두 포함한 한 줄을 출력하고 실패로 기록하라.
7. 각 Pages URL 의 owner 세그먼트에 대문자가 섞여 있는지 검사하라. 대문자가
   있으면 실패로 기록하고, 해당 URL 을 출력하라. 로컬에는 파일이 있어도
   Pages 에서 404 가 나는 케이스이므로 경고가 아니라 실패로 다뤄라.
8. 출력 형식은 기존 스킬들의 관례를 따라 성공 시 `[OK]`, 실패 시 `[FAIL]` 로
   시작하는 줄을 쓰라. 실패 줄에는 무엇이 왜 실패했는지가 한 줄 안에 들어가야
   한다. CI 로그에서 그 한 줄만 보고 원인을 알 수 있어야 한다.
9. 검사를 첫 실패에서 중단하지 말고 전부 수행한 뒤, 실패가 하나라도 있으면
   exit 1, 없으면 exit 0 하라. 그 외 exit code 는 쓰지 마라.
10. `chmod +x scripts/check-docs-links.sh` 로 실행 권한을 부여하라.
11. `.github/workflows/validate.yml` 을 열어 실제 구조를 먼저 확인하라. 현재
    이 파일의 유일한 job 은 `uses:` 로 `dEitY719/harness-skills` 의 재사용
    워크플로를 호출하며 `steps:` 를 갖지 않는다. 재사용 워크플로 호출 job 에는
    스텝을 추가할 수 없으므로, 같은 파일 안에 `ubuntu-latest` 에서 도는 별도
    job 을 추가하고 그 job 의 스텝에서 `actions/checkout` 후
    `bash scripts/check-docs-links.sh` 를 실행하라. 새 워크플로 파일을 만들지
    마라. 기존 `validate` job 의 `uses:`/`with:` 블록과 주석은 건드리지 마라.
12. `bash scripts/check-docs-links.sh` 를 현재 repo 상태에서 실행해 통과하는지
    확인하라.
13. 고의 실패 검증을 하라: guide html 하나를 임시로 다른 이름으로 옮겨
    스크립트가 실패(exit 1)하는지 확인하고 원복하라. 이어서 README 의 Pages
    링크 한 줄을 임시로 지워 개수 검사가 걸리는지 확인하고 원복하라. 검증 후
    `git status --short` 로 원복이 완료됐음을 확인하라.
14. `.github/workflows/validate.yml` 이 문법적으로 유효한 YAML 인지 확인하라
    (예: `python3 -c "import yaml,sys; yaml.safe_load(open('.github/workflows/validate.yml'))"`).
    푸시하거나 CI 를 원격에서 돌리지 마라.

## Constraints

- 원본 phase 문서 `docs/examples/claude-to-codex/phase-03-docs-ci-gate.md` 를 수정하지 마라.
- "Files to create or modify" 에 적힌 두 파일 외에는 수정하지 마라. 검증 중
  임시로 옮기거나 지운 파일은 반드시 원복하라.
- 스킬 이름을 하드코딩하지 마라. 목록은 항상 `skills/*/` 스캔에서 나와야 한다.
- 별도 워크플로 파일을 새로 만들지 마라. `.github/workflows/validate.yml` 안에서 해결하라.
- `harness-skills` 소유의 공유 `skill-check.yml` 검사 로직을 이 레포에 다시 인라인하지 마라.
- `docs/examples/` 를 검증 대상에 넣지 마라.
- 이모지를 스크립트, 워크플로, 출력 문자열 어디에도 쓰지 마라 (CLAUDE.md -> Emojis).
- 0/1 외의 exit code 를 도입하지 마라.
- HTML 내부 링크 추적이나 원격 Pages 확인을 구현하지 마라.
- git commit, git push, gh 명령을 실행하지 마라.
- 위 두 파일이 갱신되고 13-14 단계 검증이 끝나면 멈춰라.

## Assumptions / Notes

- 문서 경로 규약을 `docs/skill-guides/<skill>.{md,html}` 과
  `docs/skill-output/<skill>.{md,html}` 로 가정했다. 원본 phase 문서는
  디렉터리 두 개(`docs/skill-guides/`, `docs/skill-output/`)와 "스킬당 guide
  md/html, usage md/html 네 개"만 명시하고 파일명 규칙은 명시하지 않았다.
  Phase 01/02 산출물의 실제 파일명이 다르면 그 규칙을 따르고, 변경한 가정을
  최종 요약에 적어라.
- 현재 이 레포에서 `docs/skill-guides/` 와 `docs/skill-output/` 는 비어 있고
  `scripts/` 디렉터리는 존재하지 않는다. Phase 01/02 산출물이 아직 없는
  상태이므로 12단계 실행이 실패할 수 있다. 그 경우 스크립트 로직을 완화해
  통과시키지 말고, 실패 출력이 "어느 파일이 없어서 실패했는지"를 정확히
  가리키는지만 확인한 뒤 그 사실을 최종 요약에 보고하라.
- README 의 Pages URL 형식(owner/repo 세그먼트 구성)은 실제 `README.md`
  내용을 읽고 확인하라. URL 패턴을 추측해서 정규식을 고정하지 말고, 실제
  README 에 있는 형식에 맞춰라.
- `validate.yml` 의 job 구조는 위 11단계에 적힌 대로 원본 phase 문서의 서술
  ("스텝을 하나 더 붙인다")과 어긋난다. 원본의 의도(새 워크플로 파일을 만들지
  않는다)는 유지하되, 구현은 같은 파일 내 별도 job 으로 하라.
- `set -euo pipefail` 하에서 grep 이 매치 0건일 때 비정상 종료하지 않도록
  파이프라인을 방어적으로 작성하라 (예: `|| true` 와 명시적 개수 검사).

## Completion checklist

- [ ] `scripts/check-docs-links.sh` 가 생성되었고 실행 권한이 있다.
- [ ] 스크립트가 `set -euo pipefail` 로 시작한다.
- [ ] 스킬 목록이 `skills/*/` 스캔에서 나오고, 스킬 이름 하드코딩이 없다.
- [ ] 스킬당 guide md/html, usage md/html 4개 존재 검사가 구현되었다.
- [ ] README Pages URL 의 경로 대 실제 파일 대응 검사가 구현되었다.
- [ ] README Pages 링크 개수 == 스킬 수 x 2 검사가 구현되었다 (F-11).
- [ ] Pages URL owner 세그먼트 소문자 검사가 구현되었다.
- [ ] 출력이 `[OK]` / `[FAIL]` 관례를 따르고, 실패 사유가 한 줄로 식별된다.
- [ ] exit code 가 성공 0, 실패 1 뿐이다.
- [ ] `docs/examples/` 가 검증 대상에서 제외되어 있다.
- [ ] `.github/workflows/validate.yml` 이 이 스크립트를 실행하고, 새 워크플로 파일은 생기지 않았다.
- [ ] 기존 `validate` job 의 `uses:`/`with:` 블록이 그대로다.
- [ ] 현재 repo 상태에서 스크립트를 실행해 결과를 확인했다.
- [ ] 고의 실패 2건(guide html 이동, README 링크 삭제)을 확인하고 원복했으며 `git status --short` 로 검증했다.
- [ ] `validate.yml` 이 유효한 YAML 임을 확인했다.
- [ ] 원본 phase 문서가 수정되지 않았다.

## Codex prompt

```text
Implement this Codex task exactly as specified in this document.
Before making changes:
- Read AGENTS.md
- Read CLAUDE.md
- Read the referenced input documents listed above
Execution rules:
- Only modify the files listed in "Files to create or modify"
- Follow the implementation instructions in order
- Do not expand scope
- If an interface is uncertain, implement the safest minimal version and leave a clear note
- When finished, summarize changed files, key decisions, and unresolved risks
```
