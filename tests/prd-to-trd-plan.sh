#!/usr/bin/env bash
# tests/prd-to-trd-plan.sh — self-check for skills/prd-to-trd/lib/plan.py.
#
# The round-trip invariant of references/plan-format.md is what --apply stands
# on: it reads the plan, not the PRD, so a silent mis-parse writes the wrong
# frontmatter into every scaffold. This asserts the parser catches the five
# ways a hand-edited plan breaks it, that render round-trips the repo's own
# worked example back to the committed scaffolds, and that a mid-flow write
# failure reports partial state instead of a traceback.
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
# The title override is part of the emitted schema, defaulted from the slug.
assert by["ci-gate"]["title"] == "Ci Gate", by["ci-gate"]
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
# The swap needs a placeholder: two chained `s///` would rewrite the first
# heading twice and leave the file with two `## Suggested splits`.
sed 's/^## Suggested splits$/## \x01/; s/^## Manual review$/## Suggested splits/; s/^## \x01$/## Manual review/' \
    "$EXAMPLE/plan.md" >"$WORK/reordered.md"
reject "reordered sections" "$WORK/reordered.md" "must appear in the order"

# 4. a renamed table column
sed 's/| NF-# (primary) |/| NF-primary |/' "$EXAMPLE/plan.md" >"$WORK/column.md"
reject "renamed column" "$WORK/column.md" "table header"

# 5. a typo'd PRD item id. Whether F-7 exists in the PRD is out of scope by
#    design (the plan is the SSOT), but its shape is the parser's business.
sed 's/| ci-gate | F-12,F-13 |/| ci-gate | F12,F-13 |/' "$EXAMPLE/plan.md" >"$WORK/itemid.md"
reject "malformed item id" "$WORK/itemid.md" "malformed PRD item id"

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

# --- render: a title override reaches the scaffold --------------------------
python3 - "$WORK/rows.json" "$WORK/titled.json" <<'TITLES'
import json, sys
rows = json.load(open(sys.argv[1], encoding="utf-8"))
for r in rows:
    if r["slug"] == "ci-gate":
        r["title"] = "CI Gate"
json.dump(rows, open(sys.argv[2], "w", encoding="utf-8"), ensure_ascii=False)
TITLES
python3 "$PLAN_PY" render --rows "$WORK/titled.json" \
    --template "$ROOT/skills/prd-to-trd/references/template-fallback.md" \
    --out-dir "$WORK/titled" --prd "$EXAMPLE/prd-docs-pages.md" >/dev/null
diff <(head -n1 "$EXAMPLE/trd/ci-gate.md") <(head -n1 "$WORK/titled/ci-gate.md") \
    || fail "render: the row title override did not reach the scaffold heading"

# --- render: a mid-flow write failure reports partial state, no rollback ----
mkdir -p "$WORK/partial"
# The 4th slug's target path is taken by a directory, so its write fails after
# three scaffolds have already landed. --force is what makes render try to write
# it rather than take the skip-on-exists branch.
FOURTH=$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1], encoding="utf-8"))[3]["slug"])' "$WORK/rows.json")
mkdir -p "$WORK/partial/$FOURTH.md"
if out=$(python3 "$PLAN_PY" render --rows "$WORK/rows.json" --force \
    --template "$ROOT/skills/prd-to-trd/references/template-fallback.md" \
    --out-dir "$WORK/partial" --prd "$EXAMPLE/prd-docs-pages.md" 2>&1); then
    fail "render: a failed write must exit non-zero"
fi
case "$out" in
    *"written so far"*"[FAIL] spec-flow:prd-to-trd"*) : ;;
    *) fail "render: expected a partial-state report and a [FAIL] line, got: ${out}" ;;
esac
[ "$(find "$WORK/partial" -maxdepth 1 -name '*.md' -type f | wc -l)" -eq 3 ] \
    || fail "render: no auto-rollback — the 3 scaffolds written before the failure must remain"

# --- render: an edited slug cannot escape the output directory -------------
python3 - "$WORK/rows.json" "$WORK/escape.json" <<'ESCAPE'
import json, sys
rows = json.load(open(sys.argv[1], encoding="utf-8"))
rows[0]["slug"] = "../../outside"
json.dump(rows, open(sys.argv[2], "w", encoding="utf-8"), ensure_ascii=False)
ESCAPE
mkdir -p "$WORK/escape"
if out=$(python3 "$PLAN_PY" render --rows "$WORK/escape.json" \
    --template "$ROOT/skills/prd-to-trd/references/template-fallback.md" \
    --out-dir "$WORK/escape" --prd "$EXAMPLE/prd-docs-pages.md" 2>&1); then
    fail "render: a traversal slug must be refused"
fi
case "$out" in
    *"not kebab-case"*) : ;;
    *) fail "render: expected a kebab-case refusal, got: ${out}" ;;
esac
[ -e "$WORK/outside.md" ] && fail "render: wrote outside the out-dir"

# --- render: a project template that drifted from the standard warns --------
sed '/^## 8\. Open Questions$/,$d' "$EXAMPLE/trd/ci-gate.md" >"$WORK/_template.md"
python3 "$PLAN_PY" render --rows "$WORK/rows.json" \
    --template "$WORK/_template.md" --out-dir "$WORK/drift" \
    --prd "$EXAMPLE/prd-docs-pages.md" 2>"$WORK/drift.err" >/dev/null
grep -q 'numbered sections (expected 8)' "$WORK/drift.err" \
    || fail "render: a 7-section project template must warn, got: $(cat "$WORK/drift.err")"

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

# --- render --force: a symlinked target must not be written through --------
mkdir -p "$WORK/link"
echo original >"$WORK/victim.md"
ln -s "$WORK/victim.md" "$WORK/link/$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1], encoding="utf-8"))[0]["slug"])' "$WORK/rows.json").md"
if out=$(python3 "$PLAN_PY" render --rows "$WORK/rows.json" --force \
    --template "$ROOT/skills/prd-to-trd/references/template-fallback.md" \
    --out-dir "$WORK/link" --prd "$EXAMPLE/prd-docs-pages.md" 2>&1); then
    fail "render --force: a symlinked target must be refused"
fi
case "$out" in
    *"is a symlink"*) : ;;
    *) fail "render --force: expected a symlink refusal, got: ${out}" ;;
esac
[ "$(cat "$WORK/victim.md")" = original ] \
    || fail "render --force: wrote through a symlink, outside the out-dir"

echo "ok    prd-to-trd plan.py: parse invariants + render round-trip"
