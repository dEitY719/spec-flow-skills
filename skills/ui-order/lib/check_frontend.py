#!/usr/bin/env python3
"""Read-only scanner for spec-flow:ui-order --check.

    check_frontend.py [--project <dir>]

Scans the project's frontend sources (*.tsx *.jsx *.ts *.js *.vue *.svelte
*.css *.scss *.html; skipping SKIP_DIRS, *.min.*, *.test.*, *.spec.*) for vague
or drifting UI criteria and prints one finding per line, sorted (severity,
check, file, line):

    CHECK_ID|severity|file:line|detail

severity: high | med | low | info. info lines are facts for the agent's
judgment (data-view candidates, order-block facts, value inventories) and are
not counted as findings. Line 0 means the whole file. Last line:

    [OK] spec-flow:ui-order check target=<dir> files=<n> findings=<n> high=<n> med=<n> low=<n>

Writes nothing, ever. Exit codes: 0 report printed (findings included), 1 I/O
error, 2 usage error. Stack detection and the ui-order marker logic are shared
with setup_claude_md.py. Self-check: tests/ui-order-check.sh.
"""

import argparse
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import setup_claude_md as setup  # noqa: E402  (shared detect / markers / project_dir)

EXTS = (".tsx", ".jsx", ".ts", ".js", ".vue", ".svelte", ".css", ".scss", ".html")
STYLE_EXTS = (".css", ".scss")
SKIP_DIRS = {"node_modules", ".git", "dist", "build", ".next", "out", "coverage",
             "vendor", ".nuxt", ".svelte-kit", ".output", "e2e", "__tests__"}
TEST_RE = re.compile(r"\.(test|spec)\.")  # tests quote UI text; they are not UI
SEV = {"high": 0, "med": 1, "low": 2, "info": 3}

# Pictographic codepoints, built numerically so this file holds no emoji literal.
EMOJI_RANGES = ((0x1F000, 0x1FAFF), (0x2600, 0x27BF), (0x2B50, 0x2B50), (0x2B55, 0x2B55))


def is_emoji(ch):
    cp = ord(ch)
    return any(lo <= cp <= hi for lo, hi in EMOJI_RANGES)


ICON_LIBS = ("react-icons", "@heroicons/", "heroicons", "@mui/icons-material",
             "@fortawesome/", "font-awesome", "fontawesome", "@tabler/icons",
             "phosphor", "@radix-ui/react-icons", "feather-icons", "react-feather",
             "vue-feather", "bootstrap-icons", "material-symbols", "material-icons",
             "@iconify/", "ionicons", "@ant-design/icons", "@primer/octicons",
             "remixicon", "boxicons", "@vicons/", "~icons/")
SPEC_RE = re.compile(r"""(?:\bfrom|\bimport|\brequire\(|@import|\bhref=|\bsrc=)\s*\(?\s*(?:url\()?['"]([^'"]+)['"]""")

SIDES = r"(?:-?(?:top|right|bottom|left|inline|block)(?:-?(?:start|end))?)?"
CSS_SPACE_RE = re.compile(r"\b(padding|margin|gap|row-?gap|column-?gap)" + SIDES + r"\s*:\s*([^;}\n]+)", re.I)
TW_SPACE_RE = re.compile(r"(?<![\w-])-?((?:p|m)[xytrblse]?|gap(?:-[xy])?|space-[xy])-\[([^\]\s]+)\]")
TW_RADIUS_RE = re.compile(r"""(?<![\w:-])(rounded(?:-(?:tl|tr|br|bl|ss|se|es|ee|t|r|b|l|s|e))?"""
                          r"""(?:-(?:none|xs|sm|md|lg|xl|2xl|3xl|4xl|full|\[[^\]\s]+\]))?)(?=["'`\s])""")
