# trd-to-issues

## 한 줄 요약

채워진 TRD 를 **Epic → Feature → Task** 3단으로 분해해 계획 파일을 만들고,
`--apply` 일 때만 그 계획대로 **GitHub Milestone 과 Issue 를 대량 등록**한다.

## 무엇을 만드는가

| 모드 | 산출물 |
|------|--------|
| `--dry-run` (기본) | 분해 계획 1개 — `--plan-out` 경로의 Markdown. GitHub 미접촉 |
| `--apply` | 대상 repo 의 Milestone 여러 개 + Task 마다 Issue 1건 |

3단 구조의 의미는 이렇다. **Epic** 은 TRD 규모의 결과물, **Feature** 는 마일스톤
크기의 조각, **Task** 는 실제로 등록되는 이슈 한 건이다. Task 는 "AC 3개 이하,
단위 테스트 가능, 독립적으로 커밋 가능" 기준을 통과해야 하고, 통과하지 못하면 더
쪼개지거나 계획의 "decomposition failures" 항목으로 보고된다.

의존 관계는 `#new-1`, `#new-2` 같은 가상 인용으로 계획에 적히고, `--apply` 시점에
실제 이슈 번호로 치환된다.

## 언제 쓰고 언제 안 쓰는가

**쓴다** — TRD 본문이 채워졌고 이제 그걸 실행 가능한 이슈 묶음으로 옮길 때.
TRD 여러 개를 한 번에 넘기면 합집합으로 처리한다.

**안 쓴다:**

- 아직 TRD 가 없고 PRD 만 있을 때 → `prd-to-trd` 로 스캐폴드부터 만든다.
- 이슈 **한 건**만 필요할 때 → 대량 분해는 과하다. `gh:issue-create` 를 쓴다.
- 이슈를 실제로 구현하고 싶을 때 → `gh:issue-implement` / `gh:issue-flow`.

## 호출 형식

```
/spec-flow:trd-to-issues <trd-path>... [--prd <path>] [--remote <name>]
                         [--apply] [--plan-out <path>] [--no-ready]
```

| 인자 / 플래그 | 기본값 | 설명 |
|---|---|---|
| `<trd-path>` | 필수 | TRD Markdown 경로. **여러 개** 가능하며 합집합 처리 |
| `--prd <path>` | 없음 | 참조용 PRD. 여러 개 지정 가능 |
| `--remote <name>` | `origin` | Milestone/Issue 를 받을 remote |
| `--dry-run` | **on** | 기본값. 계획만 쓰고 GitHub 을 **절대** 건드리지 않는다 |
| `--apply` | off | 실제 등록. 라벨 사전 검증 → 마일스톤 → 이슈 → `#new-N` 치환 → Ready 승격 |
| `--plan-out <path>` | `.claude/.trd-to-issues.plan.md` | 계획 파일 경로 |
| `--no-ready` | off | `--apply` 때 첫 마일스톤 이슈의 Ready 승격을 건너뛴다 |
| `-h` / `--help` / `help` | — | 도움말만 출력. API 호출 없음 |

## 동작 단계

1. **인자 파싱 + repo 확정** — git remote 로 `TARGET_REPO=<owner>/<repo>` 를 해석한다.
   remote 가 없으면 `git remote -v` 목록을 보여주고 중단한다. **조용한 폴백은 없다.**
   모든 TRD/PRD 경로의 실재도 확인한다.
2. **분해** — Epic/Feature/Task 추출, 마일스톤 그룹핑, 의존성(`Depends on #...`) 추출,
   `pro-friendly` / `max-only` 라벨 휴리스틱 적용.
3. **계획 작성** — `--plan-out` 에 기록. dry-run 이면 여기서 멈춘다.
4. **적용** — `--apply` 일 때만. 라벨 사전 검증 → `gh api` 로 마일스톤 → Task 마다
   `gh issue create` → 가상 인용 치환 → Ready 승격.
5. **보고** — 계획 경로, 마일스톤 수, Task 수, (apply 시) 첫 마일스톤 URL.

## 주의사항 / 제약

- **`--apply` 없이는 GitHub 에 아무것도 쓰지 않는다.** 이 스킬에서 가장 중요한 계약이다.
- **라벨을 자동 생성하지 않는다.** `gh label list` 로 미리 검증하고, 없는 라벨이 있으면
  목록을 보여주며 멈춘다. 라벨은 사람이 만들어야 한다.
- **마일스톤 이름을 물어보려고 중간에 멈추지 않는다.** Claude Code 는 비대화형이라
  프롬프트가 뜨면 세션이 멈춘다. 대신 제안 이름을 계획 파일에 적어 두고 사람이 거기서
  고치게 한다.
- **`--remote <name>` 이 없으면 `origin` 으로 몰래 되돌아가지 않는다.**
- **중간 실패 시 롤백하지 않는다.** 이슈 몇 건이 만들어진 상태로 멈추고 부분 상태를
  보고한다. 뒷정리는 사람 몫이다.
- **TRD/PRD 본문을 대신 써주지 않는다.** 입력 전용이다.
- Ready 승격을 쓰려면 대상 repo 에 `Status` 필드가 `Ready` 옵션을 가진 Project 보드가
  붙어 있어야 한다. 없으면 `--no-ready` 를 쓴다.

## 이어지는 스킬

`prd-to-trd` — 이전 단계(PRD → TRD 스캐폴드). `gh:issue-flow` — 등록된 Task 이슈를
받아 구현부터 PR 까지 진행한다.
