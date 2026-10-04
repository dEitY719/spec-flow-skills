# Setup mode: `--setup`

Installs the ui-order block into the project's `CLAUDE.md` once, so every later
vague UI request runs this skill's procedure without the slash command, and Step 4
uses the project defaults instead of `checklist.md`.

## Run

Resolve the helper via `$CLAUDE_PLUGIN_ROOT` (the plugin root, the directory
holding `skills/`). Claude Code sets it for a plugin install only; a symlinked personal skill
(`<config dir>/skills/ui-order` -> clone) gets none. Then export it from the skill's
"Base directory" (the harness prints it; never `$PWD`):
`export CLAUDE_PLUGIN_ROOT=$(readlink -f "<Base directory>/../..")`.
Elsewhere export the `SKILL.md` path minus its `skills/ui-order/SKILL.md` suffix.
Still unset -> stop with
`[FAIL] spec-flow:ui-order: CLAUDE_PLUGIN_ROOT unset`; never guess a path.

```bash
[ -n "${CLAUDE_PLUGIN_ROOT:-}" ] || { echo "[FAIL] spec-flow:ui-order: CLAUDE_PLUGIN_ROOT unset"; exit 1; }
python3 "$CLAUDE_PLUGIN_ROOT/skills/ui-order/lib/setup_claude_md.py" [--apply] [--force] [--project <dir>]
```

Pass through exactly the flags the user gave. Never add `--apply` or `--force` on
the user's behalf. Print the helper's output verbatim, then stop.

| Flag | Effect |
|------|--------|
| (none) | Dry-run: print target path, whether a block exists, and the exact block. Writes nothing. |
| `--apply` | Write the block. |
| `--force` | With `--apply`, replace the content between existing markers. |
| `--project <dir>` | Project dir. Default: git toplevel of the CWD, else the CWD. |

## What it writes

- Target `<dir>/CLAUDE.md`. A symlink (commonly to `AGENTS.md`) is written through
  to its resolved file; the link stays. A missing file is created holding only the
  block.
- The block sits between `<!-- ui-order:begin -->` and `<!-- ui-order:end -->`,
  appended at the end of the file after one blank line. Bytes outside the markers
  are never touched. A marker counts only as a whole line; quoting one inline in
  prose is not a block.
- Markers already present -> skip (exit 0) unless `--force`. Malformed markers
  (begin without end, duplicates, reversed) -> `[FAIL]`, exit 1, nothing written.

The helper is the single source of the block text: `## UI 요청 규칙` plus
`## 화면 주문서 (프로젝트 기본값)` with all nine brackets, a 스택 line, and the
wireframe-first line.

## Stack detection

From `package.json` (dependencies + devDependencies) and marker files:
Tailwind (`tailwindcss` or `tailwind.config.*`), shadcn/ui (`components.json`),
MUI, Ant Design, Fluent UI, framework (Next.js / Nuxt / SvelteKit / React / Vue /
Svelte), Lucide (`lucide-react`, `lucide-vue-next`, `lucide-svelte`, `lucide`). Detected values are written plain; the rest are
`checklist.md` defaults marked `(기본값)`. `[화면]` cannot be detected, so it is a
placeholder the user must edit.

## Output

Last line, machine-readable:

```
[OK] spec-flow:ui-order setup target=<path> stack=<list|none> action=<action>
```

`action`: `would-create`, `would-append`, `would-replace` (dry-run); `created`,
`appended`, `replaced` (`--apply`); `skip`. Exit codes: 0 ok (skip included),
1 malformed markers or I/O error, 2 usage error. After a dry-run, tell the user to
re-run with `--apply`; after an apply, tell them to edit the `[화면]` placeholder.