CSS_RADIUS_RE = re.compile(r"\bborder(?:-[a-z]+)*-?radius\s*:\s*([^;}\n,]+)", re.I)
HEX_RE = re.compile(r"(?<![\w&])#(?:[0-9a-fA-F]{8}|[0-9a-fA-F]{6}|[0-9a-fA-F]{3,4})\b")
FUNC_COLOR_RE = re.compile(r"\b(?:rgba?|hsla?)\((?!\s*var\()")
TOKEN_DEF_RE = re.compile(r"--[\w-]+\s*:[^;}]*")  # custom-property definitions are the tokens
MEDIA_RE = re.compile(r"@media[^{]*")
MEDIA_W_RE = re.compile(r"(?:(?:min|max)-width\s*:\s*|width\s*[<>]=?\s*)(\d+(?:\.\d+)?)(px|em|rem)")
TW_BP_RE = re.compile(r"(?<![\w-])(?:min|max)-\[(\d+(?:\.\d+)?)(px|em|rem)\]:")
SCREENS_RE = re.compile(r"screens\s*:\s*\{([^}]*)\}")
SCREEN_W_RE = re.compile(r"""['"](\d+(?:\.\d+)?)(px|em|rem)['"]""")
PX_RE = re.compile(r"(-?\d+(?:\.\d+)?)px")
DATA_SIGNALS = [("fetch", r"\bfetch\("), ("axios", r"\baxios\b"),
                ("useQuery", r"\buse(?:Suspense|Infinite)?Query\b"), ("useSWR", r"\buseSWR\b"),
                ("load", r"\bexport\s+(?:async\s+)?(?:function\s+load\b|const\s+load\b)"),
                ("async-component", r"\bexport\s+default\s+async\s+function\b")]
STATE_HINTS = [("loading", r"isLoading|isPending|loading|Skeleton|Spinner|<Suspense|\{#await"),
               ("empty", r"\.length\s*===?\s*0|!\w+\.length|isEmpty|EmptyState|no results|:else"),
               ("error", r"isError|\berror\b|\bcatch\b|ErrorBoundary|error\.tsx")]


def open_tag_end(text, i):
    """Index just past the '>' closing the tag opened at text[i] == '<'."""
    depth, quote = 0, None
    for k in range(i + 1, len(text)):
        c = text[k]
        if quote:
            if c == quote:
                quote = None
        elif c in "\"'`":
            quote = c
        elif c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
        elif c == ">" and depth <= 0:
            return k + 1
    return len(text)


def px(num, unit):
    v = float(num) * (16 if unit in ("em", "rem") else 1)
    return int(v) if v == int(v) else v


