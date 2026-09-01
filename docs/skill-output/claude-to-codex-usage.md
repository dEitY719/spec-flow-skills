# claude-to-codex 사용 결과

> **한 줄 요약** — Claude 가 쓴 서술형 phase 문서(.md)를 받아 Codex 실행용 명령형
> 문서(.md)를 생성합니다. 원본은 수정하지 않습니다.

```
phase doc (.md)  ──▶  /spec-flow:claude-to-codex  ──▶  <base>-codex-01.md
```

## 1. 실행한 명령

CLI 플래그가 없다. 참조 문서와 대상 phase 문서를 자연어로 지목하면 발동한다.

```
<참조 문서들>, <대상 phase 문서>를 참조해서 codex 에서 작업하기 최적화된
설계문서로 변경해줘
```

이번 예시:

```
/spec-flow:claude-to-codex docs/examples/claude-to-codex/phase-03-docs-ci-gate.md
  (참조: CLAUDE.md, .github/workflows/validate.yml)
```

## 2. 입력

[`phase-03-docs-ci-gate.md`](../examples/claude-to-codex/phase-03-docs-ci-gate.md)
— 문서 링크 무결성 CI 게이트를 만들자는 Claude 작성 phase 문서(3,774바이트).
"무난해 보인다", "좋겠다", "과해 보인다", "것 같다" 같은 유예 표현이 섞여 있어
그대로 Codex 에 주면 판단을 요구받는 지점이 남는다.

## 3. 결과

```
[OK] spec-flow:claude-to-codex — 1 Codex document(s) written
  docs/ai/phases/codex/phase-03-docs-ci-gate-codex-01.md (single)
  AGENTS.md: unchanged
```

[`phase-03-docs-ci-gate-codex-01.md`](../ai/phases/codex/phase-03-docs-ci-gate-codex-01.md)
— 159줄, 10,405바이트. 섹션: Goal / Inputs / Scope / Out of scope / Files to
create or modify / Implementation instructions / Constraints / Assumptions /
Completion checklist / Codex prompt.

**분할하지 않았다(single).** 분할 조건 둘 다 걸리지 않았다 — 건드리는 파일이 신규
`scripts/check-docs-links.sh` 와 수정 `validate.yml` 둘뿐이고 같은 도메인이며,
의존 인터페이스가 전부 로컬에서 검증 가능하다.

**`AGENTS.md` 는 의도적으로 그대로 뒀다.** 이 repo 에서 `AGENTS.md` 는 `CLAUDE.md`
심링크라, 규칙대로 `@CLAUDE.md` 를 넣으면 `CLAUDE.md` 가 자기 자신을 import 하게
된다. 참조 문서가 명시한 "기존 구조화 파일을 깨뜨리는 경우" 예외에 해당한다.

원본은 수정되지 않았다 — 유예 표현 4곳이 그대로 있고 `git status` 도 변경을
보고하지 않는다.
