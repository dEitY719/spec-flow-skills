# TRD to Issues: Step 4 Bulk Create Procedure

Detailed substeps for the issue creation phase.

1. **Pre-validate labels** —
   `gh label list --repo "$TARGET_REPO" --json name --jq '.[].name'`.
   Any label referenced by the plan that is missing → stop with the
   missing list. **Never POST `/labels`** — it silently creates the label
   and pollutes the repo's label namespace.
2. **Bulk-create milestones** —
   `gh api repos/$TARGET_REPO/milestones -X POST -f title=... -f description=...`.
   Title collision → stop and report (no silent skip/merge).
3. **Create issues** — `gh issue create --repo "$TARGET_REPO" --title ...
   --body-file <tmp> --milestone <title> --label <name>...` per task.
4. **Resolve `#new-N` citations** — substitute virtual numbers with the
   real numbers returned by step 3, then `gh issue edit <real-N>
   --body-file <patched>`.
5. **Promote first milestone to Ready** (skip if `--no-ready`) —
   `claude-set-issue-status <real-N> "Ready"` per first-milestone issue.
   Guard it: `command -v claude-set-issue-status >/dev/null` first. The
   helper ships with `dEitY719/dotfiles`, not with this repo, so when it is
   absent emit one `[WARN] claude-set-issue-status not installed — Ready
   promotion skipped` and finish normally. Repeat that `[WARN]` in the Step 5
   report so a default `--apply` run never reads as "first milestone promoted"
   when nothing was promoted. Never abort here: milestones and issues already
   exist by this point and there is no rollback.

Mid-flow failure: report partial state (created milestones / issues so
far), emit `[FAIL] spec-flow:trd-to-issues <reason>`, and stop — no automatic
rollback.
