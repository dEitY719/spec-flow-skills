# TRD to Issues: Step 4 Bulk Create Procedure

Detailed substeps for the issue creation phase.

Resolve the bundled helper via `$CLAUDE_PLUGIN_ROOT` — the **plugin root**
(the directory holding `skills/`), not this file's own directory. Claude Code
sets it; elsewhere export the `SKILL.md` path minus its
`skills/trd-to-issues/SKILL.md` suffix. Unset → stop; never guess a path.

```bash
LIB="$CLAUDE_PLUGIN_ROOT/skills/trd-to-issues/lib/apply_plan.py"
python3 "$LIB" parse "<plan-out>" > "<plan-out>.rows.json"
```

`parse` is also the gate on a hand-edited plan: a violated round-trip
invariant — an out-of-order `#new-N`, a `Depends on:` citation no task
declares, a missing bullet, a fourth AC, a line that is not in the
`plan-format.md` skeleton — exits 1 naming the offending line, before
anything is created. Nothing is skipped silently, so a dangling `#new-N`
surfaces here rather than after step 3 has already filed the issues.

1. **Pre-validate labels** —
   `gh label list --repo "$TARGET_REPO" --json name --jq '.[].name'`.
   Any label referenced by the plan that is missing → stop with the
   missing list. **Never POST `/labels`** — it silently creates the label
   and pollutes the repo's label namespace.
2. **Bulk-create milestones** —
   `gh api repos/$TARGET_REPO/milestones -X POST -f title=... -f description=...`.
   Title collision → stop and report (no silent skip/merge).
3. **Create issues** — `gh issue create --repo "$TARGET_REPO" --title ...
   --body-file <tmp> --milestone <title> --label <name>...` per task, in the
   order `parse` emitted them. `gh issue create` prints the issue **URL**,
   not a number, so extract and validate it per task before recording it:

   ```bash
   url=$(gh issue create --repo "$TARGET_REPO" ...)
   num=${url##*/}
   case "$num" in ''|*[!0-9]*)
       echo "[FAIL] spec-flow:trd-to-issues unparseable issue URL: $url" >&2
       exit 1 ;;
   esac
   ```

   Collect those into a `{"new-1": <real-N>, ...}` map keyed by the `id`
   `parse` emitted for that task.
4. **Resolve `#new-N` citations** — never substitute by hand:

   ```bash
   python3 "$LIB" resolve --rows "<plan-out>.rows.json" --map <map.json> \
       > <patched.json>
   ```

   Each row carries the final `body`; write it out and
   `gh issue edit <real-N> --body-file <patched>`. A `#new-N` with no entry
   in the map exits 1 naming it rather than emitting a wrong number — which
   is the point, since step 3 has already created the issues and there is no
   rollback. A real `#<number>` citation against a pre-existing issue passes
   through untouched.
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
