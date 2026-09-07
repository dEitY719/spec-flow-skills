#!/usr/bin/env python3
"""Deterministic half of the spec-flow:trd-to-issues `--apply` path.

Two subcommands, both of which used to live only as prose in
references/bulk-create-procedure.md:

    apply_plan.py parse <plan.md>
        Validate the round-trip invariants of references/plan-format.md and
        print the plan as JSON:
        {"target_repo": ..., "milestones": [{"name", "summary", "description",
         "tasks": [{"id", "title", "labels", "depends_on", "ac"}]}],
         "failures": [...]}
        A violated invariant exits 1 naming the offending line number.
        Nothing is skipped silently: a `Depends on:` citation no task
        declares, and any line outside the skeleton, both fail here —
        before `--apply` has created anything to roll back.

    apply_plan.py resolve --rows <json|-> --map <json|->
        Rewrite every `#new-N` citation to the real issue number created by
        `gh issue create` and print one row per task:
        [{"id", "number", "milestone", "title", "labels", "body"}]
        A `#new-N` with no entry in the map exits 1 naming it.

`resolve` is the reason this file exists. `--apply` creates the issues first
and patches their `Depends on:` lines second, with no rollback: a
mis-substituted `#new-N` files issues whose dependencies silently point at the
wrong numbers, and nothing downstream catches it. A real `#<number>` citation
against a pre-existing issue passes through untouched, per plan-format.md
"Depends on".

Self-check: tests/trd-to-issues-apply-plan.sh.
"""

import argparse
import json
import re
import sys

TITLE_LINE = "# TRD-to-Issues Plan"
HEADER_FIELDS = ["Generated:", "Source TRD:", "Source PRD:", "Target repo:", "Mode:"]
FAILURES_HEADING = "## Decomposition failures"
NO_FAILURES = "_no failures._"
TIER_LABELS = {"pro-friendly", "max-only"}
MAX_AC = 3

MILESTONE_RE = re.compile(r"^## Milestone: (?P<name>.+?) — (?P<summary>.+)$")
TASK_RE = re.compile(r"^- \[ \] #new-(?P<n>\d+) (?P<title>.+)$")
SUB_RE = re.compile(r"^  - (?P<key>Labels|Depends on|AC): ?(?P<value>.*)$")
AC_RE = re.compile(r"^    - \[ \] (?P<text>.+)$")
REF_RE = re.compile(r"^#(?P<ref>new-\d+|\d+)$")


class PlanError(Exception):
    """A round-trip invariant violation, carrying the offending line number."""

    def __init__(self, line, message):
        super().__init__(message)
        self.line = line
        self.message = message


def _refs(value, lineno):
    """`(none)` sentinel -> [], otherwise the comma-separated citation tokens."""
    value = value.strip()
    if value in ("", "(none)"):
        return []
    out = []
    for raw in value.split(","):
        m = REF_RE.match(raw.strip())
        if not m:
            raise PlanError(lineno, f"'Depends on' citation must be #new-N or #<number>: {raw.strip()!r}")
        out.append(m.group("ref"))
    return out


def _labels(value, lineno):
    labels = [p.strip() for p in value.split(",") if p.strip()]
    tiers = [l for l in labels if l in TIER_LABELS]
    if len(tiers) != 1:
        raise PlanError(lineno, f"Labels must carry exactly one of {sorted(TIER_LABELS)}, got {labels}")
    return labels


