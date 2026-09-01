# spec-flow — skill index

Five skills for the PRD -> TRD -> issue planning pipeline. Each lives in this
extension's `skills/` directory. They are task-triggered: load the one that
matches the job by reading its `SKILL.md`, then follow it. Do not load all five.

| Skill | Read | Use when |
|-------|------|----------|
| `prd-to-trd` | `@./skills/prd-to-trd/SKILL.md` | Splitting one PRD into per-component TRD scaffolds before anyone writes a design. |
| `trd-to-issues` | `@./skills/trd-to-issues/SKILL.md` | Turning a filled-in TRD into Epic/Feature/Task and, with `--apply`, GitHub milestones and issues. |
| `pr-to-ssot-issue` | `@./skills/pr-to-ssot-issue/SKILL.md` | Recovering SSOT coverage for a PR that shipped without a PRD/TRD, by filing a tracking issue after the fact. |
| `reverse-engineering-analysis` | `@./skills/reverse-engineering-analysis/SKILL.md` | Analyzing an existing feature into a copy-pasteable AI implementation prompt for a new project. |
| `claude-to-codex` | `@./skills/claude-to-codex/SKILL.md` | Rewriting a Claude-authored phase document into an imperative doc Codex can execute from alone. |

Each skill's `references/` directory holds the detail it loads on demand;
`SKILL.md` says which file to read and when. Do not read `references/` files up
front.

## Picking between them

The discriminator is **which direction along the pipeline you are moving**:

- Forward, spec to work: `prd-to-trd` (PRD -> TRD scaffolds) then
  `trd-to-issues` (TRD -> milestones and issues). They chain; the human fills
  the scaffolds in between.
- Backward, work to spec: `pr-to-ssot-issue` (a shipped exception PR -> a
  tracking issue) and `reverse-engineering-analysis` (an existing feature -> a
  reusable implementation prompt).
- Sideways, doc to doc: `claude-to-codex` rewrites an existing phase document
  for a different executor. It does not decompose anything.

`trd-to-issues` is the only one that can create GitHub issues in bulk, and only
under `--apply`. If the user has not said `--apply`, the answer is a plan file.

## Tool mapping for Gemini CLI

The skills speak in actions. On Gemini CLI these resolve to:

- "Read a file" -> `read_file` / `read_many_files`
- "Create a file" / "edit a file" -> `write_file`, `replace`
- "Run a shell command" (including every `gh` call) -> `run_shell_command`
- "Search file contents" -> `grep_search`
- "Find files by name" -> `glob`
- "Create a todo" -> `write_todos`
- "Dispatch a subagent" -> `invoke_agent` with `agent_name: "generalist"`
  (only `pr-to-ssot-issue` needs one, for its Step 3 gap analysis)

The full mapping, including every capability gap and its workaround, is owned by
the sibling repo `dEitY719/harness-skills` at `references/gemini-tools.md`
(dotfiles #1410 F-5) — read it there; this repo keeps no copy. On Antigravity
read that repo's `references/antigravity-tools.md` instead: `agy` shares
`~/.gemini` but not Gemini CLI's tool names.

## Capability gaps on Gemini CLI

- `trd-to-issues` and `pr-to-ssot-issue` need the GitHub CLI (`gh`) installed
  and authenticated, driven through `run_shell_command`. There is no native
  GitHub tool to substitute. Both resolve the target repo from the git remote —
  if the named remote is missing they stop and list `git remote -v`; do not
  guess an `owner/repo`.
- These skills never prompt mid-run: they are written for a non-interactive
  harness, and the review surface is the dry-run plan file. Gemini CLI's
  `ask_user` is not part of any flow here — do not insert one.
- `reverse-engineering-analysis` reads broadly across the repo before writing.
  On a large codebase, scan imports and exports first (`grep_search` / `glob`)
  rather than reading whole files.

## Safety rules

- **`--apply` is the only door to GitHub.** `trd-to-issues` defaults to
  `--dry-run`, which writes a plan and stops. Never add `--apply` for the user.
- **The source is read-only.** `pr-to-ssot-issue` never runs `gh pr edit`,
  `gh pr comment`, or `gh pr review`; `claude-to-codex` never edits the original
  phase document. Both produce new artifacts alongside the source.
- **Never overwrite silently.** `prd-to-trd` skips an existing TRD scaffold
  unless `--force`.
- **Never auto-create labels or milestones**, and never roll back a partial run
  silently — report what was written and stop.
- **Never fabricate provenance.** No remote, no repo. An empty gap analysis is a
  refusal, not a prompt to invent one.
