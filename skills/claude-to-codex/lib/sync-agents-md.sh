#!/bin/sh
# sync-agents-md.sh <repo-root> — make <repo-root>/AGENTS.md import @CLAUDE.md.
# Prints exactly one line: AGENTS.md: created|updated|unchanged
# Contract: references/agents-md-handling.md. Never adds Codex policy text.
set -eu

[ $# -eq 1 ] && [ -d "$1" ] || { echo "usage: sync-agents-md.sh <repo-root>" >&2; exit 2; }
f="$1/AGENTS.md"

# A symlink to CLAUDE.md already is CLAUDE.md; writing through it would
# pollute CLAUDE.md with an import of itself.
if [ -L "$f" ] && [ "$(readlink -f "$f")" = "$(readlink -f "$1/CLAUDE.md")" ]; then
    echo "AGENTS.md: unchanged"; exit 0
fi

if [ ! -e "$f" ]; then
    printf '@CLAUDE.md\n' >"$f"
    echo "AGENTS.md: created"; exit 0
fi

if grep -qF '@CLAUDE.md' "$f"; then
    echo "AGENTS.md: unchanged"; exit 0
fi

tmp=$(mktemp)
trap 'rm -f "$tmp"' EXIT
# Leading YAML frontmatter: insert after its closing ---; otherwise (or if it
# never closes) at the top. k = line number to insert after.
k=0
[ "$(head -n 1 "$f")" = "---" ] &&
    k=$(awk 'NR > 1 && $0 == "---" { print NR; exit }' "$f")
awk -v k="${k:-0}" 'k == 0 && NR == 1 { print "@CLAUDE.md" } { print } NR == k { print "@CLAUDE.md" } END { if (NR == 0) print "@CLAUDE.md" }' "$f" >"$tmp"
cat "$tmp" >"$f"   # write in place: keeps mode and any non-CLAUDE.md symlink
echo "AGENTS.md: updated"
