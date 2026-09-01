# trd-to-issues 사용 결과

> **한 줄 요약** — TRD 1건(.md)을 받아 Milestone/Task 분해 계획(.md)을 생성합니다.
> GitHub 등록은 `--apply` 일 때만 일어나며, 이번 실행은 기본값 dry-run 입니다.

```
TRD (.md)  ──▶  /spec-flow:trd-to-issues  ──▶  plan (.md)   [GitHub 미접촉]
```

## 1. 실행한 명령

```
/spec-flow:trd-to-issues <trd-path>... [--prd <path>] [--apply] [--no-ready]
```

이번 예시 — `--apply` 를 주지 않았으므로 계획만 쓰고 멈춘다.

```
/spec-flow:trd-to-issues skills/trd-to-issues/references/samples/trd-fixture.md \
    --plan-out docs/examples/trd-to-issues/plan.md
```

## 2. 입력

`skills/trd-to-issues/references/samples/trd-fixture.md` — 스킬이 자체 동봉한 76줄
TRD 픽스처. 눈으로 diff 하도록 마일스톤 2개와 Task 3개만 서술한 `example-cli` 예제다.
repo 는 `git remote get-url origin` 으로 `dEitY719/spec-flow-skills` 로 확정됐다.

## 3. 결과

```
Plan written: docs/examples/trd-to-issues/plan.md (2 milestones, 3 tasks)
[OK] spec-flow:trd-to-issues plan=docs/examples/trd-to-issues/plan.md milestones=2 tasks=3
```

[`plan.md`](../examples/trd-to-issues/plan.md) — 45줄, 1,421바이트.

| Milestone | Task | 의존 |
|---|---|---|
| M0a — Scaffold & Tooling | `#new-1 chore(scaffold): bun + Next-style bootstrap` | (none) |
| M0a — Scaffold & Tooling | `#new-2 chore(ci): tox lint pipeline` | `#new-1` |
| M0b — Commands | `#new-3 feat(cli): example-cli init / build with --dry-run` | `#new-1, #new-2` |

`## Decomposition failures` 는 `_no failures._` — Task 3건 모두 기준을 통과했다.

동봉된 기대 출력 `expected-plan.md` 와 `diff` 한 결과 **차이는 두 줄뿐**이며 둘 다
환경 의존 헤더다: `Generated:`(실행 시각), `Target repo:`(픽스처는 스킬이 dotfiles 에
있던 시절의 `dEitY719/dotfiles`). 본문은 바이트 단위로 동일하다.

GitHub 쓰기는 없었다. Step 4 에 진입하지 않았고 `gh` 명령은 한 건도 실행되지 않았다.
