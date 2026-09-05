# Samples — TRD fixture + expected plan

Fixture used to verify `spec-flow:trd-to-issues` behavior end-to-end without
mutating GitHub.

## Files

- `trd-fixture.md` — small TRD with 3 Tasks across 2 Milestones,
  written to exercise:
  - TRD-named milestones (skill must NOT propose names),
  - dependency lifting (`Depends on T1, T2`),
  - priority labels lifted from the TRD (`⚡ High`),
  - both label heuristics (`pro-friendly` for M0a tasks, `max-only`
    for the multi-AC M0b task).
- `expected-plan.md` — the reference Markdown the skill should emit
  when run as:

  ```
  /spec-flow:trd-to-issues skills/trd-to-issues/references/samples/trd-fixture.md \
      --plan-out /tmp/plan.md
  ```

  Two headers are environment-dependent and must be excluded from any
  diff: `Generated:` (run timestamp) and `Target repo:` (resolved from the
  git remote, so a run here yields `dEitY719/spec-flow-skills` while the
  fixture keeps the `dEitY719/dotfiles` value it was recorded with).

## Manual verification

```bash
diff <(grep -vE '^(Generated|Target repo):' /tmp/plan.md) \
     <(grep -vE '^(Generated|Target repo):' \
       skills/trd-to-issues/references/samples/expected-plan.md)
```

Expect zero diff. Anything else means the decomposition rules,
labeling heuristics, or plan format drifted — update **all three**
(`decomposition-rules.md`, `plan-format.md`, `expected-plan.md`)
before relying on the skill again.
