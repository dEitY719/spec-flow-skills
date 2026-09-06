---
name: prd-to-trd
description: >-
  PRD 1건을 컴포넌트별 TRD 스캐폴드로 분해한다. Use for /spec-flow:prd-to-trd,
  "PRD를 TRD로 분해해줘", "PRD 한 개를 컴포넌트별 TRD 로 쪼개줘",
  "scaffold TRDs from this product spec". TRD 를 Epic/Feature/Task 이슈로
  등록하는 것은 spec-flow:trd-to-issues.
license: MIT
allowed-tools: Bash, Read, Edit, Write, Grep
metadata:
  model_recommendation:
    tier: sonnet
    reason: "PRD → multi-TRD decomposition; 8-section standard mapping; structured reasoning"
    claude: prefer
    non_claude: advisory-only
---

# spec-flow:prd-to-trd — PRD → per-component TRD scaffolds

## Help

If arg #1 is `-h`/`--help`/`help`, read `references/help.md`, output it
verbatim, then stop. **No API calls, no file mutation.**

## Step 1: Parse Args + Validate PRD

Required positional: exactly one `<prd-path>`. Flags (`--dry-run`
default, `--apply`, `--plan-out <path>`, `--force`): full table in
`references/help.md`.

The `<prd-path>` must exist as a regular file — on a miss, print
`[FAIL] spec-flow:prd-to-trd: PRD not found: <path>` and stop with exit 1.
v1 supports a single PRD only; more than one positional argument stops with
`[FAIL] multi-PRD input not supported in v1` (batching is OQ-4 for a follow-up).

## Step 2: Read PRD + Propose Decomposition

Load the PRD via `Read`. Apply the heuristic in
`references/decomposition-rules.md` to extract component slugs (6–8,
kebab-case), responsibility mapping of each PRD `F-#` / `D-#` / `NF-#`
item, and adjacent-TRD pairs that share a contract.

PRDs with fewer than 2 viable groups → `[WARN] PRD too small —
single mega-TRD refused. Add more F-#/D-# or split.` and stop.

Locate the TRD template: search `<prd-dir>/trd/_template.md` first; on
miss, fall back to `references/template-fallback.md`, which also states
the agent-toolbox **8-section standard** both must follow. Both sources
missing → `[FAIL] template unavailable` + exit 1.

## Step 3: Write Plan

Write the decomposition to `--plan-out` using `references/plan-format.md`
as the canonical skeleton — the single review surface; the user edits
slugs and mappings, then re-invokes with `--apply`. In `--dry-run`
(default), **stop here** and print:

```
Plan written: <plan-out> (<n> components)
Run with --apply to write TRD scaffolds.
```

## Step 4: Apply (only if `--apply`)

Resolve the bundled helper via `$CLAUDE_PLUGIN_ROOT` — the **plugin
root** (the directory holding `skills/`), not this file's own directory.
Claude Code sets it; elsewhere export the `SKILL.md` path minus its
`skills/prd-to-trd/SKILL.md` suffix. Unset → stop; never guess a path.

```bash
LIB="$CLAUDE_PLUGIN_ROOT/skills/prd-to-trd/lib/plan.py"
python3 "$LIB" parse "<plan-out>" > "<plan-out>.rows.json"
python3 "$LIB" render --rows "<plan-out>.rows.json" --template "<template>" \
    --out-dir "<prd-dir>/trd" --prd "<prd-path>" [--force]
```

`parse` enforces `references/plan-format.md`'s round-trip invariants and
exits 1 naming the offending line; a missing plan is `[FAIL] plan not
found at <path> — run --dry-run first`. `render` substitutes the
`{{...}}` placeholders of `references/template-fallback.md`, skips an
existing scaffold unless `--force`, creates `<prd-dir>/trd/` and nothing
above it, and prints `written=<n> skipped=<n>`. Edit a row's `"title"`
between the two commands when the slug-derived default is wrong
(`ci-gate` -> `CI Gate`). A mid-flow write failure reports the slugs
written so far, then `[FAIL]` + exit 1 — **no auto-rollback.**

## Step 5: Report

```
[OK] spec-flow:prd-to-trd plan=<path> components=<n> [scaffolds=<n> skipped=<n>]
```

`scaffolds=` and `skipped=` appear only on `--apply`. For dry-run, append
`Next: review <plan-out>, then re-run with --apply`. Operational
constraints: see `references/constraints.md`.

## Related Skills

`spec-flow:trd-to-issues` — next pipeline stage (human fills the scaffolds,
then TRD → Milestones + Issues); this skill owns the PRD → TRD slot.
