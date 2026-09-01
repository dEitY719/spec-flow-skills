# Delegated CI Validation (`validate.yml`) — Feature Analysis

## Overview

`.github/workflows/validate.yml` is this repository's entire CI surface: a 33-line
caller that runs no checks of its own and instead delegates every check to a
reusable workflow owned by a different repository, passing only the plugin name
and a two-entry emoji exemption list. The user-visible effect is a normal
`validate` check on every push to `main`, every pull request, and every manual
dispatch — but the definition of "valid" lives elsewhere and is shared by fifteen
sibling repositories at once.

## Key Libraries

"Library" here means an external dependency the workflow pulls in at run time.
Only two of them carry a version this repository can state; the rest are provided
by the runner image and are deliberately unpinned.

| Library | Version | Role |
|---------|---------|------|
| GitHub Actions reusable workflows (`on: workflow_call` / `jobs.<id>.uses`) | Platform feature — not versioned | The delegation mechanism itself: lets one repo call another repo's workflow as if it were a job. |
| `dEitY719/harness-skills/.github/workflows/skill-check.yml` | `@main` — a moving ref, not a tag or SHA | Defines all eleven validation steps. Resolved fresh at every run, so a merge to its `main` changes this repo's CI with no commit here. |
| `actions/checkout@v4` | `v4` (major-version tag; the exact patch floats) | Checks out the *caller's* code inside the reusable workflow so the checks see this repository's files. |
| `jq` | Not pinned — preinstalled on the `ubuntu-latest` runner image | Parses every tracked `*.json` to prove the manifests are valid JSON. |
| `python3` | Not pinned — preinstalled on the runner image | Runs seven of the checks as inline heredoc scripts (frontmatter, line limits, description budget, version agreement, name consistency, emoji gate). |
| PyYAML (`import yaml`) | Not pinned — preinstalled on the runner image, never installed by the workflow | Parses every tracked `*.yaml`/`*.yml`. An implicit dependency on the image: nothing in either repo installs it. |
| `shellcheck` | Not pinned — installed at run time via `apt-get install -y -qq` | Lints tracked `*.sh` at `--severity=warning`. In this repository the step short-circuits: `git ls-files '*.sh'` returns zero files. |
| `git` (`git ls-files`) | Not pinned — provided by the runner | Enumerates *tracked* files for the JSON, shellcheck, and emoji checks, so untracked scratch files are invisible to CI. |

## How It Works

**1. Trigger and delegation.** `validate.yml` declares three triggers (`push` to
`main`, any `pull_request`, and `workflow_dispatch`) and `permissions: contents:
read`. Its single job, `validate`, has no `runs-on` and no `steps`. Instead it is
a `uses:` job pointing at
`dEitY719/harness-skills/.github/workflows/skill-check.yml@main`, with a `with:`
block carrying two inputs. GitHub resolves that reference at dispatch time,
fetches the called workflow from the other repository at whatever `main` currently
points to, and runs it as this workflow's job.

**2. What crosses the boundary.** The called workflow declares four
`workflow_call` inputs: `plugin-name` (required), `max-skill-lines` (default
`100`), `description-budget` (default `5440`), and `allow-emoji-paths` (default
empty string). This caller passes exactly two — `plugin-name: spec-flow` and a
newline-delimited `allow-emoji-paths` list of two file paths — and inherits the
two numeric defaults. That is the whole contract: everything else the checks need
is *derived* from the checked-out repository rather than configured. No secrets
are passed, and no `permissions` beyond read.

**3. How `plugin-name` becomes a check.** The callee copies its inputs into job
`env` (`PLUGIN_NAME`, `MAX_SKILL_LINES`, `DESCRIPTION_BUDGET`,
`ALLOW_EMOJI_PATHS`) and each step reads them from the environment rather than
interpolating `${{ }}` inside shell bodies. `plugin-name` does double duty: it is
asserted equal to the `name` field in four JSON manifests, in
`.claude-plugin/marketplace.json` `plugins[0]`, in
`.agents/plugins/marketplace.json` `plugins[0]`, and in `.hermes-plugin/plugin.yaml`;
and it is also spliced into a required-file path,
`.opencode/plugins/${PLUGIN_NAME}.js`. So one string keeps a filename and six
manifest fields in agreement.

