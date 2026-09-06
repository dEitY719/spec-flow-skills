#!/usr/bin/env python3
"""4-bucket classifier for spec-flow:pr-to-ssot-issue Step 2.

Reads a newline-separated file list on stdin (typically
`gh pr diff <PR#> --name-only`) and writes JSON on stdout:

    {"code": [...], "schema": [...], "infra": [...], "docs": [...],
     "counts": {"code": n, "schema": n, "infra": n, "docs": n}}

Implements the ordered, first-match-wins glob table in
references/gap-detection.md "Bucket rules" as a pure function of the file
list, so bucket counts are reproducible across two runs on the same PR
(dEitY719/spec-flow-skills#3, Check 12).

Two documented tie-breaks in gap-detection.md are NOT enforced here because
they depend on diff content or export semantics, not filenames — a file list
alone can't answer them: (a) a docs/*.md file with an embedded OpenAPI/SQL
block, and (b) a models/*.py file that happens to be exported as a DB/API
contract. Both stay the subagent's / human reviewer's judgment call.

Self-check: tests/pr-to-ssot-classify.sh.
"""

import json
import re
import sys

# Ordered top-to-bottom; first match wins. Mirrors references/gap-detection.md
# "Bucket rules" table exactly — do not reorder without updating that table.
BUCKET_PATTERNS = [
    ("schema", [
        "migrations/**",
        "*.sql",
        "schema*.sql",
        "openapi*.{yaml,yml,json}",
        "*.proto",
        "graphql/**",
        "**/schema.{ts,py,graphql}",
    ]),
    ("infra", [
        ".github/workflows/**",
        "Dockerfile*",
        "docker-compose*.yml",
        "Makefile",
        "terraform/**",
        "helm/**",
        "ansible/**",
        ".env*",
        "infra/**",
        "deploy/**",
    ]),
    ("docs", [
        "*.md",
        "*.rst",
        "docs/**",
        "README*",
    ]),
]
DEFAULT_BUCKET = "code"


def _glob_to_regex(pattern):
    """Translate one gap-detection.md glob into an anchored regex.

    Supports the subset actually used by BUCKET_PATTERNS: `**/` (zero or more
    leading path segments), bare `**` (any span, slashes included), `*`
    (any span within one segment), and `{a,b,c}` brace alternation. No `?`
    wildcard — no pattern in the table below needs one.
    """
    out = ["^"]
    i, n = 0, len(pattern)
    while i < n:
        if pattern[i : i + 3] == "**/":
            out.append("(?:.*/)?")
            i += 3
        elif pattern[i : i + 2] == "**":
            out.append(".*")
            i += 2
        elif pattern[i] == "*":
            out.append("[^/]*")
            i += 1
        elif pattern[i] == "{":
            j = pattern.find("}", i)
            if j == -1:
                raise ValueError(f"unclosed '{{' in bucket pattern: {pattern!r}")
            options = pattern[i + 1 : j].split(",")
            out.append("(?:" + "|".join(re.escape(o) for o in options) + ")")
            i = j + 1
        else:
            out.append(re.escape(pattern[i]))
            i += 1
    out.append("$")
    return re.compile("".join(out))


# A pattern with no "/" (e.g. `*.sql`, `Dockerfile*`) is a basename glob —
# it must match at any depth (`services/api.sql`), not just at repo root.
# A pattern with a "/" (e.g. `migrations/**`, `.github/workflows/**`) is
# rooted and matches the full path. Same distinction gitignore/find -name
# draw between a bare pattern and a path pattern.
_COMPILED = [
    (bucket, [(_glob_to_regex(p), "/" not in p) for p in patterns])
    for bucket, patterns in BUCKET_PATTERNS
]


def classify(path):
    """Return the bucket name for one file path."""
    basename = path.rsplit("/", 1)[-1]
    for bucket, regexes in _COMPILED:
        for rx, basename_only in regexes:
            if rx.match(basename if basename_only else path):
                return bucket
    return DEFAULT_BUCKET


def classify_all(paths):
    buckets = {"code": [], "schema": [], "infra": [], "docs": []}
    for path in paths:
        buckets[classify(path)].append(path)
    counts = {b: len(files) for b, files in buckets.items()}
    return {**buckets, "counts": counts}


def main():
    paths = [line.strip() for line in sys.stdin if line.strip()]
    print(json.dumps(classify_all(paths), ensure_ascii=False))


if __name__ == "__main__":
    main()
