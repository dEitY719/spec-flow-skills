#!/usr/bin/env bash
# tests/prd-to-trd-plan.sh — self-check for skills/prd-to-trd/lib/plan.py.
#
# The round-trip invariant of references/plan-format.md is what --apply stands
# on: it reads the plan, not the PRD, so a silent mis-parse writes the wrong
# frontmatter into every scaffold. This asserts the parser catches the four
# ways a hand-edited plan breaks it, and that render round-trips the repo's own
# worked example back to the committed scaffold.
#
#   bash tests/prd-to-trd-plan.sh

set -euo pipefail

ROOT=$(cd "$(dirname "$0")/.." && pwd)
PLAN_PY="$ROOT/skills/prd-to-trd/lib/plan.py"
EXAMPLE="$ROOT/docs/examples/prd-to-trd"
WORK=$(mktemp -d)
trap 'rm -rf "$WORK"' EXIT INT TERM

fail() { printf 'FAIL  %s\n' "$1" >&2; exit 1; }

# --- parse: the repo's own worked example --------------------------------
python3 "$PLAN_PY" parse "$EXAMPLE/plan.md" >"$WORK/rows.json" \
    || fail "parse rejected the committed example plan"

python3 - "$WORK/rows.json" <<'PY' || fail "parse produced the wrong rows"
import json, sys
rows = json.load(open(sys.argv[1], encoding="utf-8"))
assert len(rows) == 8, f"expected 8 rows, got {len(rows)}"
assert [r["slug"] for r in rows][0] == "skill-inventory", rows[0]
by = {r["slug"]: r for r in rows}
# (none) is a sentinel, not data: it must parse to empty/None, never a literal.
assert by["ci-gate"]["nf_primary"] is None, by["ci-gate"]
assert by["ci-gate"]["nf_cited"] == ["NF-5", "NF-6"], by["ci-gate"]
assert by["guide-pages"]["d_items"] == ["D-1", "D-5"], by["guide-pages"]
assert by["usage-pages"]["nf_primary"] is None, by["usage-pages"]
assert all("(none)" not in json.dumps(r, ensure_ascii=False) for r in rows), rows
PY

# --- parse: each invariant violation is caught, with a line number ---------
reject() {
    local name=$1 file=$2 want=$3 out
    if out=$(python3 "$PLAN_PY" parse "$file" 2>&1); then
        fail "$name: parse accepted an invalid plan"
    fi
    case "$out" in
        *"$want"*) : ;;
        *) fail "$name: expected ${want} in: ${out}" ;;
    esac
}

# 1. a blank cell where the (none) sentinel belongs
sed 's/| (none) | NF-5,NF-6 |/|  | NF-5,NF-6 |/' "$EXAMPLE/plan.md" >"$WORK/blank.md"
reject "blank cell" "$WORK/blank.md" "blank"

# 2. a row added during --apply pointing at a slug that is not in the plan
sed 's/^| ci-gate |.*$/&\n| extra-slug | F-99 | (none) | (none) | (none) | nowhere |/' \
    "$EXAMPLE/plan.md" >"$WORK/dangling.md"
reject "dangling 인접 TRD" "$WORK/dangling.md" "not a slug in this plan"

# 3. a reordered section heading
sed 's/^## Suggested splits$/## Manual review/; s/^## Manual review$/## Suggested splits/' \
    "$EXAMPLE/plan.md" >"$WORK/reordered.md"
reject "reordered sections" "$WORK/reordered.md" "order"

# 4. a renamed table column
sed 's/| NF-# (primary) |/| NF-primary |/' "$EXAMPLE/plan.md" >"$WORK/column.md"
reject "renamed column" "$WORK/column.md" "table header"

# --- render: the example plan reproduces the committed scaffold ------------
python3 "$PLAN_PY" render \
    --rows "$WORK/rows.json" \
    --template "$ROOT/skills/prd-to-trd/references/template-fallback.md" \
    --out-dir "$WORK/trd" \
    --prd "$EXAMPLE/prd-docs-pages.md" >"$WORK/render.out"

grep -q '^written=8 skipped=0$' "$WORK/render.out" \
    || fail "render: expected written=8 skipped=0, got $(cat "$WORK/render.out")"

# The committed scaffold's own frontmatter, minus the Draft-v1 date line, which
# render stamps with today's date by design.
for slug in ci-gate usage-pages; do
    diff <(sed -n '/^> \*\*책임 PRD 항목\*\*/,/^> \*\*인접 TRD\*\*/p' "$EXAMPLE/trd/$slug.md") \
         <(sed -n '/^> \*\*책임 PRD 항목\*\*/,/^> \*\*인접 TRD\*\*/p' "$WORK/trd/$slug.md") \
        || fail "render: $slug frontmatter does not match the committed scaffold"
done

# --- render: skip-on-exists is the default, --force is the only override ----
python3 "$PLAN_PY" render --rows "$WORK/rows.json" \
    --template "$ROOT/skills/prd-to-trd/references/template-fallback.md" \
    --out-dir "$WORK/trd" --prd "$EXAMPLE/prd-docs-pages.md" >"$WORK/again.out"
grep -q '^written=0 skipped=8$' "$WORK/again.out" \
    || fail "render: second run must skip all 8, got $(tail -n1 "$WORK/again.out")"

python3 "$PLAN_PY" render --rows "$WORK/rows.json" \
    --template "$ROOT/skills/prd-to-trd/references/template-fallback.md" \
    --out-dir "$WORK/trd" --prd "$EXAMPLE/prd-docs-pages.md" --force >"$WORK/forced.out"
grep -q '^written=8 skipped=0$' "$WORK/forced.out" \
    || fail "render --force: expected written=8, got $(tail -n1 "$WORK/forced.out")"

echo "ok    prd-to-trd plan.py: parse invariants + render round-trip"
