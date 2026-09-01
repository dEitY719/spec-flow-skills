# prd-to-trd

## 한 줄 요약

PRD 1건을 읽어 **컴포넌트별 TRD 스캐폴드**를 만들어 내는 스킬이다. 최종 산출물은
`<prd-dir>/trd/<slug>.md` 파일들 — 8-섹션 헤더와 작성 가이드 블록만 들어 있는
빈 뼈대이고, 본문은 사람이 채운다.

## 무엇을 만드는가

| 모드 | 산출물 |
|------|--------|
| `--dry-run` (기본) | 분해 계획 1개 — `--plan-out` 경로의 Markdown |
| `--apply` | 계획을 다시 읽어 컴포넌트마다 `<prd-dir>/trd/<slug>.md` 스캐폴드 |

계획 파일이 **유일한 리뷰 표면**이다. 슬러그 이름이나 책임 매핑이 마음에 안 들면
계획 파일을 손으로 고친 다음 `--apply` 로 다시 부르면 된다. 스킬은 원본 PRD 를
다시 해석하지 않고 편집된 계획을 그대로 왕복(round-trip)시킨다.

8-섹션 표준은 AI Spec-Driven 6개 섹션(AWS Kiro / Spec Kit / Cursor 계열)에 Google
Design Doc 의 2개 섹션(Goals / Non-Goals, Alternatives Considered)을 더한 형태다.

## 언제 쓰고 언제 안 쓰는가

**쓴다** — 제품 스펙 하나가 확정됐고, 이걸 컴포넌트 단위 기술 설계로 쪼개
누가 무엇을 책임지는지 나누고 싶을 때.

**안 쓴다:**

- TRD 를 GitHub Epic/Feature/Task 이슈로 등록하고 싶을 때 → `trd-to-issues`.
  이 스킬은 파이프라인의 PRD → TRD 구간만 담당하고 GitHub 을 전혀 건드리지 않는다.
- TRD 본문까지 AI 가 써주길 바랄 때 → 이 스킬은 거부한다. 500~800줄짜리 본문은
  의도적으로 사람 몫으로 남긴다(AI 범위 폭주 차단).
- PRD 가 너무 작아 컴포넌트가 2개도 안 나올 때 → `[WARN] PRD too small` 로
  중단한다. 메가 TRD 하나로 뭉뚱그리지 않는다.

## 호출 형식

```
/spec-flow:prd-to-trd <prd-path> [--apply] [--plan-out <path>] [--force]
```

| 인자 / 플래그 | 기본값 | 설명 |
|---|---|---|
| `<prd-path>` | 필수 | PRD Markdown 경로. v1 은 **1건만** 받는다(2개 이상이면 중단) |
| `--dry-run` | **on** | 기본값. 계획만 쓰고 스캐폴드는 절대 안 쓴다 |
| `--apply` | off | 계획을 재독해 `<prd-dir>/trd/<slug>.md` 스캐폴드 생성 |
| `--plan-out <path>` | `.claude/.prd-to-trd.plan.md` | 계획 파일 경로 |
| `--force` | off | `--apply` 때 기존 스캐폴드를 덮어쓴다(기본은 건너뛰고 로그) |
| `-h` / `--help` / `help` | — | 도움말만 출력하고 종료. 파일 변경 없음 |

## 동작 단계

1. **인자 검증** — PRD 파일 실재 확인. 없으면 `[FAIL] PRD not found: <path>` 후 중단.
2. **분해 제안** — PRD 의 `D-#`(교차 제약) → `F-#`(주 그룹핑 신호) → `NF-#`(TRD 당
   최대 1개 primary 배정) 순으로 읽어 kebab-case 슬러그 6~8개와 책임 매핑표를 만든다.
   계약을 공유하는 슬러그끼리는 인접 TRD 로 상호 연결한다.
3. **템플릿 탐색** — `<prd-dir>/trd/_template.md` 를 먼저 찾고, 없으면 내장
   `references/template-fallback.md` 로 폴백. 둘 다 없으면 중단.
4. **계획 작성** — `--plan-out` 에 기록하고 dry-run 이면 여기서 멈춘다.
5. **적용** — `--apply` 일 때만. 계획을 다시 읽어 슬러그별 스캐폴드를 쓴다.

## 주의사항 / 제약

- **PRD 를 수정하지 않는다.** 입력 전용이며, PRD 의 빈틈은 계획에 보고만 한다.
- **출력 경로가 PRD 디렉터리에 갇혀 있다.** `<prd-dir>/trd/` 밖으로는 쓰지 않는다.
- **기존 스캐폴드는 건너뛴다.** `--force` 없이는 덮어쓰지 않으므로 재실행이 안전하다.
- **중간 실패 시 롤백하지 않는다.** 어디까지 썼는지 부분 상태를 보고하고 멈춘다.
  뒷정리는 사람 몫이다.
- **NF-# 를 지어내지 않는다.** TRD 수보다 NF 항목이 적으면 남는 칸은 `(none)` 으로
  둔다. 슬롯을 채우려고 항목을 합성하지 않는다.
- 슬러그에 버전 접미사(`-v1`)나 PRD 섹션 번호(`f4-auth`)를 넣지 않는다.

## 이어지는 스킬

`trd-to-issues` — 사람이 스캐폴드를 채운 뒤 그 TRD 를 Milestone + Issue 로 등록한다.