**4. The eleven checks, in order.** JSON manifests parse (`jq empty` over `git
ls-files '*.json'`); YAML manifests parse (PyYAML over a recursive glob, skipping
`.git/`); sixteen required harness manifests exist; `AGENTS.md` is a symlink whose
`readlink` target is exactly `CLAUDE.md`; no `plugins/` directory exists and
`skills/` does; each `skills/<dir>/SKILL.md` has YAML frontmatter whose `name` is
bare (a `:` fails it) and equals its directory name, plus a `description:` key;
every `SKILL.md` is at most `MAX_SKILL_LINES` lines; each description is non-empty
and at most 1024 characters, and their sum is at most `DESCRIPTION_BUDGET`;
version agrees across six manifests (five `version` fields plus
`marketplace.json` `plugins[0].version`); the plugin name is consistent
everywhere; shellcheck passes; and no tracked text file contains an emoji.

**5. The emoji gate and why the exemption list exists.** The emoji check
deliberately classifies only pictographic code points as emoji — `ord(ch) >=
0x1F000` or the variation selector `U+FE0F` — so arrows, check marks, and box
drawing used throughout the skills do not trip it. `ALLOW_EMOJI_PATHS` is split on
commas and newlines into a tuple and matched with `str.startswith`, which is why
it is a **prefix** match and why the caller's comment insists on exact file paths:
passing a directory would exempt everything beneath it. Scanning this repository
with the same rule finds emoji on exactly two tracked lines —
`skills/pr-to-ssot-issue/references/metrics-footer.md:20` and
`skills/trd-to-issues/references/decomposition-rules.md:42` — the two paths the
caller exempts. The list is therefore load-bearing, not defensive: remove it and
CI fails.

**6. Non-obvious design choices.** (a) The `@main` pin is a moving reference: it
buys "one edit ships to fifteen repos" and pays for it with the ability of an
upstream merge to turn this repository's CI red without a commit here. Both
repositories' header comments name that trade-off (anti-drift, "NF-2") and forbid
re-inlining the checks. (b) Nearly every check is an inline `python3` or `bash`
heredoc rather than a marketplace action, so the only third-party action in the
chain is `actions/checkout`. (c) The checks read `git ls-files` rather than the
filesystem, so they judge tracked content only. (d) The caller contributes more
comment than code — 12 of its 33 lines are prose explaining where the checks live
and why the two emoji paths are sanctioned.

**7. Current state of this repository against those checks.** Verified locally by
running the same logic: all sixteen required files exist; `AGENTS.md` resolves to
`CLAUDE.md`; the five `SKILL.md` files are 81, 91, 96, 97, and 99 lines (all under
100, the largest with one line of headroom); descriptions total 1054 of 5440
characters (19.4 percent); all seven version strings are `0.1.0`; zero `*.sh`
files are tracked, so shellcheck short-circuits; and the only emoji-bearing files
are the two exempted ones.

## File Map

Key files involved in this feature:

- `.github/workflows/validate.yml` — the whole feature in this repository: 33
  lines, one `uses:` job, two inputs, and a comment block explaining the
  delegation.
- `dEitY719/harness-skills/.github/workflows/skill-check.yml` — **not in this
  repository.** The reusable workflow that defines all eleven checks and the four
  `workflow_call` inputs. Read for this analysis from a local clone of that
  repository whose `HEAD` is `51440500d101eea75df63439440f825b1173a962`, verified
  by `git ls-remote` to be the current tip of its `main`. Because the caller pins
  the moving `@main` ref rather than that SHA, a later merge upstream can change
  what runs without any change here, and this analysis would then be stale.
- `CLAUDE.md` (and `AGENTS.md`, a symlink to it) — the documented rationale:
  shared CI lives in `harness-skills`, must not be re-inlined, and the emoji
  allowlist stays at file granularity with exactly two entries.
- `README.md` lines 150-165 — the user-facing statement that this repository
  defines no checks of its own and that changes go via a PR against the owner
  repository.
