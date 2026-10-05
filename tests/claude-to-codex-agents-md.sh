#!/usr/bin/env bash
# tests/claude-to-codex-agents-md.sh — self-check for
# skills/claude-to-codex/lib/sync-agents-md.sh.
#
# Five cases, each with its exact one-line token: missing -> created, has the
# import -> unchanged, lacks it -> updated (prepended), YAML frontmatter ->
# updated (after the closing ---), symlink to CLAUDE.md -> unchanged with the
# target's bytes untouched.
#
#   bash tests/claude-to-codex-agents-md.sh

set -euo pipefail

ROOT=$(cd "$(dirname "$0")/.." && pwd)
SH="$ROOT/skills/claude-to-codex/lib/sync-agents-md.sh"
WORK=$(mktemp -d)
trap 'rm -rf "$WORK"' EXIT INT TERM

fail() { printf 'FAIL  %s\n' "$1" >&2; exit 1; }
expect() { # <dir> <token>
    out=$(sh "$SH" "$1") || fail "$1: exited non-zero"
    [ "$out" = "AGENTS.md: $2" ] || fail "$1: expected 'AGENTS.md: $2', got '$out'"
}

# --- missing -> created ----------------------------------------------------
P="$WORK/missing"; mkdir "$P"
expect "$P" created
[ "$(cat "$P/AGENTS.md")" = "@CLAUDE.md" ] || fail "created file is not exactly @CLAUDE.md"

# --- already imports -> unchanged, bytes identical -------------------------
P="$WORK/has"; mkdir "$P"
printf '# Agents\n\n@CLAUDE.md\n' >"$P/AGENTS.md"
before=$(cksum <"$P/AGENTS.md")
expect "$P" unchanged
[ "$(cksum <"$P/AGENTS.md")" = "$before" ] || fail "unchanged case modified the file"

# --- lacks the import -> prepended, content preserved ----------------------
P="$WORK/lacks"; mkdir "$P"
printf '# Agents\nkeep me\n' >"$P/AGENTS.md"
expect "$P" updated
[ "$(cat "$P/AGENTS.md")" = "$(printf '@CLAUDE.md\n# Agents\nkeep me')" ] || fail "prepend: $(cat "$P/AGENTS.md")"

# --- frontmatter -> inserted after closing --- -----------------------------
P="$WORK/fm"; mkdir "$P"
printf -- '---\ntitle: x\n---\nbody\n' >"$P/AGENTS.md"
expect "$P" updated
[ "$(cat "$P/AGENTS.md")" = "$(printf -- '---\ntitle: x\n---\n@CLAUDE.md\nbody')" ] || fail "frontmatter: $(cat "$P/AGENTS.md")"

# --- symlink to CLAUDE.md -> unchanged, target bytes untouched -------------
P="$WORK/link"; mkdir "$P"
printf '# Project rules\nno import here\n' >"$P/CLAUDE.md"
ln -s CLAUDE.md "$P/AGENTS.md"
before=$(cksum <"$P/CLAUDE.md")
expect "$P" unchanged
[ -L "$P/AGENTS.md" ] || fail "symlink was replaced"
[ "$(cksum <"$P/CLAUDE.md")" = "$before" ] || fail "symlink case wrote into CLAUDE.md"

printf 'PASS  claude-to-codex sync-agents-md (5 cases)\n'
