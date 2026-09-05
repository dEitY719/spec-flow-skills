# Metrics Footer — `<!-- ai-metrics:spec-flow-pr-to-ssot-issue -->`

Appended after Section 8 ("관계 / Cross-refs") of the rendered issue
body. Matches the canonical block format used by `gh-issue:create` /
`gh-pr:create` so `gh-setup:add-ai-metrics` can backfill / re-compute it later.

## When to skip

If the env var `GH_DISABLE_AI_METRICS=1` is set, the entire footer
block is omitted from the body. The parent-backlink comment is also
suppressed in that case (parity with `gh-flow:issue` Step 2.6 — see
dEitY719/dotfiles#399 for the rationale). Do not emit a partial footer.

## Block format

Append after a `---` horizontal rule at the end of the body:

    ---
    <details>
    <summary>🤖 AI Metrics · 📊 ~X tokens · 👤 ~M h · 🤖 ~L min</summary>

    <!-- ai-metrics:spec-flow-pr-to-ssot-issue -->
    📊 ~X tokens · 👤 ~M h · 🤖 ~L min
    <!-- /ai-metrics:spec-flow-pr-to-ssot-issue -->

    </details>

The named comment marker (`spec-flow-pr-to-ssot-issue`) lets future
backfill / re-compute tools target this skill's block without colliding
with the `gh-flow:issue` aggregate block (`<!-- ai-metrics:gh-flow-issue -->`)
when the new issue later flows through `/gh-flow:issue`.

## Field semantics

| Field | Source | Notes |
|-------|--------|-------|
| `X` (tokens) | `(len(PR body) + len(rendered issue body draft) + len(subagent gap report)) ÷ 4`, rounded to nearest 500. Minimum 1 000. | Caps an outlier at 50 000. |
| `M` (human time) | Look up the **issue type** in `dEitY719/gh-issue-skills`'s `skills/create/references/metrics-baseline.md` table. For SSOT recovery, the type is `docs` (1 h) when only Section E (Cross-refs) is non-empty; otherwise `feat (small)` (4 h). | The skill writes `docs(ssot):` titles but the recovery effort is closer to a small `feat` for table-lookup purposes when multiple SSOT sections are affected. |
| `L` (AI minutes) | Computed at Step 6 as `(NOW - START_TS) / 60`, rounded to the nearest minute. Minimum 1. | Wall-clock from skill entry, not just the `gh issue create` call. |

## Token estimation — priority order

First available source wins, matching the convention used by
`gh-issue:create`:

1. Explicit `--tokens <N>` override (not currently a CLI flag, but
   reserved for future use).
2. Character-sum estimate from the table above.
3. Fallback: 3 000 (conservative — the SSOT body without a subagent
   report still pulls in the PR diff + 8-section template).

## Backlink comment (parent issue)

When `--parent <issue#>` is set and `GH_DISABLE_AI_METRICS != 1`, the
skill posts the following on the parent issue (no metrics footer):

```
> 역공학 SSOT 이슈가 등록됐습니다 — #<new issue number>.
> 원본 PR: #<PR#>. Exception 사유는 새 이슈 6. Audit 섹션 참조.
```

The backlink itself does not carry an `<!-- ai-metrics:* -->` block —
it's a single-line comment whose AI cost is already accounted for
inside the new issue's footer.

## Re-compute via `/gh-setup:add-ai-metrics --force`

The `<!-- ai-metrics:spec-flow-pr-to-ssot-issue -->` marker is the
recompute key. Running `/gh-setup:add-ai-metrics --force` on the new issue
will replace the block in place using fresh measurements (per the
`gh-setup:add-ai-metrics` skill's `--force` contract), without touching any
other content in the issue body.

## Pairs with

- `references/issue-body-template.md` — the footer attaches after
  Section 8.
- `dEitY719/gh-issue-skills` `skills/create/references/metrics-baseline.md`
  — human-time lookup table is SSOT'd there; do not duplicate it here.
- `SKILL.md` Step 4 (render) + Step 5 (post).
