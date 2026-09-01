# PRD-to-TRD Plan
Generated: 2026-09-01T17:44:52+09:00
Source PRD: docs/examples/prd-to-trd/prd-docs-pages.md
PRD directory: docs/examples/prd-to-trd
Mode: dry-run
Template: references/template-fallback.md

## Components

| Slug | 책임 F-# | 책임 D-# | NF-# (primary) | NF-# (cited) | 인접 TRD |
|------|----------|----------|----------------|--------------|----------|
| skill-inventory | F-1 | D-6 | NF-6 | NF-5 | guide-pages,usage-pages,link-validation,ci-gate |
| guide-pages | F-2 | D-1,D-5 | NF-1 | NF-3,NF-6 | skill-inventory,html-rendering |
| usage-pages | F-3,F-4 | D-1,D-4,D-5 | (none) | NF-3,NF-6 | skill-inventory,html-rendering |
| html-rendering | F-5,F-6 | D-3 | NF-2 | NF-4,NF-6 | guide-pages,usage-pages,pages-deploy |
| readme-index | F-7,F-8 | D-1,D-2 | NF-3 | NF-5,NF-6 | link-validation,pages-deploy |
| pages-deploy | F-9,F-14 | D-2 | NF-4 | NF-2 | html-rendering,readme-index |
| link-validation | F-10,F-11 | D-6 | NF-5 | NF-3 | skill-inventory,readme-index,ci-gate |
| ci-gate | F-12,F-13 | D-6 | (none) | NF-5,NF-6 | skill-inventory,link-validation |

## Suggested splits
_no suggestions._

## Manual review
- pages-deploy — PRD OQ-1 (Pages 발행 소스를 `docs/` 로 할지 `gh-pages` 브랜치로 할지) 미결. 이 TRD 의 §8 로 승계되며 PRD 확정 시 반영 필요.
- html-rendering — PRD OQ-2 (렌더된 HTML 을 repo 에 커밋할지 CI 에서 생성할지) 미결. D-3 은 생성 방법만 정하고 보관 위치는 열려 있음.
