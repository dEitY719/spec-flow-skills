#!/usr/bin/env bash
# tests/pr-to-ssot-classify.sh — self-check for
# skills/pr-to-ssot-issue/lib/classify_buckets.py.
#
# The 4-bucket table in references/gap-detection.md is a pure function of a
# PR's file list; running it as prose meant two runs on the same PR could
# disagree. This asserts the ordered glob table classifies one file of each
# bucket correctly, that schema beats code on an overlapping pattern (the
# documented tie-break), and that an empty bucket comes back as `[]` rather
# than being dropped from the output.
#
#   bash tests/pr-to-ssot-classify.sh

set -euo pipefail

ROOT=$(cd "$(dirname "$0")/.." && pwd)
CLASSIFY_PY="$ROOT/skills/pr-to-ssot-issue/lib/classify_buckets.py"

fail() { printf 'FAIL  %s\n' "$1" >&2; exit 1; }

OUT=$(printf '%s\n' \
    "migrations/0001_init.sql" \
    ".github/workflows/ci.yml" \
    "docs/guide.md" \
    "src/app.py" \
    | python3 "$CLASSIFY_PY") || fail "classify_buckets.py exited non-zero"

python3 - "$OUT" <<'PY' || fail "bucket assignment or counts wrong"
import json, sys
d = json.loads(sys.argv[1])
assert d["schema"] == ["migrations/0001_init.sql"], d
assert d["infra"] == [".github/workflows/ci.yml"], d
assert d["docs"] == ["docs/guide.md"], d
assert d["code"] == ["src/app.py"], d
assert d["counts"] == {"code": 1, "schema": 1, "infra": 1, "docs": 1}, d
PY

# Tie-break: a `.py` file matching the `schema` pattern (`**/schema.{ts,py,graphql}`)
# must land in schema, not fall through to the `code` default for its
# extension — per gap-detection.md "Tie-breaks" ("schema wins").
OUT=$(printf '%s\n' "backend/schema.py" | python3 "$CLASSIFY_PY")
python3 - "$OUT" <<'PY' || fail "schema-vs-code tie-break not honored"
import json, sys
d = json.loads(sys.argv[1])
assert d["schema"] == ["backend/schema.py"], d
assert d["code"] == [], d
PY

# Empty input -> every bucket present as [], counts all zero (never dropped).
OUT=$(printf '' | python3 "$CLASSIFY_PY")
python3 - "$OUT" <<'PY' || fail "empty input should yield all-zero buckets, not omit keys"
import json, sys
d = json.loads(sys.argv[1])
for b in ("code", "schema", "infra", "docs"):
    assert d[b] == [], d
    assert d["counts"][b] == 0, d
PY

printf 'PASS  tests/pr-to-ssot-classify.sh\n'
