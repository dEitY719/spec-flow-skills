---
name: ui-order
description: >-
  모호한 UI 요청을 바로 구현하지 않고, 빠진 결정을 되묻는 질문과 기본값을 채운
  화면 주문서 초안으로 먼저 답한다. Use for /spec-flow:ui-order, "버튼 만들어줘",
  "좀 예쁘게 해줘", "폰에서도 되게 해줘", "ui-order 설정해줘",
  "clarify a vague UI request before building".
license: MIT
allowed-tools: Read, Glob, Grep, Bash
metadata:
  model_recommendation:
    tier: sonnet
    reason: "vague UI request -> slot gap check + clarifying questions + draft order; judgment; writes only the CLAUDE.md block under --setup --apply"
    claude: prefer
    non_claude: advisory-only
---

# spec-flow:ui-order

## Purpose

모호한 UI 요청을 구현 전에 UI/UX 용어의 칸(slot)에 대 보고, 빠진 결정을 **질문 +
기본값이 채워진 화면 주문서 초안**으로 되돌려준다. 다음 턴의 답이나 "기본값으로 진행"
으로 확정된 주문서를 구현한다.

## Help

If the argument is `-h`, `--help`, or `help`, read `references/help.md` and output
its content verbatim, then stop.

## Setup mode

If the argument starts with `--setup`, run `lib/setup_claude_md.py` via
`$CLAUDE_PLUGIN_ROOT` (unset -> stop; never guess a path) exactly as
[`references/setup.md`](references/setup.md) says. Dry-run unless `--apply`. Then stop.

## Contract

- **The questions are the final output, not a mid-run prompt.** Never call
  AskUserQuestion or any blocking prompt. Print the questions and the draft order,
  then end the turn. The user replies in a normal next turn.
- **Writes files only under `--setup --apply`**: only the project `CLAUDE.md`, only
  between the ui-order markers. Otherwise read the project only to detect a stack
  (Tailwind, shadcn/ui, MUI, ...) and tokens; an existing convention beats defaults.
  A 화면 주문서 block in the project's `CLAUDE.md` is the strongest default source.
- **Do not nag a well-specified request.** If it already names parts and numbers,
  build it.

## Procedure

**Step 1: Identify targets** — name the screen type (대시보드, 목록-상세, 설정, 랜딩,
로그인, ...) and the components in the request (버튼, 폼 입력, 오버레이, 목록, ...).
Vague words map to precise terms via the translation table in
[`references/glossary.md`](references/glossary.md).

**Step 2: Check slots** — walk [`references/checklist.md`](references/checklist.md):
the screen-level slots (화면 · 레이아웃 · 내용 · 부품 · 상태 · 토큰 · 글자 · 반응형 ·
접근성) plus the component-family slots for every target found in Step 1. Mark each
relevant slot as specified (a name or a number is given) or missing.

**Step 3: Decide**

- Every relevant slot specified -> proceed to implement. No questions.
- Otherwise -> Step 4, then stop.

**Step 4: Output the order draft and end the turn** — exactly three parts, per
[`references/order-template.md`](references/order-template.md):

1. **질문** — at most 5, highest impact first (위계 / 오버레이 종류 / 예외 상태 /
   반응형 before 색·모션). Each question offers a concrete default from
   `checklist.md`.
2. **주문서 초안** — the request rewritten in the bracket format `[화면] [레이아웃]
   [내용] [부품] [상태] [토큰] [글자] [반응형] [접근성]`, relevant brackets only,
   every filled-in default marked `(기본값)`.
3. One closing line: `"기본값으로 진행"이라고 답하면 위 초안대로 구현합니다.`

**Step 5: Next turn** — on answers, merge them into the draft and implement. On
"기본값으로 진행" / "알아서 해줘", apply the defaults and state, in the implementation
reply, which `(기본값)` items were applied.

## Always-required exception states

For any view that shows data (list, table, card grid, dashboard, detail), the order
must carry all three, asked or defaulted — AI builds only the happy path otherwise:
로딩 = 스켈레톤 · 빈 상태 = 엠프티 스테이트 + 다음 행동 버튼 · 에러 = 에러 메시지 +
재시도 버튼.

## References

| File | Read when |
|------|-----------|
| `references/checklist.md` | Step 2 — slot lists and default values |
| `references/glossary.md` | Step 1 — term lookup, confusing pairs, vague-phrase translation |
| `references/order-template.md` | Step 4 — output shape and a worked example |
| `references/setup.md` | `--setup` only |
| `references/help.md` | `help` argument only |

Source vocabulary: "바이브 코더를 위한 UI/UX 용어 사전" (geniuskey),
https://geniuskey.github.io/vibe-coding/ui-ux/ — references are paraphrased, not copied.