class Scan:
    def __init__(self):
        self.out = []
        self.radius = {}   # value -> [count, first (file, line)]
        self.widths = {}   # px -> first (file, line)
        self.uses_icons = False

    def add(self, check, sev, f, line, detail):
        self.out.append((SEV[sev], check, f, line, sev, detail))

    def file(self, rel, text):
        ext = os.path.splitext(rel)[1]
        low = rel.lower()
        lines = text.split("\n")
        lineno = lambda pos: text.count("\n", 0, pos) + 1  # noqa: E731
        style = ext in STYLE_EXTS
        themeish = ("tailwind.config" in low or "theme" in low or "tokens" in low)

        # 1. spacing (per line, worst severity) + radius inventory
        for n, ln in enumerate(lines, 1):
            bad, sev = [], None
            for m in TW_SPACE_RE.finditer(ln):
                v = PX_RE.fullmatch(m.group(2))
                off4 = not v or float(v.group(1)) % 4
                bad.append(m.group(0))
                sev = "med" if off4 or sev == "med" else "low"
            for m in CSS_SPACE_RE.finditer(ln):
                for v in PX_RE.findall(m.group(2)):
                    x = abs(float(v))
                    if x % 8:
                        bad.append(f"{m.group(1)}:{v}px")
                        sev = "med" if x % 4 or sev == "med" else (sev or "low")
            if bad:
                self.add("token-spacing", sev, rel, n,
                         " ".join(bad) + " -> spacing token (8의 배수: 4/8/16/24/40)")
            if not themeish:
                for m in TW_RADIUS_RE.finditer(ln):
                    self._radius(m.group(1), rel, n)
                for m in CSS_RADIUS_RE.finditer(ln):
                    v = m.group(1).strip().strip("'\"")
                    if not v.startswith("var("):
                        self._radius(v, rel, n)

        # 2. hard-coded colors, one finding per file
        if not themeish:
            bare = [TOKEN_DEF_RE.sub("", ln) for ln in lines]
            hits = [n for n, ln in enumerate(bare, 1)
                    for _ in HEX_RE.findall(ln) + FUNC_COLOR_RE.findall(ln)]
            if hits:
                self.add("color-hardcode", "med", rel, hits[0],
                         f"{len(hits)} color literal(s) -> color role token (primary/surface/muted/semantic)")

        # 3. a11y
        if not style:
            for m in re.finditer(r"<(button|Button)\b", text):
                end = open_tag_end(text, m.start())
                attrs = text[m.start():end]
                close = text.find(f"</{m.group(1)}>", end)
                if attrs.endswith("/>") or close < 0 or re.search(r"\b(aria-label|aria-labelledby|title)\s*=", attrs):
                    continue
                body = text[end:close]
                rest = re.sub(r"<svg\b.*?</svg>", "", body, flags=re.S)
                rest = re.sub(r"<[A-Z][\w.]*\b[^<]*?/>", "", rest, flags=re.S)
                emo = any(is_emoji(c) for c in rest)
                rest = "".join(c for c in rest if not is_emoji(c) and c != chr(0xFE0F)).strip()
                if not rest and body.strip():
                    self.add("a11y-icon-button", "high", rel, lineno(m.start()),
                             "icon-only button without aria-label" + (" (emoji)" if emo else "")
                             + " -> 아이콘 버튼 aria-label")
            for m in re.finditer(r"<img\b", text):
                attrs = text[m.start():open_tag_end(text, m.start())]
                if not re.search(r"\balt\s*=", attrs):
                    self.add("a11y-img-alt", "med", rel, lineno(m.start()),
                             "<img> without alt -> 대체 텍스트 alt (장식이면 alt=\"\")")
        for m in re.finditer(r"(?<![\w:-])outline-none\b|\boutline\s*:\s*['\"]?(?:none|0)\b", text):
            if m.group(0).startswith("outline-none"):
                s = text.rfind("<", 0, m.start())
                e = open_tag_end(text, s) if s >= 0 else -1
                if s < 0 or e < m.start():  # not inside a tag: fall back to the line
                    s, e = text.rfind("\n", 0, m.start()) + 1, text.find("\n", m.start())
            else:  # CSS rule or style object: from the rule's '{' to its '}'
                s = text.rfind("}", 0, m.start()) + 1
                e = text.find("}", m.start())
            ctx = text[s:e if e >= 0 else len(text)]
            if "focus-visible" not in ctx:
                self.add("a11y-focus", "med", rel, lineno(m.start()),
                         f"{m.group(0).strip()} without focus-visible -> 포커스 링 (focus-visible)")

        # 4. icon set: Lucide only; emoji icons discouraged
        for n, ln in enumerate(lines, 1):
            for spec in SPEC_RE.findall(ln):
                lib = next((x for x in ICON_LIBS if x in spec), None)
                if lib:
                    self.uses_icons = True
                    pkg = {".vue": "lucide-vue-next", ".svelte": "lucide-svelte"}.get(ext, "lucide-react")
                    self.add("icon-set", "high", rel, n,
                             f"{spec} -> replace with the Lucide equivalent ({pkg}); one icon set only")
            if not style and not re.match(r"\s*(//|/\*|\*|<!--)", ln):
                emo = sorted({f"U+{ord(c):04X}" for c in ln if is_emoji(c)})
                if emo:
                    self.uses_icons = True
                    self.add("icon-emoji", "med", rel, n,
                             " ".join(emo) + " -> use a Lucide icon instead of emoji")
        if "<svg" in text:
            self.uses_icons = True

        # 5. breakpoint inventory
        for m in MEDIA_RE.finditer(text):
            for w in MEDIA_W_RE.findall(m.group(0)):
                self.widths.setdefault(px(*w), (rel, lineno(m.start())))
        for m in TW_BP_RE.finditer(text):
            self.widths.setdefault(px(m.group(1), m.group(2)), (rel, lineno(m.start())))
        if "tailwind.config" in low:
            for m in SCREENS_RE.finditer(text):
                for w in SCREEN_W_RE.findall(m.group(1)):
                    self.widths.setdefault(px(*w), (rel, lineno(m.start())))

        # 6. data-view candidates for the agent's exception-state judgment
        if not style:
            sig = [(lineno(m.start()), name) for name, rx in DATA_SIGNALS
                   for m in [re.search(rx, text)] if m]
            if sig:
                seen = [k for k, rx in STATE_HINTS if re.search(rx, text)]
                self.add("data-view-candidate", "info", rel, min(sig)[0],
                         "signals=" + ",".join(sorted(n for _, n in sig))
                         + " states-seen=" + (",".join(seen) or "none"))

    def _radius(self, v, f, n):
        r = self.radius.setdefault(v, [0, (f, n)])
        r[0] += 1

    def finish(self, chosen):
        if self.radius:
            first = min(r[1] for r in self.radius.values())
            inv = ", ".join(f"{v} x{c}" for v, (c, _) in sorted(self.radius.items(), key=lambda kv: (-kv[1][0], kv[0])))
            if len(self.radius) >= 4:
                self.add("token-radius", "med", *first,
                         f"{len(self.radius)} distinct radius values: {inv} -> radius token 1-2개로 통일")
            else:
                self.add("token-radius", "info", *first, f"radius values: {inv}")
        if self.widths:
            custom = sorted(w for w in self.widths if w not in chosen)
            first = min(self.widths.values())
            allw = "/".join(str(w) for w in sorted(self.widths))
            if len(custom) >= 3:
                self.add("breakpoints", "med", *first,
                         f"{len(custom)} widths beyond {'/'.join(map(str, sorted(chosen)))}: "
                         + "/".join(map(str, custom)) + " -> 브레이크포인트 2-3개로 통일")
            else:
                self.add("breakpoints", "info", *first, f"breakpoint widths: {allw}")


