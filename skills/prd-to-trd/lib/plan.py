#!/usr/bin/env python3
"""Round-trip helper for spec-flow:prd-to-trd.

Two deterministic halves of the `--apply` path, which used to live only as
prose in SKILL.md Step 4:

    plan.py parse <plan.md>
        Validate the round-trip invariants of `references/plan-format.md` and
        print the Components table as a JSON array of
        {slug, f_items, d_items, nf_primary, nf_cited, adjacent}.
        A violated invariant exits 1 naming the offending line number.

    plan.py render --rows <json|-> --template <path> --out-dir <dir> --prd <path>
        Substitute the `{{...}}` placeholders of
        `references/template-fallback.md` from those rows and write one
        scaffold per slug. Existing files are skipped unless --force.
        Prints `written=<n> skipped=<n>`.

The parser is the reason this file exists: `--apply` reads the plan, not the
PRD, so a silent mis-parse would write the wrong frontmatter into every
scaffold. Self-check: tests/prd-to-trd-plan.sh.
"""

import argparse
import datetime
import json
import pathlib
import re
import sys

COLUMNS = ["Slug", "책임 F-#", "책임 D-#", "NF-# (primary)", "NF-# (cited)", "인접 TRD"]
HEADER_FIELDS = ["Generated:", "Source PRD:", "PRD directory:", "Mode:", "Template:"]
SECTIONS = ["## Components", "## Suggested splits", "## Manual review"]
NONE = "(none)"
SLUG_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
# Shape only. Whether F-7 exists in the PRD is deliberately NOT checked here:
# constraints.md -> "Plan is the SSOT" makes --apply read the plan, not the PRD.
# A malformed id ("F7", "NF-", "X-1") is a typo the parser can and does catch.
ITEM_RE = {"F": re.compile(r"^F-\d+$"), "D": re.compile(r"^D-\d+$"), "NF": re.compile(r"^NF-\d+$")}
PLACEHOLDER_RE = re.compile(r"\{\{([A-Za-z0-9_-]+)\}\}")
FRONTMATTER_SLOTS = ["상태", "책임 PRD 항목", "인용 NF", "소유자", "인접 TRD"]


class PlanError(Exception):
    """A round-trip invariant violation, carrying the offending line number."""

    def __init__(self, line, message):
        super().__init__(message)
        self.line = line
        self.message = message


def _cells(row):
    """Split a markdown table row into its cells (leading/trailing pipe dropped)."""
    return [c.strip() for c in row.strip().strip("|").split("|")]


def _items(cell, line, column, kind=None):
    """`(none)` sentinel -> [], otherwise comma-separated items, shape-checked."""
    if cell == NONE:
        return []
    if not cell:
        raise PlanError(line, f"{column} is blank — use the {NONE} sentinel, never an empty cell")
    items = [x.strip() for x in cell.split(",") if x.strip()]
    if kind:
        bad = [x for x in items if not ITEM_RE[kind].match(x)]
        if bad:
            raise PlanError(line, f"{column} holds malformed PRD item id(s) {bad} — expected {kind}-<n>")
    return items


