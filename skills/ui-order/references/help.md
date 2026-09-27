/spec-flow:ui-order — Clarify a vague UI request before building it

Usage:
  /spec-flow:ui-order "<UI request>"
  /spec-flow:ui-order --setup [--apply] [--force] [--project <dir>]
  /spec-flow:ui-order help | -h | --help

Arguments:
  "<UI request>"    The request as the user wrote it (e.g. "버튼 만들어줘",
                    "대시보드 좀 예쁘게", "폰에서도 되게 해줘")

Behaviour:
  - Well-specified request (names + numbers given): implements it directly.
  - Vague request: prints up to 5 questions with defaults and a draft
    화면 주문서, then ends the turn. No blocking prompt, no files written.
  - Reply "기본값으로 진행" in the next turn to build with the defaults.

Setup (--setup):
  Installs the "UI 요청 규칙" + "화면 주문서 (프로젝트 기본값)" block into the
  project's CLAUDE.md, between <!-- ui-order:begin --> / <!-- ui-order:end -->.
  Detects the stack (Tailwind, shadcn/ui, MUI, Ant Design, Fluent UI, framework,
  Lucide) from package.json; undetected values are marked (기본값). Edit the
  [화면] placeholder afterwards.

  --apply           Write the block (default is a dry-run that prints it)
  --force           Replace the content between existing markers
  --project <dir>   Project dir (default: git toplevel of CWD, else CWD)

  A symlinked CLAUDE.md (e.g. -> AGENTS.md) is written through. Nothing outside
  the markers is ever touched. Malformed markers fail with exit 1, no write.

Examples:
  /spec-flow:ui-order "버튼 만들어줘"
  /spec-flow:ui-order "알림 띄워줘"
  /spec-flow:ui-order "사내 수율 대시보드 만들어줘, 폰에서도 되게"
  /spec-flow:ui-order --setup
  /spec-flow:ui-order --setup --apply
  /spec-flow:ui-order --setup --apply --force
  /spec-flow:ui-order help

Options:
  help, -h, --help  Show this message
