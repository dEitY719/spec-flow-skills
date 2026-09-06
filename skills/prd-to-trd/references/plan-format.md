# Plan Format

This file owns one artifact: the **dry-run plan** the skill writes to
`--plan-out`. The TRD scaffold rendered from it on `--apply` is owned by
`references/template-fallback.md` — one copy, not two.

The plan must round-trip: a plan written by this skill is re-parsed by
`lib/plan.py parse` on `--apply` (Step 4), which enforces every invariant
below and exits 1 naming the offending line rather than writing wrong
frontmatter into every scaffold.

## Plan skeleton (dry-run output)

```markdown
# PRD-to-TRD Plan
Generated: <ISO 8601 local time>
Source PRD: <prd-path>
PRD directory: <dirname(prd-path)>
Mode: dry-run
Template: <_template.md path | references/template-fallback.md>

## Components

| Slug | 책임 F-# | 책임 D-# | NF-# (primary) | NF-# (cited) | 인접 TRD |
|------|----------|----------|----------------|--------------|----------|
| <slug-1> | F-1,F-2 | D-3 | NF-1 | NF-2 | <slug-2> |
| <slug-2> | F-3 | D-3 | NF-3 | NF-1 | <slug-1> |
| <slug-3> | F-4 | (none) | (none) | NF-1 | (none) |

## Suggested splits
<empty list, OR>
- <slug-X> — carries N items (>= 8), consider sub-splitting.

## Manual review
<empty list, OR>
- <slug-Y>-a / <slug-Y>-b — naming collision auto-resolved; review.
```

## Plan field rules

- **Slug column** — kebab-case, unique per plan.
- **책임 F-# / D-#** — comma-separated, no spaces around commas.
  Empty cells are rendered as `(none)` — never blank — so the
  round-trip parser can distinguish "no items" from "missing column".
- **NF-# (primary)** — at most one NF item owned by this TRD (0 or 1).
  When the PRD has fewer `NF-#` items than TRDs, or none apply to this
  component, the cell is rendered as `(none)`.
- **NF-# (cited)** — comma-separated, may be empty (rendered `(none)`).
- **인접 TRD** — comma-separated slugs that share a contract. May be
  empty (rendered `(none)`). References must point at slugs in the
  same plan, and must be **bidirectional** — a shared contract binds
  both sides, so `parse` rejects a one-sided entry
  (`decomposition-rules.md` rule 4).
- **Suggested splits** — rendered as `_no suggestions._` when empty.
- **Manual review** — rendered as `_none._` when empty.

## Round-trip invariant

- One row per slug in the **Components** table. Adding rows during
  `--apply` is forbidden; the user must edit the plan and re-run.
- Heading levels and ordering are stable: `## Components`,
  `## Suggested splits`, `## Manual review` in that order.
- Frontmatter block before `## Components` is line-stable
  (`Generated:` / `Source PRD:` / `PRD directory:` / `Mode:` /
  `Template:` in order).

## Where the scaffold lives

`references/template-fallback.md` carries the verbatim 8-section scaffold
and its frontmatter slot rules. `lib/plan.py render` reads that file (or
the project's own `<prd-dir>/trd/_template.md`) and substitutes its
`{{...}}` placeholders from the Components table above — so the plan
columns and the template placeholders are the single contract between the
two files.
