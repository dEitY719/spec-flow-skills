---
name: claude-to-codex
description: >-
  Claude 로 작성한 phase 구현 문서를, 고칠 파일과 순서와 멈출 지점을 못박은
  scope-bounded work order 로 재구성(필요하면 분할)한다. Use for
  /spec-flow:claude-to-codex, "이 phase 문서를 codex용으로 재구성해줘",
  "codex 에서 작업하기 최적화된 설계문서로 바꿔줘",
  "convert this phase doc into a scope-bounded work order for Codex".
license: MIT
allowed-tools: Bash, Read, Write, Edit, Grep, Glob
metadata:
  model_recommendation:
    tier: sonnet
    reason: "phase-doc → scope-bounded Codex work order; split-boundary judgment; structured reasoning, no direct code execution"
    claude: prefer
    non_claude: advisory-only
---

# Purpose

Turn a Claude-authored phase implementation document into a **scope-bounded
work order** — one document naming exactly which files may change, in what
order, and where to stop. Preserve the original phase document — never edit
it. Generate derived documents under `docs/ai/phases/codex/`.
Treat `CLAUDE.md` as the source of truth and `AGENTS.md` as a thin bridge
for Codex. Never rewrite `CLAUDE.md` itself unless the user explicitly asks.

## Help

If the user asks for help/usage, read `references/help.md` and output its
content verbatim, then stop. No API calls, no file mutation.

## Step 1: Read Inputs

Read every reference document the user listed plus the target phase
document in one batch (they are independent reads). Scan repo structure
(`AGENTS.md`, `CLAUDE.md`) for context the transformed document should
preserve.

## Step 2: Decide Single vs Split

Evaluate whether the phase document is already narrow and deterministic
enough for one Codex pass. Default to a single output document — do not
split by default. Split into multiple numbered documents only when a
trigger condition in `references/output-and-split.md` is met; follow that
file's split-axis guidance and prefer the minimum number of documents
needed.

## Step 3: Write the Output File(s)

Naming and path rules (zero-padded `-codex-NN` suffix, base filename
preservation, `docs/ai/phases/codex/` target dir): see
`references/output-and-split.md`. Contract the scope — goal, exact
`NEW`/`MODIFY` file list, excluded work, ordered steps — per
`references/rewrite-rules.md`. Structure each generated document exactly
per `references/document-template.md`.

## Step 4: Sync AGENTS.md

Apply the three-way branch (missing / has `@CLAUDE.md` / missing
`@CLAUDE.md`) in `references/agents-md-handling.md`. Do not add extra
Codex policy text to `AGENTS.md` unless the user explicitly requests it.

## Quality bar

- Codex can execute from the generated document alone, without the
  original long phase spec open at all times.
- Implementation scope and the file list are unambiguous; mixed
  responsibilities are separated only when it genuinely helps reliability.
- Output stays faithful to the original Claude-authored intent — these are
  practical implementation documents, not summaries.

## Step 5: Report

Print a concise verdict, then keep any remaining chat response short:

```
[OK] spec-flow:claude-to-codex — <n> Codex document(s) written
  docs/ai/phases/codex/<base>-codex-01.md (single|slice 1/<n>)
  ...
  AGENTS.md: created | updated (@CLAUDE.md added) | unchanged
```

Next: hand the printed Codex prompt block(s) to Codex.
