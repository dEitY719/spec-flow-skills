# spec-flow-skills

Five skills for the **PRD -> TRD -> issue** planning pipeline — turning a
product spec into technical designs, technical designs into GitHub issues, and
finished work back into specs and prompts. Packaged as a single plugin named
`spec-flow`, installable on six coding-agent harnesses.

Every stage produces a reviewable artifact first. Nothing reaches GitHub until
you ask for it explicitly.

## Skills

| Skill | Invoke | What it does |
|-------|--------|--------------|
| `prd-to-trd` | `/spec-flow:prd-to-trd <prd-path> [--apply] [--plan-out <path>] [--force]` | Reads one PRD, proposes 6-8 kebab-case component slugs with each `F-#`/`D-#`/`NF-#` item mapped to an owner, and writes a decomposition plan. With `--apply`, renders 8-section TRD scaffolds into `<prd-dir>/trd/` — headers and guidance only, never an AI-drafted body. |
| `trd-to-issues` | `/spec-flow:trd-to-issues <trd-path>... [--prd <path>] [--apply] [--no-ready]` | Decomposes a filled-in TRD into Epic -> Feature -> Task, checks every Task against the "3 ACs, unit-testable, independently committable" bar, and writes the plan. With `--apply`, creates the GitHub milestones and issues and resolves `#new-N` cross-references to real numbers. |
| `pr-to-ssot-issue` | `/spec-flow:pr-to-ssot-issue <PR#> --reason "<text>" [--parent <N>] [--dry-run]` | Reverse-engineers an exception PR — one already merged, or in flight with no matching PRD/TRD — into an 8-section SSOT tracking issue, so the workflow regains coverage. The source PR is read-only. |
| `reverse-engineering-analysis` | `/spec-flow:reverse-engineering-analysis "<feature or file path>" [output-dir]` | Traces how one existing feature actually works — libraries, data flow, file map — and writes `analysis.md` whose most important section is a self-contained AI implementation prompt you can paste into any assistant to rebuild it elsewhere. |
| `claude-to-codex` | `/spec-flow:claude-to-codex` (names a phase doc plus its references) | Rewrites a Claude-authored phase document into imperative Codex instructions under `docs/ai/phases/codex/`, splitting into numbered slices only when a documented trigger fires. The original is never edited. |

### Picking between them

The discriminator is **which direction along the pipeline you are moving**:

| Forward — spec to work | Backward — work to spec | Sideways — doc to doc |
|---|---|---|
| `prd-to-trd` -> `trd-to-issues`. They chain: a human fills the scaffolds in between. | `pr-to-ssot-issue` (shipped PR -> tracking issue), `reverse-engineering-analysis` (feature -> reusable prompt) | `claude-to-codex` rewrites an existing phase doc for a different executor; it decomposes nothing |

`trd-to-issues` is the only skill that creates GitHub issues in bulk, and it
does so only under `--apply`.

## Safety contract

These skills plan out loud before they act:

- **`--dry-run` is the default** for `prd-to-trd` and `trd-to-issues`. The
  default run writes a plan file and stops; you edit the plan, then re-invoke
  with `--apply`. The plan round-trips — Step 4 reads it back rather than
  re-deriving from the source document.
- **GitHub writes are opt-in and narrow.** `trd-to-issues --apply` creates
  milestones and issues. `pr-to-ssot-issue` creates exactly one issue plus an
  optional backlink comment on the parent. Neither auto-creates labels or
  milestones that do not already exist; both stop instead.
- **Sources are read-only.** `pr-to-ssot-issue` never runs `gh pr edit`,
  `gh pr comment`, or `gh pr review`. `claude-to-codex` never touches the
  original phase document. `prd-to-trd` skips an existing scaffold unless
  `--force`.
- **The target repo comes from the git remote**, never from a guess. A missing
  remote prints `git remote -v` and stops.
- **No push, no merge, no force-push, and no automatic rollback.** A mid-flow
  failure reports the partial state and exits non-zero.
- **No mid-run prompts.** These skills are written for a non-interactive
  harness; the review surface is the plan file.

## Install

### Claude Code

```
/plugin marketplace add dEitY719/spec-flow-skills
/plugin install spec-flow@spec-flow-skills
```

### Codex

```
codex plugin install dEitY719/spec-flow-skills
```

### Kimi CLI

```
kimi plugin install dEitY719/spec-flow-skills
```

### Hermes Agent

```
hermes plugins install dEitY719/spec-flow-skills
```

### OpenCode

See [`.opencode/INSTALL.md`](.opencode/INSTALL.md).

