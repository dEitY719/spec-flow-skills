#!/usr/bin/env bash
# tests/trd-to-issues-apply-plan.sh — self-check for skills/trd-to-issues/lib/apply_plan.py.
#
# Two invariants live here.
#
# 1. `--apply` creates the issues first and patches their `Depends on:` lines
#    second, with no rollback. A mis-substituted `#new-N` files issues whose
#    dependencies point at the wrong numbers and nothing downstream notices, so
#    `resolve` must refuse an unmapped citation rather than emit a number.
# 2. The three-way agreement between references/decomposition-rules.md,
#    references/plan-format.md and references/samples/expected-plan.md used to
#    be a note asking a human to remember to run a diff. Parsing the committed
#    sample and cross-checking it against the fixture it was recorded from
#    enforces it instead.
#
#   bash tests/trd-to-issues-apply-plan.sh

set -euo pipefail

ROOT=$(cd "$(dirname "$0")/.." && pwd)
APPLY_PLAN="$ROOT/skills/trd-to-issues/lib/apply_plan.py"
SAMPLES="$ROOT/skills/trd-to-issues/references/samples"
WORK=$(mktemp -d)
trap 'rm -rf "$WORK"' EXIT INT TERM

fail() { printf 'FAIL  %s\n' "$1" >&2; exit 1; }

# --- parse: the committed sample plan -------------------------------------
python3 "$APPLY_PLAN" parse "$SAMPLES/expected-plan.md" >"$WORK/rows.json" \
    || fail "parse rejected the committed sample plan"

python3 - "$WORK/rows.json" "$SAMPLES/trd-fixture.md" <<'PY' || fail "parse produced the wrong plan"
import json, sys
plan = json.load(open(sys.argv[1], encoding="utf-8"))
fixture = open(sys.argv[2], encoding="utf-8").read()

ms = plan["milestones"]
assert [m["name"] for m in ms] == ["M0a", "M0b"], ms
tasks = [t for m in ms for t in m["tasks"]]
assert [t["id"] for t in tasks] == ["new-1", "new-2", "new-3"], tasks
assert plan["failures"] == [], plan["failures"]

# "Depends on T1, T2" in the TRD must survive as virtual citations in the plan.
by = {t["id"]: t for t in tasks}
assert by["new-1"]["depends_on"] == [], by["new-1"]
assert by["new-2"]["depends_on"] == ["new-1"], by["new-2"]
assert by["new-3"]["depends_on"] == ["new-1", "new-2"], by["new-3"]

# The pro-friendly / max-only split: the multi-AC task is the max-only one.
assert by["new-1"]["labels"][0] == "pro-friendly", by["new-1"]
assert by["new-2"]["labels"] == ["pro-friendly"], by["new-2"]
assert by["new-3"]["labels"] == ["max-only"], by["new-3"]
assert len(by["new-3"]["ac"]) == 3, by["new-3"]
# The priority label lifted from the TRD rides alongside the tier label.
assert len(by["new-1"]["labels"]) == 2, by["new-1"]

# Three-way agreement: every plan task and milestone must trace to the fixture.
for m in ms:
    assert m["name"] in fixture, f"milestone {m['name']} is not in trd-fixture.md"
for t in tasks:
    assert t["title"] in fixture, f"task title not in trd-fixture.md: {t['title']}"
PY

# --- resolve: #new-N becomes the real issue number -------------------------
printf '{"new-1": 101, "new-2": 102, "new-3": 103}\n' >"$WORK/map.json"
python3 "$APPLY_PLAN" resolve --rows "$WORK/rows.json" --map "$WORK/map.json" \
    >"$WORK/resolved.json" || fail "resolve rejected a complete map"

python3 - "$WORK/resolved.json" <<'PY' || fail "resolve substituted the wrong numbers"
import json, sys
rows = {r["id"]: r for r in json.load(open(sys.argv[1], encoding="utf-8"))}
assert rows["new-2"]["number"] == 102, rows["new-2"]
assert "Depends on: #101" in rows["new-2"]["body"], rows["new-2"]["body"]
assert "Depends on: #101, #102" in rows["new-3"]["body"], rows["new-3"]["body"]
# No virtual citation may survive into a body that is about to be filed.
assert all("#new-" not in r["body"] for r in rows.values()), rows
PY

# --- resolve: an unmapped citation must fail, not guess --------------------
printf '{"new-2": 102, "new-3": 103}\n' >"$WORK/partial.json"
if python3 "$APPLY_PLAN" resolve --rows "$WORK/rows.json" --map "$WORK/partial.json" \
    >"$WORK/bad.json" 2>"$WORK/bad.err"; then
    fail "resolve emitted rows for a map missing new-1"
fi
grep -q 'new-1' "$WORK/bad.err" || fail "resolve did not name the unmapped citation"

# --- parse: hand-broken plans fail, with the offending line number ---------
# Each case names the line the reader has to go fix, so `line 1:` is a bug.
reject() {  # <case-name> <sed-expression> <string the message must name>
    sed "$2" "$SAMPLES/expected-plan.md" >"$WORK/broken.md"
    if python3 "$APPLY_PLAN" parse "$WORK/broken.md" >/dev/null 2>"$WORK/broken.err"; then
        fail "parse accepted $1"
    fi
    grep -qE 'line [1-9][0-9]*:' "$WORK/broken.err" || fail "$1: no line number in $(cat "$WORK/broken.err")"
    if grep -qE '^\[FAIL\] spec-flow:trd-to-issues line 1:' "$WORK/broken.err"; then
        fail "$1: reported line 1 instead of the offending line"
    fi
    grep -qF "$3" "$WORK/broken.err" || fail "$1: message did not name $3"
}

reject "an out-of-order #new-N" 's/#new-2 chore(ci)/#new-5 chore(ci)/' 'new-5'
reject "a dangling dependency" 's/Depends on: #new-1$/Depends on: #new-9/' 'new-9'
reject "a dropped Labels bullet" '/  - Labels: max-only/d' 'new-3'
reject "a fourth acceptance criterion" \
    's/^    - \[ \] `tox -e ruff`.*/&\n    - [ ] extra\n    - [ ] extra2/' 'new-2'
# Free prose inside a task must fail loudly, never be silently dropped from
# the body resolve() renders (PR #12 review, agy + codex BLOCKER).
reject "task prose outside the skeleton" \
    's/^  - Labels: max-only$/  Implementation note: use the bun runtime.\n&/' 'Implementation note'

printf 'PASS  tests/trd-to-issues-apply-plan.sh\n'