def parse(path):
    text = pathlib.Path(path).read_text(encoding="utf-8")
    lines = text.splitlines()

    # Header block: the five fields, in order, before `## Components`.
    seen_at = -1
    for field in HEADER_FIELDS:
        for i, line in enumerate(lines):
            if line.startswith(field):
                if i <= seen_at:
                    raise PlanError(i + 1, f"header field {field!r} is out of order")
                seen_at = i
                break
        else:
            raise PlanError(1, f"plan header is missing {field!r}")

    # The three sections, in order.
    at = {}
    for section in SECTIONS:
        try:
            at[section] = lines.index(section)
        except ValueError:
            raise PlanError(1, f"plan is missing the {section!r} section") from None
    order = [at[s] for s in SECTIONS]
    if order != sorted(order):
        raise PlanError(order[0] + 1, f"sections must appear in the order {SECTIONS}")
    if at[SECTIONS[0]] < seen_at:
        raise PlanError(at[SECTIONS[0]] + 1, "## Components must follow the header block")

    body = lines[at[SECTIONS[0]] + 1 : at[SECTIONS[1]]]
    offset = at[SECTIONS[0]] + 2  # 1-based line number of body[0]
    table = [(offset + i, ln) for i, ln in enumerate(body) if ln.strip().startswith("|")]
    if len(table) < 3:
        raise PlanError(offset, "## Components has no table rows")

    head_line, head = table[0]
    if _cells(head) != COLUMNS:
        raise PlanError(head_line, f"table header must be exactly {COLUMNS}, got {_cells(head)}")
    sep_line, sep = table[1]
    if not all(set(c) <= set("-: ") and c for c in _cells(sep)):
        raise PlanError(sep_line, "row 2 of the Components table must be the `|---|` separator")

    rows = []
    slugs = set()
    for line, raw in table[2:]:
        cells = _cells(raw)
        if len(cells) != len(COLUMNS):
            raise PlanError(line, f"expected {len(COLUMNS)} columns, got {len(cells)}")
        slug = cells[0]
        if not SLUG_RE.match(slug):
            raise PlanError(line, f"slug {slug!r} is not kebab-case")
        if slug in slugs:
            raise PlanError(line, f"duplicate slug {slug!r} — one row per slug")
        slugs.add(slug)
        nf_primary = _items(cells[3], line, COLUMNS[3], "NF")
        if len(nf_primary) > 1:
            raise PlanError(line, f"NF-# (primary) holds at most one item, got {nf_primary}")
        rows.append(
            {
                "slug": slug,
                "f_items": _items(cells[1], line, COLUMNS[1], "F"),
                "d_items": _items(cells[2], line, COLUMNS[2], "D"),
                "nf_primary": nf_primary[0] if nf_primary else None,
                "nf_cited": _items(cells[4], line, COLUMNS[4], "NF"),
                "adjacent": _items(cells[5], line, COLUMNS[5]),
                # The plan has no title column, so the default is the
                # title-cased slug. Edit this field before `render` when the
                # component name is an acronym (ci-gate -> "CI Gate").
                "title": _default_title(slug),
                "_line": line,
            }
        )

    for row in rows:
        for other in row["adjacent"]:
            if other not in slugs:
                raise PlanError(row["_line"], f"인접 TRD {other!r} is not a slug in this plan")
        del row["_line"]
    return rows


def _template_body(path):
    """A project `_template.md` is used raw; the bundled fallback's fenced block is extracted."""
    text = pathlib.Path(path).read_text(encoding="utf-8")
    if "## Verbatim template" in text:
        after = text.split("## Verbatim template", 1)[1]
        m = re.search(r"^```[a-z]*\n(.*?)^```", after, re.S | re.M)
        if not m:
            sys.exit(f"[FAIL] {path}: '## Verbatim template' has no fenced block")
        text = m.group(1)
    # A project template is the SSOT and may legitimately differ, so drift from
    # the agent-toolbox 8-section standard warns rather than fails — but it is
    # never silent: an unnoticed 9th section lands in every scaffold it renders.
    sections = len(re.findall(r"^## \d+\. ", text, re.M))
    slots = [s for s in FRONTMATTER_SLOTS if f"**{s}**" not in text]
    if sections != 8 or slots:
        print(f"[WARN] {path}: {sections} numbered sections (expected 8)"
              + (f", missing frontmatter slot(s) {slots}" if slots else "")
              + " — see references/template-fallback.md", file=sys.stderr)
    return text


def _project_name(prd_path, override):
    if override:
        return override
    for line in pathlib.Path(prd_path).read_text(encoding="utf-8").splitlines():
        if line.startswith("# "):
            title = re.sub(r"^#\s*(PRD:)?\s*", "", line)
            return re.sub(r"\s*\([^()]*\)\s*$", "", title).strip()
    sys.exit(f"[FAIL] {prd_path}: no `# ` title to derive the project name from — pass --project")


