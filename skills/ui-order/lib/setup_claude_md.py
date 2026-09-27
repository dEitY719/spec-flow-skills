#!/usr/bin/env python3
"""Setup helper for spec-flow:ui-order --setup.

    setup_claude_md.py [--apply] [--force] [--project <dir>]

Detects the project's UI stack and inserts the ui-order block (UI 요청 규칙 +
화면 주문서 프로젝트 기본값) into <dir>/CLAUDE.md, between the markers

    <!-- ui-order:begin -->
    <!-- ui-order:end -->

This file is the single source of that block's text; the skill guide keeps a
copy for manual users only.

Default is a dry-run: print the target, its marker state and the block, write
nothing. --apply writes. A symlinked CLAUDE.md (commonly -> AGENTS.md) is
written through to its resolved file; the link itself is kept. A missing file
is created holding only the block. An existing block is skipped unless
--force, which replaces only the bytes between the markers. Bytes outside the
markers are never touched.

Last line of stdout is a machine-readable summary:

    [OK] spec-flow:ui-order setup target=<path> stack=<...> action=<action>

action: would-create | would-append | would-replace | skip | created |
appended | replaced.

Exit codes: 0 ok (skip included), 1 malformed markers or I/O error (nothing
written), 2 usage error. Self-check: tests/ui-order-setup.sh.
"""

import argparse
import glob
import json
import os
import re
import subprocess
import sys

BEGIN = b"<!-- ui-order:begin -->"
END = b"<!-- ui-order:end -->"
# Markers count only as whole lines, so prose quoting them inline is not a block.
BEGIN_RE = re.compile(rb"^" + re.escape(BEGIN) + rb"\r?$", re.M)
END_RE = re.compile(rb"^" + re.escape(END) + rb"\r?$", re.M)
D = " (기본값)"

RULES = """## UI 요청 규칙
UI 요청이 모호하면 바로 구현하지 말고 `/spec-flow:ui-order` 절차로 먼저 되묻는다.
모호한 요청 = 부품 이름·숫자·상태가 빠진 요청 (예: "버튼 만들어줘", "예쁘게", "폰에서도 되게").
되물을 항목: 위계(primary/secondary/ghost/destructive) · 크기·여백(padding, radius) ·
상태(hover/focus-visible/disabled/loading) · 예외 화면(로딩/빈/에러) · 반응형(브레이크포인트).
"기본값으로 진행"이라고 답하면 ui-order 기본값으로 구현하고, 적용한 기본값을 밝힌다.
"""

# Checklist defaults (references/checklist.md), one line per bracket.
BRACKETS = [
    ("화면", "<이 프로젝트의 화면 종류: 예) 대시보드 + 목록-상세 + 설정>"),
    ("레이아웃", "상단 56px 앱 바 + 좌측 240px 고정 사이드바 + 본문. 컨테이너 max-width 1200px." + D),
    ("내용", "카드 그리드(데스크톱 3열 / 태블릿 2열 / 모바일 1열, gap 16px), 비교·정렬 데이터는 테이블." + D),
    ("부품", "화면당 primary 버튼 1개, 확인·삭제는 컨펌 다이얼로그, 완료 피드백은 토스트 3초." + D),
    ("상태", "로딩은 스켈레톤, 0건은 엠프티 스테이트(다음 행동 버튼 포함), 실패는 재시도 버튼이 있는 에러 상태." + D),
    ("토큰", "간격 8의 배수, 라운드 12px, 그림자 약하게, 글자 크기 4단계(Display/Heading/Body/Caption)." + D),
    ("글자", "본문 16px · 행간 1.6, 카드 제목은 2줄 line-clamp, 숫자 열은 tabular-nums." + D),
    ("반응형", "모바일 퍼스트, 브레이크포인트 640/1024. 1024px 미만에서 사이드바는 드로어로." + D),
    ("접근성", "포커스 링 유지, 명암비 4.5:1 이상, 터치 타깃 44px 이상, 아이콘 버튼에 aria-label." + D),
]

FRAMEWORKS = [("next", "Next.js"), ("nuxt", "Nuxt"), ("@sveltejs/kit", "SvelteKit"),
              ("react", "React"), ("vue", "Vue"), ("svelte", "Svelte")]
LIBS = [("@mui/material", "MUI"), ("antd", "Ant Design"),
        ("@fluentui/react-components", "Fluent UI")]
LUCIDE = ("lucide-react", "lucide-vue-next", "lucide-svelte", "lucide")


def detect(project):
    """Return the detected stack as a dict of display names (absent = not found)."""
    deps = {}
    try:
        with open(os.path.join(project, "package.json"), encoding="utf-8") as f:
            pkg = json.load(f)
        for key in ("dependencies", "devDependencies"):
            deps.update(pkg.get(key) or {})
    except (OSError, ValueError):
        pass  # no or unreadable package.json -> all defaults
    s = {}
    s["framework"] = next((n for k, n in FRAMEWORKS if k in deps), None)
    s["tailwind"] = "tailwindcss" in deps or bool(glob.glob(os.path.join(project, "tailwind.config.*")))
    s["shadcn"] = os.path.isfile(os.path.join(project, "components.json"))
    s["lib"] = next((n for k, n in LIBS if k in deps), None)
    s["lucide"] = any(k in deps for k in LUCIDE)
    return s


