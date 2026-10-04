#!/usr/bin/env bash
# tests/ui-order-check.sh — self-check for skills/ui-order/lib/check_frontend.py.
#
# --check is a read-only audit, so the first contract is that it writes
# nothing: every fixture file's checksum must survive a run. Then every Layer A
# check fires on its positive case and stays quiet on its clean case, the
# Lucide-only icon policy holds, excluded trees are ignored, and the output is
# byte-identical across runs. Emoji are generated at runtime so this file holds
# none (CI emoji gate).
#
#   bash tests/ui-order-check.sh

set -euo pipefail

ROOT=$(cd "$(dirname "$0")/.." && pwd)
PY="$ROOT/skills/ui-order/lib/check_frontend.py"
WORK=$(mktemp -d)
trap 'rm -rf "$WORK"' EXIT INT TERM

fail() { printf 'FAIL  %s\n' "$1" >&2; exit 1; }
has() { grep -qF -- "$1" "$WORK/out" || fail "missing: $1"; }
hasnt() { if grep -qF -- "$1" "$WORK/out"; then fail "unexpected: $1"; fi; }
ROCKET=$(python3 -c 'print(chr(0x1F680), end="")')
BELL=$(python3 -c 'print(chr(0x1F514), end="")')

P="$WORK/app"; mkdir -p "$P/src" "$P/node_modules/pkg" "$P/dist"
cat >"$P/package.json" <<'JSON'
{"dependencies": {"react": "18.0.0", "react-icons": "5.0.0"}}
JSON
cat >"$P/src/Bad.tsx" <<EOF
import { FaBeer } from "react-icons/fa";
export function Bad() {
  return (
    <div className="p-[13px] gap-[16px] rounded-lg" style={{ color: "#ff0000" }}>
      <button onClick={() => go()}><FaBeer /></button>
      <button onClick={() => go()}>$BELL</button>
      <img src="/a.png" />
      <input className="outline-none border" />
      <span>$ROCKET Launch</span>
      <p style={{ background: "rgb(1, 2, 3)" }}>x</p>
      <div className="rounded-md rounded-xl rounded-[7px]" />
    </div>
  );
}
EOF
cat >"$P/src/Good.tsx" <<'EOF'
import { X } from "lucide-react";
export function Good() {
  return (
    <div className="p-4 gap-2">
      <button aria-label="닫기" onClick={() => close()}><X className="h-5 w-5" /></button>
      <button onClick={save}>저장</button>
      <img src="/b.png" alt="" />
      <input className="outline-none focus-visible:ring-2" />
      <p style={{ color: "hsl(var(--primary))" }}>ok</p>
    </div>
  );
}
EOF
cat >"$P/src/styles.css" <<'EOF'
:root { --brand: #123456; }
.card { padding: 12px; margin: 10px 16px; gap: 8px; border-radius: 12px; }
.btn { outline: none; }
.btn2:focus-visible { outline: none; box-shadow: 0 0 0 2px var(--brand); }
@media (min-width: 700px) { .a { color: var(--brand); } }
@media (max-width: 900px) { .b { color: var(--brand); } }
@media (min-width: 1100px) { .c { color: var(--brand); } }
@media (min-width: 640px) { .d { color: var(--brand); } }
.row { padding: 20px 24px; }
EOF
cat >"$P/src/theme.ts" <<'EOF'
export const colors = { primary: "#0055ff", danger: "rgb(200, 0, 0)" };
EOF
# review (agy, PR #17): a "theme"-named component is not a token file; ~icons/lucide is Lucide
cat >"$P/src/ThemeToggle.tsx" <<'EOF'
import Sun from "~icons/lucide/sun";
export const T = () => <span style={{ color: "#ff0000" }} />;
EOF
cat >"$P/src/List.tsx" <<'EOF'
import { useQuery } from "@tanstack/react-query";
export function List() {
  const { data } = useQuery({ queryKey: ["items"], queryFn: getItems });
  return <ul>{data.map((i) => <li key={i.id}>{i.name}</li>)}</ul>;
}
EOF
# excluded trees and files: must not appear in the output at all
for f in node_modules/pkg/index.tsx dist/app.js src/vendor.min.js src/Bad.test.tsx; do
    printf 'import X from "react-icons/fa";\n<img src="x" />\nconst c = "#abcdef";\n' >"$P/$f"
done
cat >"$P/CLAUDE.md" <<'EOF'
# App

<!-- ui-order:begin -->
## 화면 주문서 (프로젝트 기본값)
[화면]     <이 프로젝트의 화면 종류: 예) 대시보드 + 목록-상세 + 설정>
[토큰]     간격 8의 배수, 라운드 12px. (기본값)
[반응형]   모바일 퍼스트, 브레이크포인트 640/1024. (기본값)
<!-- ui-order:end -->
EOF

sums() { (cd "$P" && find . -type f -print0 | sort -z | xargs -0 cksum) >"$1"; }
sums "$WORK/before"
python3 "$PY" --project "$P" >"$WORK/out" || fail "scanner exited non-zero"
python3 "$PY" --project "$P" >"$WORK/out2"
sums "$WORK/after"

# --- read-only: no fixture file changed, none created ------------------------
cmp -s "$WORK/before" "$WORK/after" || fail "--check modified the fixture: $(diff "$WORK/before" "$WORK/after")"

# --- deterministic and sorted (severity, check, file, line) --------------------
cmp -s "$WORK/out" "$WORK/out2" || fail "output differs between runs"
python3 - "$WORK/out" <<'PY' || fail "findings not sorted by severity"
import sys
rank = {"high": 0, "med": 1, "low": 2, "info": 3}
rows = [l.split("|") for l in open(sys.argv[1], encoding="utf-8") if "|" in l]
keys = [rank[r[1]] for r in rows]
assert keys == sorted(keys), keys
PY

