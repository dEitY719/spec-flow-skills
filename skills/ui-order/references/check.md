# Check mode: `--check`

A read-only audit of an existing frontend for vague or drifting UI criteria. It
writes nothing — not even the project `CLAUDE.md`. The report is the final output;
no blocking prompt.

## Run

Same plugin-root rule as `--setup` (including the personal-skill export from the
"Base directory": `references/setup.md`): resolve the helper via
`$CLAUDE_PLUGIN_ROOT`, stop with `[FAIL] spec-flow:ui-order: CLAUDE_PLUGIN_ROOT unset` when it is unset,
never guess a path.

```bash
[ -n "${CLAUDE_PLUGIN_ROOT:-}" ] || { echo "[FAIL] spec-flow:ui-order: CLAUDE_PLUGIN_ROOT unset"; exit 1; }
python3 "$CLAUDE_PLUGIN_ROOT/skills/ui-order/lib/check_frontend.py" [--project <dir>]
```

`--project <dir>` defaults to the git toplevel of the CWD, else the CWD. Exit 0 =
report printed (findings do not fail it), 1 = I/O error, 2 = usage error. On a
non-zero exit, print its stderr and stop.

## Layer A — helper output

One line per finding, sorted by severity then check, file, line:

```
CHECK_ID|severity|file:line|detail
[OK] spec-flow:ui-order check target=<dir> files=<n> findings=<n> high=<n> med=<n> low=<n>
```

`info` lines are facts for Layer B and are not counted. Line 0 = whole file. In a git repo only tracked + untracked-not-ignored files are scanned (`.gitignore` is honoured); outside git, a walk skipping `SKIP_DIRS`.

| Check | Severity | Fires on |
|-------|----------|----------|
| `icon-set` | high | Import from a non-Lucide icon library (react-icons, @heroicons, @mui/icons-material, @fortawesome, @tabler/icons, phosphor, @radix-ui/react-icons, ...) |
| `icon-set` | high | Icons in use but no Lucide dependency in `package.json` |
| `icon-emoji` | high | Emoji used as an icon in markup or a string literal |
| `a11y-icon-button` | high | `<button>`/`<Button>` whose only child is an icon, svg or emoji, with no `aria-label` / `aria-labelledby` / `title` |
| `a11y-focus` | med | `outline-none` / `outline: none` with no `focus-visible` in the same element or rule |
| `a11y-img-alt` | med | `<img>` without `alt` |
| `token-spacing` | med / low | Tailwind arbitrary spacing (`p-[13px]`) or CSS padding/margin/gap px: not a multiple of 4 = med, of 8 = low |
| `token-radius` | med / info | 4+ distinct radius values = med; otherwise the inventory as info |
| `color-hardcode` | med | Per-file count of `#hex` / `rgb()` / `hsl()` literals outside theme/token files, custom-property definitions and comments; a digits-only `#123` counts only as a whole quoted string or a color property value (else it is an issue ref) |
| `breakpoints` | med / info | 3+ media widths beyond the block's `[반응형]` set (default 640/1024) |
| `order-unconfirmed` | med | No ui-order block, malformed markers, or `[화면]` still the `<...>` placeholder |
| `data-view-candidate` | info | File with a data signal (fetch, axios, useQuery, useSWR, load, async component) plus the state hints seen |
| `order-block` | info | Block present, with the count of `(기본값)` values to verify |

## Layer B — judgment the helper cannot make

Read the code the helper points at; do not re-scan the whole tree.

- **`exception-states` (high)** — for each `data-view-candidate`, open the file and
  the component that renders its data. Missing 로딩, 빈 상태 (0건) or 에러 handling ->
  one finding per missing state. `states-seen=none` is a strong hint, not proof.
- **`overlay-mix` (med)** — one purpose served by mixed overlays: confirmations via
  both a modal dialog and `window.confirm`, or completion feedback via both toast
  and `alert()`. Grep `confirm(`, `alert(`, `Dialog`, `Modal`, `toast`.
- **`order-unconfirmed` contradictions (med)** — compare each `(기본값)` value in the
  block with what the code consistently uses (`token-radius` / `breakpoints`
  inventories, spacing, icon set). Block says radius 12px but the code uses
  `rounded-lg` (8px) everywhere -> finding.

Drop a helper finding only with a stated reason (e.g. a `color-hardcode` hit that is
a chart palette); never silently.

## Report (Korean, the final output)

1. One line: target, files scanned, count by severity.
2. Groups by check, highest impact first (high -> med -> low). Each item:
   `file:line` evidence + the precise UI term to use when fixing — e.g.
   "아이콘 버튼 aria-label", "엠프티 스테이트 + 다음 행동 버튼", "Lucide outline 20px",
   "포커스 링 (focus-visible)", "간격 토큰 8의 배수". Collapse more than 5 hits of one
   check into the top 5 plus a count.
3. **주문서 반영 제안** — concrete edits to the `CLAUDE.md` ui-order block that record
   what the code actually standardized on (e.g. `[토큰] ... 라운드 8px`, `[반응형]
   640/1024/1280`, `아이콘 Lucide`), or the `[화면]` value to fill in. Suggest only:
   tell the user to apply it by editing the block, or by
   `/spec-flow:ui-order --setup --apply --force` and then editing.

Example item:

```
### 아이콘 (high)
- src/Toolbar.tsx:12 — react-icons/fa import. Lucide 단일 세트로 교체 (lucide-react, outline 20px).
- src/Header.tsx:31 — 아이콘만 있는 버튼에 이름 없음. 아이콘 버튼 aria-label="닫기" 추가.
```
