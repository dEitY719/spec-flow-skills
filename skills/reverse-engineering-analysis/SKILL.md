---
name: reverse-engineering-analysis
description: >-
  기존 기능 하나를 분석해 재사용 가능한 AI 구현 프롬프트를 생성한다. Use for
  /spec-flow:reverse-engineering-analysis, "이 기능 어떻게 동작하는지 분석해줘",
  "graph 기능 뜯어서 프롬프트로 만들어줘",
  "reverse engineer this feature into a reusable AI prompt".
license: MIT
allowed-tools: Read, Glob, Grep, Write, Edit, Bash
metadata:
  model_recommendation:
    tier: sonnet
    reason: "feature analysis → one Markdown deliverable; reads code, writes no implementation"
    claude: prefer
    non_claude: advisory-only
---

# spec-flow:reverse-engineering-analysis

## Purpose

Goals:

1. Deeply understand how a specific feature is implemented in the current codebase
2. Identify the essential libraries and their roles
3. Explain the working mechanism (data flow focus)
4. **Generate a copy-pasteable AI implementation prompt** — the most important output

The final deliverable lets the user paste one prompt into any AI coding assistant to implement the same feature in a new project.

---

## Help

If the argument is `-h`, `--help`, or `help`, read `references/help.md` and output its content verbatim, then stop.

## Options

| Argument | Required | Default | Description |
|----------|----------|---------|-------------|
| `<feature or file path>` | yes | — | Feature description (keyword search) or explicit file path |
| `[output directory]` | no | `docs/` | Directory where `analysis.md` is written |

A feature description is resolved by keyword search (Grep/Glob); a file path is read directly.

---

## Analysis Workflow

See [`references/workflow.md`](references/workflow.md) for full step details.

Stop on error: if any step fails, abort and report the failed step.

**Step 1: Locate** — search by keyword or read file path directly
**Step 2: Deep Dive** — read each core file; note what it does, how data flows, what it touches
**Step 3: Extract Libraries** — gather from imports; check the package manifest for versions
**Step 4: Explain Mechanism** — data flow, component handoffs, non-obvious design choices
**Step 5: Generate AI Prompt** — self-contained and paste-and-go (**most critical output**)

---

## Output Format

Write to `<output_dir>/analysis.md`. See [`references/output-template.md`](references/output-template.md) for the full template.

The template is the single source for the required sections; the **AI Implementation Prompt** section is the critical one and must stay free of project-specific paths.

End with `[OK] analysis written: <path>` or `[FAIL] <reason>`. A pre-write
quality checklist is in `references/output-template.md`.

`Next: read <output_dir>/analysis.md and paste the AI Implementation Prompt section into the target project's AI assistant.`