- `skills/pr-to-ssot-issue/references/metrics-footer.md`,
  `skills/trd-to-issues/references/decomposition-rules.md` — the two exempted
  paths; the only tracked files here that contain emoji.
- Inputs the checks read but that are not part of the workflow: the seven
  version-bearing manifests, the six harness manifests keyed on the plugin name,
  and every `skills/*/SKILL.md`.

## AI Implementation Prompt

> Copy and paste this prompt into your AI coding assistant to implement this feature in a new project.

---

[START OF PROMPT]

I want to set up shared, delegated CI validation across a family of related
GitHub repositories, using GitHub Actions reusable workflows. Read this
repository's `git remote -v` to learn its owner and name, and use that owner for
every cross-repository reference you write; do not ask me for it.

**Goal:** Define the validation rules exactly once, in a single owner repository,
and have every sibling repository call them with a thin caller workflow that
contains no checks of its own. Adding a rule in the owner repository must apply
to every sibling on their next run, with no commit in any sibling.

**Required libraries and tools:**

- GitHub Actions reusable workflows — no install; a workflow with `on:
  workflow_call:` can be invoked as `jobs.<id>.uses: <owner>/<repo>/.github/workflows/<file>.yml@<ref>`.
- `actions/checkout@v4` — no install; pin the major tag. The reusable workflow
  must check out the *calling* repository, which `actions/checkout` does by
  default when it runs inside a called workflow.
- `jq`, `python3`, PyYAML, and `git` — already present on the `ubuntu-latest`
  runner image; do not add install steps for them. Note in a comment that PyYAML
  is an implicit dependency on the image.
- `shellcheck` — not on the image; install it inside the step that needs it with
  `sudo apt-get update -qq && sudo apt-get install -y -qq shellcheck`, and only
  after confirming there is at least one file to lint.

**Expected behavior:**

- Each sibling repository holds one workflow file, roughly 30 lines, that
  triggers on `push` to the default branch, on `pull_request`, and on
  `workflow_dispatch`; declares `permissions: contents: read`; and whose single
  job is a `uses:` job with a short `with:` block. It must contain no `runs-on`,
  no `steps`, and no check logic.
- The owner repository holds one reusable workflow declaring typed
  `workflow_call` inputs: one required identifier string, and optional tunables
  with sensible defaults so that a typical caller passes only the required one.
- Provide an opt-in exemption input (default: empty string, meaning the strictest
  behavior) so a repository with a legitimate exception can declare it in its own
  caller instead of forcing the shared rule to be weakened for everyone.
- A failing check prints one `FAIL <path>: <reason>` line per offending file and
  exits non-zero; a passing check prints one `ok <path>` line per file so the log
  is a readable inventory. Collect all failures within a step before exiting
  rather than aborting on the first one.
- Every check must judge *tracked* files only, enumerated with `git ls-files`, so
  untracked local scratch files never affect CI.

**Implementation approach:**

- Put the shared workflow in the owner repository at
  `.github/workflows/<name>.yml` with `on: workflow_call:` and an `inputs:` map;
  give every input a `description` and a `type`, and a `default` for every
  optional one.
- Copy the inputs into the job's `env:` block once (`env: FOO: ${{ inputs.foo }}`)
  and have each step read them from the environment. Do not interpolate `${{ }}`
  directly inside shell script bodies — that is a script-injection hazard and it
  breaks quoting.
- Write each check as an inline `bash` or `python3 - <<'PY' ... PY` heredoc rather
  than pulling in third-party actions, so the only external action in the chain is
  `actions/checkout`. Quote the heredoc delimiter so the shell does not expand the
  script.
- Start every `bash` step with `set -euo pipefail`, accumulate a `fail` variable,
  and `exit "$fail"` at the end. In Python steps, accumulate `fail = 0` and end
  with `sys.exit(fail)`.
- Reuse the required identifier input in two ways: assert it equals the
  corresponding field in each config file, and splice it into any path that is
  named after it. One input then keeps a filename and several config fields in
  agreement.
- For an exemption input, accept a newline- or comma-separated string, split it
  with `re.split(r"[,\n]", value)`, drop empties, and match with
  `str.startswith`. Document in a comment that this is prefix matching, so callers
  must pass exact file paths unless they intend to exempt a whole subtree.
