#!/usr/bin/env bash
# tests/ui-order-setup.sh — self-check for skills/ui-order/lib/setup_claude_md.py.
#
# The helper writes into a user's own CLAUDE.md, so the contract under test is
# what it must never do: write on a dry-run, touch a byte outside the
# ui-order markers, replace a symlink, or write anything when the markers are
# malformed. Plus: stack detection from a fixture package.json.
#
#   bash tests/ui-order-setup.sh

set -euo pipefail

ROOT=$(cd "$(dirname "$0")/.." && pwd)
PY="$ROOT/skills/ui-order/lib/setup_claude_md.py"
WORK=$(mktemp -d)
trap 'rm -rf "$WORK"' EXIT INT TERM

fail() { printf 'FAIL  %s\n' "$1" >&2; exit 1; }
run() { python3 "$PY" --project "$@"; }
BEGIN='<!-- ui-order:begin -->'
END='<!-- ui-order:end -->'

# --- dry-run writes nothing ------------------------------------------------
P="$WORK/dry"; mkdir "$P"
out=$(run "$P") || fail "dry-run exited non-zero"
[ ! -e "$P/CLAUDE.md" ] || fail "dry-run created CLAUDE.md"
case "$out" in *"action=would-create"*) : ;; *) fail "dry-run summary: $out" ;; esac
case "$out" in *"$BEGIN"*"[화면]"*"<이 프로젝트의 화면 종류"*"$END"*) : ;; *) fail "dry-run did not print the block" ;; esac
printf 'keep\n' >"$P/CLAUDE.md"
run "$P" >/dev/null
[ "$(cat "$P/CLAUDE.md")" = keep ] || fail "dry-run modified an existing CLAUDE.md"

# --- apply on missing file creates it holding only the block ---------------
P="$WORK/create"; mkdir "$P"
run "$P" --apply | grep -q 'action=created' || fail "apply on missing file: wrong action"
[ "$(head -n1 "$P/CLAUDE.md")" = "$BEGIN" ] || fail "created file does not start with the begin marker"
[ "$(tail -n1 "$P/CLAUDE.md")" = "$END" ] || fail "created file does not end with the end marker"

# --- apply appends, prior bytes preserved exactly --------------------------
P="$WORK/append"; mkdir "$P"
printf '# Project\n\nno trailing newline' >"$P/CLAUDE.md"
cp "$P/CLAUDE.md" "$WORK/prior"
run "$P" --apply | grep -q 'action=appended' || fail "append: wrong action"
n=$(wc -c <"$WORK/prior")
cmp -s <(head -c "$n" "$P/CLAUDE.md") "$WORK/prior" || fail "append altered prior bytes"
grep -qx "$BEGIN" "$P/CLAUDE.md" || fail "append: no begin marker"
# one blank line between prior content and the block
python3 - "$P/CLAUDE.md" <<'PY' || fail "append: block not preceded by exactly one blank line"
import sys
b = open(sys.argv[1], "rb").read()
assert b"no trailing newline\n\n<!-- ui-order:begin -->" in b, b[:80]
PY

# --- second apply skips (idempotent) ---------------------------------------
cp "$P/CLAUDE.md" "$WORK/after1"
out=$(run "$P" --apply) || fail "second apply exited non-zero"
case "$out" in *"action=skip"*) : ;; *) fail "second apply did not skip: $out" ;; esac
cmp -s "$P/CLAUDE.md" "$WORK/after1" || fail "second apply changed the file"

# --- --force replaces inner block only -------------------------------------
P="$WORK/force"; mkdir "$P"
printf 'HEAD\r\nbytes\n%s\nstale inner\n%s\ntail \xe2\x80\x94 bytes\n' "$BEGIN" "$END" >"$P/CLAUDE.md"
cp "$P/CLAUDE.md" "$WORK/pre-force"
run "$P" --apply --force | grep -q 'action=replaced' || fail "force: wrong action"
python3 - "$WORK/pre-force" "$P/CLAUDE.md" <<'PY' || fail "force touched bytes outside the markers"
import sys
B, E = b"<!-- ui-order:begin -->", b"<!-- ui-order:end -->"
old, new = (open(p, "rb").read() for p in sys.argv[1:])
assert old[:old.index(B) + len(B)] == new[:new.index(B) + len(B)]
assert old[old.index(E):] == new[new.index(E):]
assert b"stale inner" not in new and "## UI 요청 규칙".encode() in new
PY

# --- markers quoted inline in prose are not a block --------------------------
P="$WORK/prose"; mkdir "$P"
printf 'Setup writes between `%s` and `%s`.\n' "$BEGIN" "$END" >"$P/CLAUDE.md"
run "$P" | grep -q 'action=would-append' || fail "inline marker mention mistaken for a block"

# --- symlink CLAUDE.md -> AGENTS.md writes through, keeps the link ---------
P="$WORK/link"; mkdir "$P"
printf '# Agents\n' >"$P/AGENTS.md"
ln -s AGENTS.md "$P/CLAUDE.md"
run "$P" --apply >/dev/null
[ -L "$P/CLAUDE.md" ] || fail "symlink CLAUDE.md was replaced by a file"
[ "$(readlink "$P/CLAUDE.md")" = AGENTS.md ] || fail "symlink target changed"
grep -qx "$BEGIN" "$P/AGENTS.md" || fail "block not written into AGENTS.md"

# --- malformed markers fail closed, nothing written ------------------------
malformed() {
    local name=$1 body=$2 P="$WORK/bad-$1"
    mkdir "$P"; printf '%s' "$body" >"$P/CLAUDE.md"; cp "$P/CLAUDE.md" "$WORK/bad"
    if run "$P" --apply --force >/dev/null 2>"$WORK/err"; then
        fail "$name: malformed markers accepted"
    fi
    grep -q 'malformed ui-order markers' "$WORK/err" || fail "$name: unclear error: $(cat "$WORK/err")"
    cmp -s "$P/CLAUDE.md" "$WORK/bad" || fail "$name: file written despite malformed markers"
}
malformed begin-only "x
$BEGIN
y
"
malformed duplicate "$BEGIN
a
$END
$BEGIN
b
$END
"
malformed reversed "$END
$BEGIN
"

# --- stack detection -------------------------------------------------------
P="$WORK/detect"; mkdir "$P"
cat >"$P/package.json" <<'JSON'
{"dependencies": {"next": "14.0.0", "react": "18.0.0", "lucide-react": "0.1.0"},
 "devDependencies": {"tailwindcss": "3.4.0"}}
JSON
printf '{}\n' >"$P/components.json"
out=$(run "$P")
case "$out" in *"stack=Next.js,Tailwind,shadcn/ui,Lucide "*) : ;; *) fail "detection summary: $out" ;; esac
case "$out" in *"스택: Next.js, Tailwind + shadcn/ui, 아이콘 Lucide, "*) : ;; *) fail "detected stack not written plain" ;; esac
case "$out" in *"Tailwind + shadcn/ui (기본값)"*) fail "detected stack still marked (기본값)" ;; esac

echo "ok    ui-order setup: dry-run, create, append, skip, force, symlink, malformed, detection"