def order_block(root, scan):
    """Order-block facts; returns the breakpoint set the block chose (or the default)."""
    chosen = {640, 1024}
    try:
        with open(os.path.join(root, "CLAUDE.md"), "rb") as f:
            data = f.read()
    except FileNotFoundError:
        data = b""
    try:
        span = setup.block_span(data)
    except ValueError as e:
        scan.add("order-unconfirmed", "med", "CLAUDE.md", 0, f"{e} -> fix by hand")
        return chosen
    if span is None:
        scan.add("order-unconfirmed", "med", "CLAUDE.md", 0,
                 "no ui-order block -> /spec-flow:ui-order --setup --apply")
        return chosen
    base = data[:span[0]].count(b"\n") + 1
    block = data[span[0]:span[1]].decode("utf-8", "replace").split("\n")
    defaults = 0
    for k, ln in enumerate(block):
        defaults += ln.count("(기본값)")
        if ln.startswith("[화면]") and re.search(r"<[^>]+>", ln):
            scan.add("order-unconfirmed", "med", "CLAUDE.md", base + k,
                     "[화면] is still the <...> placeholder -> 이 프로젝트의 화면 종류로 확정")
        if ln.startswith("[반응형]"):
            ws = {int(w) for w in re.findall(r"\b(\d{3,4})\b", ln)}
            chosen = ws or chosen
    scan.add("order-block", "info", "CLAUDE.md", base, f"present, {defaults} (기본값) value(s) to verify against the code")
    return chosen


def main():
    ap = argparse.ArgumentParser(prog="check_frontend.py")
    ap.add_argument("--project")
    a = ap.parse_args()
    root = setup.project_dir(a.project)
    if not os.path.isdir(root):
        print(f"[FAIL] spec-flow:ui-order check: project dir not found: {root}", file=sys.stderr)
        sys.exit(1)

    scan, nfiles = Scan(), 0
    try:
        for d, dirs, files in os.walk(root):
            dirs[:] = sorted(x for x in dirs if x not in SKIP_DIRS)
            for name in sorted(files):
                if not name.endswith(EXTS) or ".min." in name or TEST_RE.search(name):
                    continue
                path = os.path.join(d, name)
                with open(path, encoding="utf-8", errors="replace") as f:
                    text = f.read()
                nfiles += 1
                scan.file(os.path.relpath(path, root).replace(os.sep, "/"), text)
        chosen = order_block(root, scan)
    except OSError as e:
        print(f"[FAIL] spec-flow:ui-order check: {e}", file=sys.stderr)
        sys.exit(1)
    scan.finish(chosen)
    if scan.uses_icons and not setup.detect(root)["lucide"]:
        scan.add("icon-set", "low", "package.json", 0,
                 "icons used but no Lucide dependency -> add lucide-react (or lucide-vue-next / lucide-svelte)")

    counts = {"high": 0, "med": 0, "low": 0}
    for _, check, f, line, sev, detail in sorted(scan.out):
        print(f"{check}|{sev}|{f}:{line}|{detail}")
        if sev in counts:
            counts[sev] += 1
    print(f"[OK] spec-flow:ui-order check target={root} files={nfiles} "
          f"findings={sum(counts.values())} high={counts['high']} med={counts['med']} low={counts['low']}")


if __name__ == "__main__":
    main()
