# Installing spec-flow for OpenCode

## Prerequisites

- [OpenCode.ai](https://opencode.ai) installed
- The GitHub CLI (`gh`), installed and authenticated — `trd-to-issues` and
  `pr-to-ssot-issue` shell out to it. The other three skills do not need it.

## Installation

Add the plugin to the `plugin` array in your `opencode.json` (global or
project-level):

```json
{
  "plugin": ["spec-flow-skills@git+https://github.com/dEitY719/spec-flow-skills.git"]
}
```

Restart OpenCode. The plugin installs through OpenCode's plugin manager and
registers all five skills.

OpenCode uses its own plugin install. If you also use Claude Code, Codex, or
another harness, install this plugin separately for each one.

## Usage

Use OpenCode's native `skill` tool:

```
use skill tool to list skills
use skill tool to load prd-to-trd
```

## Tool mapping

The authoritative OpenCode tool mapping for every `dEitY719/*-skills` repo is
owned by the sibling repo
[`dEitY719/harness-skills`](https://github.com/dEitY719/harness-skills/blob/main/references/opencode-tools.md)
(dotfiles #1410 F-5). Read it there when a skill names a tool you do not
recognise; this repo keeps no copy on purpose. Short version:

- "Read a file" -> `read`
- "Create a file" / "edit a file" -> `apply_patch`
- "Run a shell command", including every `gh` call -> `bash`
- "Search file contents" / "find files by name" -> `grep`, `glob`
- "Create a todo" -> `todowrite`
- "Dispatch a subagent" -> OpenCode's agent facility; only
  `pr-to-ssot-issue` needs one, for its Step 3 gap analysis. If none is
  available, do that analysis inline rather than skipping it.
- "Invoke a skill" -> OpenCode's native `skill` tool
- "Ask the user" -> not used. These skills are non-interactive by design; the
  review surface is the dry-run plan file, not a prompt.

## Safety notes

- `trd-to-issues` writes to GitHub only with `--apply`. The default is a
  dry-run that writes a plan file and stops.
- `pr-to-ssot-issue` treats the source PR as read-only and creates exactly one
  issue, plus an optional backlink comment on the parent.
- Both resolve `owner/repo` from the git remote and stop if it is missing —
  they never guess.

## Troubleshooting

### Plugin not loading

1. Check logs: `opencode run --print-logs "hello" 2>&1 | grep -i spec-flow`
2. Verify the plugin line in your `opencode.json`
3. Make sure you are running a recent version of OpenCode

### Skills not found

1. Use the `skill` tool to list what was discovered
2. Check that the plugin is loading (see above)

### `gh` errors on --apply

1. `gh auth status` — the run stops on an unauthenticated CLI by design
2. `git remote -v` — the target repo comes from the remote, not from a guess

## Getting Help

Report issues: https://github.com/dEitY719/spec-flow-skills/issues
