# spec-flow-skills — Contributor Guidelines

This file is the AI context document for this repo. `AGENTS.md` is a symlink to
it, so Claude Code, Codex, Gemini CLI, and every other harness read the same
text. Edit `CLAUDE.md`; never replace the symlink with a second copy.

## What this repo is

A single-plugin skill marketplace. The plugin is named `spec-flow` and it
bundles the five skills of the **PRD -> TRD -> issue planning pipeline** —
turning a product spec into technical designs, technical designs into GitHub
issues, and finished work back into specs and prompts:

| Skill | Role |
|-------|------|
| `prd-to-trd` | Decompose one PRD into per-component TRD scaffolds (8-section standard, headers and guidance only). |
| `trd-to-issues` | Decompose a TRD into Epic/Feature/Task and, only with `--apply`, bulk-create GitHub milestones and issues. |
| `pr-to-ssot-issue` | Reverse-engineer an exception PR that skipped PRD/TRD into an SSOT tracking issue. |
| `reverse-engineering-analysis` | Analyze an existing feature into a reusable, copy-pasteable AI implementation prompt. |
| `claude-to-codex` | Rewrite a Claude-authored phase document into an imperative doc optimized for Codex execution, splitting it when needed. |

The skills were extracted from `dEitY719/dotfiles` (`claude/skills/devx-*`) as a
snapshot — see the first commit for the source SHA. The dotfiles copies remain
in place for now; they are removed in a later phase of that repo's migration
plan (#1410 Phase 4).

## Layout: root manifests, one flat `skills/`

This repo deliberately does **not** use the nested `plugins/<name>/skills/`
"mono" layout. Every harness manifest sits at the repo root and points at a
single flat `./skills/` directory:

```
.claude-plugin/{marketplace,plugin}.json   Claude Code
.codex-plugin/plugin.json                  Codex
.kimi-plugin/plugin.json                   Kimi CLI
.hermes-plugin/{plugin.yaml,__init__.py}   Hermes Agent
.opencode/plugins/spec-flow.js             OpenCode
.agents/plugins/marketplace.json           Antigravity
gemini-extension.json + GEMINI.md          Gemini CLI
skills/<name>/SKILL.md                     the skills themselves
```

Only Claude Code understands the nested mono layout. The other five harnesses
resolve manifests at the repo root and a skills tree at `./skills/`, so nesting
would silently cut this plugin down to Claude-Code-only. **Do not move the
manifests under a `plugins/` directory.**

## Shared assets live in `harness-skills` — link, never copy

Two things this repo depends on are owned by `dEitY719/harness-skills`
(dotfiles #1410 F-5 / D-10):

1. **Per-harness tool mappings** — `references/{codex,kimi,gemini,antigravity,hermes,opencode}-tools.md`.
   This repo carries no `references/` tree of its own; `GEMINI.md`,
   `.opencode/INSTALL.md`, and `.kimi-plugin/plugin.json` link there instead.
   If you are about to paste one in, stop and add a link — one tool rename must
   stay one edit, not fifteen (NF-2).
2. **The CI workflow** — `.github/workflows/skill-check.yml`. This repo's
   `validate.yml` calls it with `plugin-name: spec-flow`. Do not re-inline the
   checks here; to change what is checked, open a PR against `harness-skills`.

## Rules for changing skills

- **Skill directory name is the identity.** `skills/<name>/` must match the
  `name:` field in that skill's `SKILL.md` frontmatter, and that field is the
  **bare** name (`prd-to-trd`), never namespaced (`spec-flow:prd-to-trd`). The
  harness supplies the `spec-flow:` prefix at invocation time.
- **Invocation form in prose is namespaced.** Body text referring to a skill as
  a command writes `/spec-flow:prd-to-trd`.
- **Progressive disclosure.** `SKILL.md` stays under 100 lines (CI enforces it)
  and names which `references/` file to read and when. Detail lives in that
  skill's own `references/`. Do not inline a reference file back into
  `SKILL.md`. These five are already close to the limit — shorten prose rather
  than moving steps out of sight.
- **Description budget.** CI sums every skill description and fails past 5,440
  characters — Codex's context budget. Keep new descriptions tight, and keep the
  Korean trigger phrases: they are what makes a skill fire.
- **Honour each skill's safety contract.** `trd-to-issues` writes to GitHub only
  under `--apply`; its default `--dry-run` writes a reviewable plan file and
  stops. `pr-to-ssot-issue` treats the source PR as read-only and creates
  exactly one issue plus an optional backlink comment. `prd-to-trd` skips
  existing scaffolds unless `--force`. `reverse-engineering-analysis` and
  `claude-to-codex` write local files and never edit the source document.
  Nothing here pushes, merges, or force-pushes. Neither `gh`-touching skill
  auto-creates labels or milestones, and neither rolls back on a mid-flow
  failure — it reports partial state instead. Do not "improve" any of that.
- **Non-interactive by design.** None of these skills stops to ask a question
  mid-run; the review surface is the plan file. A blocking prompt would hang the
  harness. Do not add one.
- **Provenance is non-negotiable.** These skills resolve the target repo from
  the git remote, cite PR numbers and `file:line` anchors, and fail closed on an
  unknown remote or an empty gap. A step that would let a skill guess instead of
  failing is a bug, not a convenience.

## Emojis

Not in prose, manifests, or workflow files — token efficiency, same rule as the
upstream dotfiles repo. **Two exceptions, both exact files:**

- `skills/pr-to-ssot-issue/references/metrics-footer.md` — the ai-metrics footer
  template. Those glyphs *are* the output format the skill emits, and the
  upstream dotfiles `CLAUDE.md` names this the single sanctioned emoji exception
  in the whole project (#317 F-2, PR #320).
- `skills/trd-to-issues/references/decomposition-rules.md` — GitHub priority
  label names quoted verbatim as they appear on the board.

CI's emoji gate is passed those two paths in `allow-emoji-paths` for exactly
that reason. Matching is by prefix, so keep it at file granularity: do not widen
it to a directory, do not add a third path, and do not add emoji anywhere else.

## Version bumps

The version appears in seven manifests: `.claude-plugin/marketplace.json`,
`.claude-plugin/plugin.json`, `.codex-plugin/plugin.json`,
`.kimi-plugin/plugin.json`, `.hermes-plugin/plugin.yaml`,
`gemini-extension.json`, and `package.json`. CI checks that they agree — bump
all of them together. Versioning is independent per repo (#1410 D-9); this repo
does not move in lockstep with its siblings.