def _default_title(slug):
    return " ".join(w.capitalize() for w in slug.split("-"))


def render(rows, template, out_dir, prd, project, force):
    body = _template_body(template)
    project = _project_name(prd, project)
    prd_basename = pathlib.Path(prd).name
    today = datetime.date.today().isoformat()
    out = pathlib.Path(out_dir)
    done = []

    def abort(reason):
        # SKILL.md Step 4: report the slugs written so far, then [FAIL].
        # No auto-rollback — the written scaffolds stay on disk.
        print(f"[INFO] written so far: {', '.join(done) or '(none)'}")
        sys.exit(f"[FAIL] spec-flow:prd-to-trd {reason}")

    try:
        out.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        abort(str(e))

    written = skipped = 0
    for row in rows:
        # The rows JSON is hand-editable between `parse` and `render`, so this
        # is not a re-check of parse's work: it is the only guard on the write
        # path. constraints.md -> "Never write outside <prd-dir>/trd/".
        if not SLUG_RE.match(str(row.get("slug", ""))):
            abort(f"slug {row.get('slug')!r} is not kebab-case — refusing to write outside {out}")
        target = out / f"{row['slug']}.md"
        # A symlink here writes through to wherever it points, which defeats
        # the kebab-case guard above: `--force` would clobber a file outside
        # `out`. Refuse rather than resolve — nothing legitimately symlinks a
        # scaffold. (codex review, PR #9)
        if target.is_symlink():
            abort(f"{target} is a symlink — refusing to write outside {out}")
        if target.exists() and not force:
            print(f"[INFO] skip existing: {target}")
            skipped += 1
            continue
        responsible = row["f_items"] + row["d_items"]
        if row["nf_primary"]:
            responsible.append(row["nf_primary"])
        values = {
            "component-title": row.get("title") or _default_title(row["slug"]),
            "project-name": project,
            "iso-date": today,
            "responsible-prd-items": ", ".join(responsible) or NONE,
            "prd-basename": prd_basename,
            "cited-nf-items": ", ".join(row["nf_cited"]) or NONE,
            "owner-placeholder": "<github-handle-placeholder>",
            "adjacent-trd-slugs": ", ".join(row["adjacent"]) or NONE,
        }
        text = PLACEHOLDER_RE.sub(lambda m: values.get(m.group(1), m.group(0)), body)
        left = PLACEHOLDER_RE.findall(text)
        if left:
            abort(f"{target}: unsubstituted placeholder(s) {sorted(set(left))}")
        try:
            target.write_text(text, encoding="utf-8")
        except OSError as e:
            abort(f"{target}: {e}")
        done.append(row["slug"])
        written += 1
    print(f"written={written} skipped={skipped}")


def main(argv=None):
    ap = argparse.ArgumentParser(prog="plan.py", description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("parse", help="validate a plan and print its Components rows as JSON")
    p.add_argument("plan")

    r = sub.add_parser("render", help="write one TRD scaffold per row")
    r.add_argument("--rows", required=True, help="JSON file of parse output, or - for stdin")
    r.add_argument("--template", required=True)
    r.add_argument("--out-dir", required=True)
    r.add_argument("--prd", required=True, help="source PRD path; supplies the relative link target")
    r.add_argument("--project", default=None, help="override the PRD-title-derived project name")
    r.add_argument("--force", action="store_true", help="overwrite an existing scaffold")

    args = ap.parse_args(argv)
    if args.cmd == "parse":
        try:
            print(json.dumps(parse(args.plan), ensure_ascii=False, indent=2))
        except PlanError as e:
            sys.exit(f"[FAIL] {args.plan}:{e.line}: {e.message}")
        except OSError as e:
            sys.exit(f"[FAIL] {e}")
        return
    raw = sys.stdin.read() if args.rows == "-" else pathlib.Path(args.rows).read_text(encoding="utf-8")
    render(json.loads(raw), args.template, args.out_dir, args.prd, args.project, args.force)


if __name__ == "__main__":
    main()
