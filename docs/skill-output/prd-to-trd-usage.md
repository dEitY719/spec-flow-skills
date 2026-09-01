# prd-to-trd 사용 결과

> **한 줄 요약** — PRD 1건(.md)을 받아 분해 계획 1개와 컴포넌트별 TRD 스캐폴드
> 8개(.md)를 생성합니다.

```
PRD (.md)  ──▶  /spec-flow:prd-to-trd  ──▶  plan (.md) + trd/<slug>.md x8
```

## 1. 실행한 명령

```
/spec-flow:prd-to-trd <prd-path> [--apply] [--plan-out <path>] [--force]
```

이번 예시 — dry-run 으로 계획을 만든 뒤 `--apply` 로 스캐폴드를 썼다.

```
/spec-flow:prd-to-trd docs/examples/prd-to-trd/prd-docs-pages.md \
    --plan-out docs/examples/prd-to-trd/plan.md
/spec-flow:prd-to-trd docs/examples/prd-to-trd/prd-docs-pages.md \
    --plan-out docs/examples/prd-to-trd/plan.md --apply
```

## 2. 입력

[`prd-docs-pages.md`](../examples/prd-to-trd/prd-docs-pages.md) — 이 repo 의 문서
사이트 PRD(6,366바이트). `F-1`~`F-14`, `D-1`~`D-6`, `NF-1`~`NF-6`, 미결 `OQ-1`/`OQ-2`.
`trd/_template.md` 가 없어 내장 `references/template-fallback.md` 로 폴백했다.

## 3. 결과

```
Plan written: docs/examples/prd-to-trd/plan.md (8 components)
[OK] spec-flow:prd-to-trd plan=docs/examples/prd-to-trd/plan.md components=8 scaffolds=8 skipped=0
```

- [`plan.md`](../examples/prd-to-trd/plan.md) — 26줄. 슬러그 8개: `skill-inventory`,
  `guide-pages`, `usage-pages`, `html-rendering`, `readme-index`, `pages-deploy`,
  `link-validation`, `ci-gate`. `F-1`~`F-14` 가 각각 한 번씩 배정됐다.
- [`trd/`](../examples/prd-to-trd/trd/) — 스캐폴드 8개, 각 65줄 / 8섹션. 본문 없이
  헤더와 안내 인용구만 들어 있다.

NF 는 6개인데 TRD 는 8개라 `usage-pages`/`ci-gate` 의 primary 칸이 `(none)` 으로
남았다. 규칙상 슬롯을 채우려 NF 를 합성하지 않는다. 미결 질문 2건은 계획의
`## Manual review` 로 넘어갔다.