def parse(text):
    """Parse a plan into the JSON shape above, or raise PlanError."""
    lines = text.splitlines()
    if not lines or lines[0].rstrip() != TITLE_LINE:
        raise PlanError(1, f"plan must start with {TITLE_LINE!r}")

    header = {}
    for lineno, line in enumerate(lines, 1):
        if line.startswith(FAILURES_HEADING) or MILESTONE_RE.match(line):
            break
        for field in HEADER_FIELDS:
            if line.startswith(field):
                header[field] = line[len(field):].strip()
    missing = [f for f in HEADER_FIELDS if f not in header]
    if missing:
        raise PlanError(1, f"missing header field(s): {', '.join(missing)}")

    # '## Decomposition failures' is always the last, bottom-level section
    # (plan-format.md "Top-level structure") — splitting on it up front turns
    # per-line in-failures tracking into a plain slice, and doubles as the
    # "section present" check no separate pass needs to redo below.
    try:
        split_at = next(i for i, line in enumerate(lines) if line.startswith(FAILURES_HEADING))
    except StopIteration:
        raise PlanError(len(lines), f"missing '{FAILURES_HEADING}' section") from None

    milestones = []
    failures = []
    task = None
    mode = None  # None | "ac" | "description"
    expected_id = 1

    for lineno, line in enumerate(lines[:split_at], 1):
        m = MILESTONE_RE.match(line)
        if m:
            milestones.append({
                "name": m.group("name").strip(),
                "summary": m.group("summary").strip(),
                "description": "",
                "tasks": [],
            })
            task, mode = None, None
            continue

        if line.startswith("Description:"):
            if not milestones:
                raise PlanError(lineno, "'Description:' before any '## Milestone:' heading")
            milestones[-1]["description"] = line[len("Description:"):].strip()
            mode = "description"
            continue

        if mode == "description":
            # The description wraps over the following lines until a blank one.
            if line.strip() and not line.startswith(("-", "#")):
                milestones[-1]["description"] += " " + line.strip()
                continue
            mode = None

        m = TASK_RE.match(line)
        if m:
            if not milestones:
                raise PlanError(lineno, "task before any '## Milestone:' heading")
            got = int(m.group("n"))
            if got != expected_id:
                raise PlanError(lineno, f"#new-N must run 1..N in order; expected #new-{expected_id}, got #new-{got}")
            expected_id += 1
            task = {
                "id": f"new-{got}",
                "line": lineno,
                "title": m.group("title").strip(),
                "labels": None,
                "depends_on": None,
                "ac": [],
            }
            milestones[-1]["tasks"].append(task)
            mode = None
            continue

        m = SUB_RE.match(line)
        if m:
            if task is None:
                raise PlanError(lineno, f"'{m.group('key')}:' outside a task bullet")
            key, value = m.group("key"), m.group("value")
            if key == "Labels":
                task["labels"] = _labels(value, lineno)
            elif key == "Depends on":
                task["depends_on"] = _refs(value, lineno)
            else:
                if value.strip():
                    raise PlanError(lineno, "'AC:' takes no inline value; criteria are nested checkboxes")
                mode = "ac"
            continue

        m = AC_RE.match(line)
        if m:
            if mode != "ac":
                raise PlanError(lineno, "acceptance criterion outside an 'AC:' bullet")
            task["ac"].append(m.group("text").strip())
            continue

        # A criterion wrapped onto the next line: any indent deeper than the
        # `    - [ ] ` bullet it continues.
        if mode == "ac" and task and task["ac"] and line.strip() and line.startswith("     "):
            task["ac"][-1] += " " + line.strip()
            continue

        # Anything else inside a milestone is unrecognised. Refuse it rather
        # than skip it: the plan is the single review surface, and silently
        # dropping a hand-edited line is exactly the failure this parser
        # exists to prevent (PR #12 review, agy + codex BLOCKER).
        if milestones and line.strip():
            raise PlanError(lineno, f"line does not match the plan-format.md skeleton: {line.strip()[:60]!r}")

    for lineno, line in enumerate(lines[split_at + 1:], split_at + 2):
        if line.strip() and line.strip() != NO_FAILURES:
            if not line.startswith("- "):
                raise PlanError(lineno, "decomposition failures must be '- ' bullets")
            failures.append(line[2:].strip())

    if not milestones:
        raise PlanError(1, "no '## Milestone:' heading found")

    declared = {t["id"] for m in milestones for t in m["tasks"]}
    for milestone in milestones:
        for task in milestone["tasks"]:
            line = task.pop("line")
            if task["labels"] is None:
                raise PlanError(line, f"task #{task['id']} has no 'Labels:' bullet")
            if task["depends_on"] is None:
                raise PlanError(line, f"task #{task['id']} has no 'Depends on:' bullet")
            if not 1 <= len(task["ac"]) <= MAX_AC:
                raise PlanError(line, f"task #{task['id']} has {len(task['ac'])} AC; plan-format.md allows 1..{MAX_AC}")
            # Catch a dangling #new-N here, before --apply has created
            # anything — resolve() would only see it after the issues exist,
            # and that path has no rollback (PR #12 review, codex BLOCKER).
            for ref in task["depends_on"]:
                if ref.startswith("new-") and ref not in declared:
                    raise PlanError(line, f"task #{task['id']} depends on #{ref}, which no task declares")

    return {
        "target_repo": header["Target repo:"],
        "milestones": milestones,
        "failures": failures,
    }


def _body(task, deps):
    """Render the issue body: acceptance criteria plus the resolved deps line."""
    out = ["## Acceptance Criteria", ""]
    out += [f"- [ ] {c}" for c in task["ac"]]
    if deps:
        out += ["", "Depends on: " + ", ".join(f"#{d}" for d in deps)]
    return "\n".join(out) + "\n"


def resolve(plan, mapping):
    """Substitute every #new-N citation with its real issue number."""
    rows = []
    for milestone in plan["milestones"]:
        for task in milestone["tasks"]:
            if task["id"] not in mapping:
                raise PlanError(0, f"no created issue number for {task['id']}")
            deps = []
            for ref in task["depends_on"]:
                if ref.startswith("new-"):
                    if ref not in mapping:
                        raise PlanError(0, f"{task['id']} depends on #{ref}, which has no created issue number")
                    deps.append(mapping[ref])
                else:
                    deps.append(ref)  # real cross-plan citation, passes through
            rows.append({
                "id": task["id"],
                "number": mapping[task["id"]],
                "milestone": milestone["name"],
                "title": task["title"],
                "labels": task["labels"],
                "body": _body(task, deps),
            })
    return rows


def _load(source):
    text = sys.stdin.read() if source == "-" else open(source, encoding="utf-8").read()
    return json.loads(text)


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("parse")
    p.add_argument("plan")
    r = sub.add_parser("resolve")
    r.add_argument("--rows", required=True, help="parse output, or - for stdin")
    r.add_argument("--map", required=True, dest="map_", help='{"new-1": 42, ...}, or - for stdin')

    args = ap.parse_args()
    try:
        if args.cmd == "parse":
            with open(args.plan, encoding="utf-8") as fh:
                out = parse(fh.read())
        else:
            out = resolve(_load(args.rows), _load(args.map_))
    except PlanError as exc:
        where = f"line {exc.line}: " if exc.line else ""
        print(f"[FAIL] spec-flow:trd-to-issues {where}{exc.message}", file=sys.stderr)
        return 1
    except OSError as exc:
        print(f"[FAIL] spec-flow:trd-to-issues {exc}", file=sys.stderr)
        return 1
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
