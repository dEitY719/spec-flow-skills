# spec-flow:claude-to-codex — AGENTS.md handling

Step 4 runs `lib/sync-agents-md.sh <repo-root>`, where repo root is the
nearest root of the target project being worked on (not this skills repo).
It prints exactly one line, which Step 5 quotes verbatim:

| `AGENTS.md` state | Action | Output |
|-------------------|--------|--------|
| missing | create it holding exactly `@CLAUDE.md` | `AGENTS.md: created` |
| symlink to `CLAUDE.md` | write nothing (writing would pollute `CLAUDE.md`) | `AGENTS.md: unchanged` |
| already contains `@CLAUDE.md` | write nothing | `AGENTS.md: unchanged` |
| exists without `@CLAUDE.md` | insert `@CLAUDE.md` at the top — after the closing `---` when the file opens with YAML frontmatter; existing content preserved | `AGENTS.md: updated` |

A non-zero exit (usage error: missing or non-directory root) is a
`[FAIL]` for the run. Do not add Codex policy text to `AGENTS.md` unless
the user explicitly requests it. Self-check: `tests/claude-to-codex-agents-md.sh`.