def stack_summary(s):
    parts = [s["framework"], "Tailwind" if s["tailwind"] else None,
             "shadcn/ui" if s["shadcn"] else None, s["lib"], "Lucide" if s["lucide"] else None]
    return ",".join(p.replace(" ", "-") for p in parts if p) or "none"


def build_block(s):
    ui = [p for p in ("Tailwind" if s["tailwind"] else None,
                      "shadcn/ui" if s["shadcn"] else None, s["lib"]) if p]
    stack = [s["framework"]] if s["framework"] else []
    stack.append(" + ".join(ui) if ui else "Tailwind + shadcn/ui" + D)
    stack.append("아이콘 Lucide" if s["lucide"] else "아이콘 Lucide outline 20px" + D)
    stack.append("미니멀 스타일, 라이트/다크 모드 둘 다" + D)
    lines = [f"[{k}]{' ' * max(1, 9 - 2 * len(k))}{v}" for k, v in BRACKETS]
    if s["lib"]:  # a component library owns the tokens; follow it
        lines[5] = f"[토큰]     {s['lib']} 테마 토큰을 따른다."
    inner = (RULES + "\n## 화면 주문서 (프로젝트 기본값)\n" + "\n".join(lines) + "\n"
             + "스택: " + ", ".join(stack) + ".\n"
             + "화면 단위 작업은 와이어프레임 먼저 → 스크린샷 확인 → 스타일 입히기." + D + "\n")
    return inner.encode("utf-8")


def block_span(data):
    """Byte span (i, j) of the ui-order block's inner text, None when absent.

    Raises ValueError(msg) on malformed markers. Shared with check_frontend.py.
    """
    bs, es = list(BEGIN_RE.finditer(data)), list(END_RE.finditer(data))
    nb, ne = len(bs), len(es)
    if nb == 0 and ne == 0:
        return None
    if nb == 1 and ne == 1 and bs[0].start() < es[0].start():
        return bs[0].start() + len(BEGIN), es[0].start()
    raise ValueError(f"malformed ui-order markers (begin={nb}, end={ne})")


def project_dir(arg):
    if arg:
        return os.path.abspath(arg)
    try:
        out = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True,
                             text=True, check=True).stdout.strip()
        if out:
            return out
    except (OSError, subprocess.CalledProcessError):
        pass
    return os.getcwd()


def fail(msg):
    print(f"[FAIL] spec-flow:ui-order setup: {msg}", file=sys.stderr)
    sys.exit(1)


def main():
    ap = argparse.ArgumentParser(prog="setup_claude_md.py")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--project")
    a = ap.parse_args()

    proj = project_dir(a.project)
    if not os.path.isdir(proj):
        fail(f"project dir not found: {proj}")
    link = os.path.join(proj, "CLAUDE.md")
    real = os.path.realpath(link)
    s = detect(proj)
    inner = build_block(s)

    try:
        with open(real, "rb") as f:
            old = f.read()
        exists = True
    except FileNotFoundError:
        old, exists = b"", False
    except OSError as e:
        fail(f"cannot read {real}: {e}")

    try:
        span = block_span(old)
    except ValueError as e:
        fail(f"{e} in {real}; fix them by hand, nothing written")
    present = span is not None

    if not present:
        sep = b"" if not old else (b"" if old.endswith(b"\n") else b"\n") + b"\n"
        new = old + sep + BEGIN + b"\n" + inner + END + b"\n"
        action = "appended" if exists else "created"
    elif a.force:
        i, j = span
        new = old[:i] + b"\n" + inner + old[j:]
        action = "replaced"
    else:
        new, action = None, "skip"

    shown = real if real == link else f"{link} -> {real}"
    print(f"target: {shown}")
    print(f"block: {'present' if present else 'absent'}{'' if exists else ' (file missing)'}")
    if action == "skip":
        print("ui-order block already present; re-run with --force to replace it.")
    elif not a.apply:
        action = {"appended": "would-append", "created": "would-create",
                  "replaced": "would-replace"}[action]
        print("--- block (dry-run, nothing written) ---")
        sys.stdout.write((BEGIN + b"\n" + inner + END + b"\n").decode("utf-8"))
        print("--- re-run with --apply to write ---")
    else:
        try:
            with open(real, "wb") as f:
                f.write(new)
        except OSError as e:
            fail(f"cannot write {real}: {e}")
    print(f"[OK] spec-flow:ui-order setup target={real} stack={stack_summary(s)} action={action}")


if __name__ == "__main__":
    main()