- When a check scans text for a character class, define the class narrowly and say
  why in a comment. For an emoji ban, treat only `ord(ch) >= 0x1F000` and the
  variation selector `U+FE0F` as emoji, so that arrows, check marks, and
  box-drawing characters do not trigger false failures. Wrap file reads in
  `try/except (UnicodeDecodeError, OSError)` and skip symlinks and non-files.
- Skip work when there is nothing to do: if the file list for a step is empty,
  print an `ok ... nothing to check` line and exit 0 before installing any tool.
- In the caller, spend comment lines generously. State where the checks live, that
  a copy would be a drift risk, and exactly which file to edit to change what is
  validated. Do the same in the owner's header, including a copy-pasteable example
  `uses:` block.

**Ref-pinning decision — make it explicitly:**

- `@main` gives you "one edit ships everywhere" and is the right default for a
  family of repositories under one owner, but it is a moving reference: an
  upstream merge can turn a sibling's CI red with no commit in that sibling.
- `@v1` (a tag you move deliberately) or `@<full-sha>` gives reproducibility at
  the cost of a bump in every sibling.
- Pick one, write the reason in a comment above the `uses:` line, and be
  consistent across the family.

**Data structure / API:**

The contract between the two repositories is the input map. Shape it like this:

```yaml
# owner repository: .github/workflows/shared-check.yml
on:
  workflow_call:
    inputs:
      target-name:        # required identifier, e.g. the component name
        description: "Must match the `name` field in every manifest."
        required: true
        type: string
      max-lines:
        description: "Per-file line ceiling."
        required: false
        type: number
        default: 100
      allow-paths:
        description: "Newline- or comma-separated path prefixes exempt from the strict rule. Empty means no exemptions."
        required: false
        type: string
        default: ""
```

```yaml
# each sibling repository: .github/workflows/validate.yml
name: validate
on:
  push:
    branches: [main]
  pull_request:
  workflow_dispatch:
permissions:
  contents: read
jobs:
  validate:
    uses: <owner>/<owner-repo>/.github/workflows/shared-check.yml@main
    with:
      target-name: <this repository's component name>
      allow-paths: |
        path/to/legitimate/exception.md
```

Please implement this step by step: first the reusable workflow in the owner
repository with its `workflow_call` inputs and one trivial check, then the thin
caller in this repository, then add the remaining checks one step at a time,
verifying each with `workflow_dispatch` before adding the next.

[END OF PROMPT]

---

## Notes

- **The called workflow is not in this repository.** Its contents were read from a
  local clone of the owner repository at commit
  `51440500d101eea75df63439440f825b1173a962`, confirmed by `git ls-remote origin
  main` to be the current tip of that repository's `main` — the exact ref the
  caller pins. Had that clone not been available, the internals of the eleven
  checks would have been unknowable from this repository alone, and only the
  caller's two inputs could have been described.
- **`@main` means this analysis has a shelf life.** Nothing in this repository
  records which upstream commit its CI ran against. A merge upstream changes the
  behavior described in "How It Works" without any commit here.
- **Unpinned tool versions are a deliberate gap, not an omission in this
  document.** `jq`, `python3`, PyYAML, `shellcheck`, and `git` have no version
  constraint anywhere in either workflow; they are whatever the `ubuntu-latest`
  image ships on the day of the run. `actions/checkout@v4` pins only a major
  version. PyYAML is the sharpest edge: it is imported but never installed, so a
  runner image that dropped it would break the YAML check with no local signal.
- **The shellcheck step is untested here.** This repository tracks zero `*.sh`
  files, so that step always takes its early-exit branch; its apt-get and
  `shellcheck` invocation have never run against this repository.
- **Headroom is thin in two places.** The largest `SKILL.md` is 99 lines against a
  100-line ceiling, so a two-line addition fails CI. The description budget, by
  contrast, is at 1054 of 5440 characters (19.4 percent) and is not a near-term
  constraint.
- **The emoji allowlist is required, not precautionary.** Scanning this
  repository with the workflow's own rule finds emoji on exactly the two exempted
  lines. Widening the list to a directory would silently exempt every file beneath
  it, because the match is `startswith`.