### Gemini CLI / Antigravity

```
gemini extensions install https://github.com/dEitY719/spec-flow-skills
```

Antigravity (`agy`) shares `~/.gemini`, so it inherits the install.

## Harness support

These skills are written in Claude Code's vocabulary, but they are mostly
read-document / write-markdown work plus shell calls, so they port cleanly. The
per-harness tool mappings and capability gaps are documented once, in
[`dEitY719/harness-skills/references/`](https://github.com/dEitY719/harness-skills/tree/main/references)
(#1410 F-5); read the one file for the harness you are on.

| Skill | Claude Code | Codex | Kimi | Gemini / Antigravity | Hermes | OpenCode |
|-------|:-----------:|:-----:|:----:|:--------------------:|:------:|:--------:|
| `prd-to-trd` | full | full | full | full | full | full |
| `trd-to-issues` | full | full | full | full | full | full |
| `pr-to-ssot-issue` | full | full | full | full | full | full |
| `reverse-engineering-analysis` | full | full | full | full | full | full |
| `claude-to-codex` | full | full | full | full | full | full |

Two prerequisites are on you, not the plugin:

- **`gh`** must be installed and authenticated for `trd-to-issues --apply` and
  for `pr-to-ssot-issue`. Every harness reaches GitHub by shelling out to it;
  none has a native substitute. The other three skills need no network at all.
- **A subagent facility** for `pr-to-ssot-issue` Step 3 (gap analysis). Every
  harness above has one under some name; the mapping is in the `harness-skills`
  reference for yours. Where a build genuinely lacks it, run that analysis
  inline — the rest of the skill is unaffected.

## Layout

Manifests live at the repo root and all point at one flat `skills/` directory:

```
.
├── skills/{prd-to-trd,trd-to-issues,pr-to-ssot-issue,reverse-engineering-analysis,claude-to-codex}/
│   ├── SKILL.md
│   └── references/
├── .claude-plugin/{marketplace,plugin}.json      Claude Code
├── .codex-plugin/plugin.json                     Codex
├── .kimi-plugin/plugin.json                      Kimi CLI
├── .hermes-plugin/{plugin.yaml,__init__.py}      Hermes Agent
├── .opencode/plugins/spec-flow.js + INSTALL.md   OpenCode
├── .agents/plugins/marketplace.json              Antigravity
├── gemini-extension.json + GEMINI.md             Gemini CLI
├── package.json
├── CLAUDE.md · AGENTS.md -> CLAUDE.md
└── LICENSE
```

Only Claude Code understands a nested `plugins/<name>/skills/` layout. The other
five harnesses resolve manifests at the repo root and a skills tree at
`./skills/`, so this repo keeps everything flat. See [`CLAUDE.md`](CLAUDE.md) for
the full rationale and contribution rules.

The `.kimi-plugin/` manifest is pre-provisioned: Kimi CLI is not installed on the
maintainer's machines yet, and shipping the manifest now costs nothing and saves
a migration later.

## CI

[`.github/workflows/validate.yml`](.github/workflows/validate.yml) calls the
reusable workflow owned by
[`dEitY719/harness-skills`](https://github.com/dEitY719/harness-skills/blob/main/.github/workflows/skill-check.yml)
(#1410 D-10) — manifest parsing, required files, skill frontmatter,
progressive-disclosure line limits, the Codex description budget, version
agreement, shellcheck, and an emoji gate.

There are no checks defined in this repo. To change what is validated here, open
a PR against `harness-skills`; a merge to its `main` ships to all fifteen repos
at once.

The emoji gate is passed two exact file paths that carry emoji as subject
matter — the ai-metrics footer template and the GitHub priority label names. See
[`CLAUDE.md`](CLAUDE.md) -> "Emojis".

## Provenance

These skills were extracted from
[`dEitY719/dotfiles`](https://github.com/dEitY719/dotfiles)
(`claude/skills/devx-{prd-to-trd,trd-to-issues,pr-to-ssot-issue,reverse-engineering-analysis,claude-to-codex}`)
as a content snapshot — no history rewriting. The source commit SHA is recorded
in this repo's first commit message. The `devx-` prefix is dropped here because
the plugin namespace (`spec-flow:`) now supplies it; the dotfiles originals stay
put and keep working under their old namespace until #1410 Phase 4 removes
them.

This is part of Phase 2 of the dotfiles #1410 migration (tracked as #1657);
`packaging-skills` was Phase 0 and `harness-skills` and `notes-skills` are
its Phase 0/1 siblings.

## License

MIT. See [LICENSE](LICENSE).