# --- 1. token-spacing / token-radius -----------------------------------------
has 'token-spacing|med|src/Bad.tsx:4|p-[13px] gap-[16px]'
has 'token-spacing|med|src/styles.css:2|padding:12px margin:10px'
has 'token-spacing|low|src/styles.css:9|padding:20px -> '
hasnt 'token-spacing|med|src/Good.tsx'
has 'token-radius|med|'
grep -F 'token-radius|med|' "$WORK/out" | grep -qF 'rounded-[7px] x1' || fail "radius inventory missing arbitrary value"

# --- 2. color-hardcode: per-file count, token/theme files exempt --------------
has 'color-hardcode|med|src/Bad.tsx:4|2 color literal(s)'
hasnt 'color-hardcode|med|src/Good.tsx'
hasnt 'color-hardcode|med|src/theme.ts'
has 'color-hardcode|med|src/ThemeToggle.tsx:2|1 color literal(s)'
hasnt 'color-hardcode|med|src/styles.css'

# --- 3. a11y --------------------------------------------------------------------
has 'a11y-icon-button|high|src/Bad.tsx:5|'
has 'a11y-icon-button|high|src/Bad.tsx:6|icon-only button without aria-label (emoji)'
hasnt 'a11y-icon-button|high|src/Good.tsx'
has 'a11y-img-alt|med|src/Bad.tsx:7|'
hasnt 'a11y-img-alt|med|src/Good.tsx'
has 'a11y-focus|med|src/Bad.tsx:8|outline-none without focus-visible'
has 'a11y-focus|med|src/styles.css:3|'
hasnt 'a11y-focus|med|src/Good.tsx'
hasnt 'a11y-focus|med|src/styles.css:4|'

# --- 4. Lucide-only icon policy --------------------------------------------------
has 'icon-set|high|src/Bad.tsx:1|react-icons/fa -> replace with the Lucide equivalent (lucide-react)'
hasnt 'icon-set|high|src/Good.tsx'
hasnt 'icon-set|high|src/ThemeToggle.tsx'
has 'icon-emoji|high|src/Bad.tsx:9|U+1F680'
has 'icon-set|high|package.json:0|icons used but no Lucide dependency'

# --- 5. breakpoints: 700/900/1100 beyond the block's 640/1024 --------------------
has 'breakpoints|med|src/styles.css:5|3 widths beyond 640/1024: 700/900/1100'

# --- 6. data-view candidates for the agent ---------------------------------------
has 'data-view-candidate|info|src/List.tsx:1|signals=useQuery states-seen=none'
hasnt 'data-view-candidate|info|src/Good.tsx'

# --- 8. order block facts ----------------------------------------------------------
has 'order-unconfirmed|med|CLAUDE.md:5|[화면] is still the <...> placeholder'
has 'order-block|info|CLAUDE.md:3|present, 2 (기본값)'

# --- exclusions ----------------------------------------------------------------------
for x in "|node_modules/" "|dist/" "vendor.min.js" "Bad.test.tsx"; do hasnt "$x"; done
tail -n1 "$WORK/out" | grep -qE '^\[OK\] spec-flow:ui-order check target=.* files=6 findings=[0-9]+ high=[0-9]+ med=[0-9]+ low=[0-9]+$' \
    || fail "summary line: $(tail -n1 "$WORK/out")"

# --- clean project: Lucide dep, confirmed block, no findings ---------------------------
C="$WORK/clean"; mkdir -p "$C/src"
printf '{"dependencies": {"lucide-react": "0.1.0"}}\n' >"$C/package.json"
cp "$P/src/Good.tsx" "$C/src/"
printf '<!-- ui-order:begin -->\n[화면]     대시보드. 새 화면은 `app/<name>.tsx`\n[반응형]   640/1024\n<!-- ui-order:end -->\n' >"$C/CLAUDE.md"
python3 "$PY" --project "$C" >"$WORK/out"
tail -n1 "$WORK/out" | grep -q 'files=1 findings=0 high=0 med=0 low=0$' || fail "clean project: $(cat "$WORK/out")"

# --- missing block, usage and I/O errors -----------------------------------------------
M="$WORK/noblock"; mkdir "$M"
python3 "$PY" --project "$M" >"$WORK/out"
has 'order-unconfirmed|med|CLAUDE.md:0|no ui-order block'
rc=0; python3 "$PY" --bogus >/dev/null 2>&1 || rc=$?
[ "$rc" = 2 ] || fail "usage error exit $rc, want 2"
rc=0; python3 "$PY" --project "$WORK/missing" >/dev/null 2>&1 || rc=$?
[ "$rc" = 1 ] || fail "missing project exit $rc, want 1"

# --- .gitignore is honoured inside a git repo -------------------------------------------
G="$WORK/gitproj"; mkdir -p "$G/gen" "$G/src"
cp "$P/src/Bad.tsx" "$G/gen/"; cp "$P/src/Good.tsx" "$G/src/"
printf 'gen/\n' >"$G/.gitignore"
git -C "$G" init -q
python3 "$PY" --project "$G" >"$WORK/out"
hasnt 'gen/Bad.tsx'
tail -n1 "$WORK/out" | grep -q 'files=1 ' || fail "gitignore: $(tail -n1 "$WORK/out")"

echo "ok    ui-order check: read-only, deterministic, spacing, radius, color, a11y, lucide, breakpoints, data-view, order block, exclusions"
