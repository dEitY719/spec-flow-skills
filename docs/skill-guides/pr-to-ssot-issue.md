# pr-to-ssot-issue

## 한 줄 요약

PRD/TRD 를 건너뛰고 진행된 **예외 PR** 을 역산해, 빠진 명세를 8-섹션 **SSOT 추적
이슈 1건**으로 등록한다. 산출물은 새 이슈 하나(그리고 선택적으로 부모 이슈에 다는
backlink 코멘트 하나)다.

## 예외 PR 이란

프로젝트의 정상 흐름은 `Issue → PRD → TRD → 구현 → PR` 이다. 이걸 우회한 PR —
이미 머지됐거나, 대응하는 PRD/TRD 이슈 없이 진행 중인 PR — 이 예외 PR 이다.
코드는 들어갔는데 명세에는 그 흔적이 없는 상태이므로, 나중에 그 기능의 근거를
찾을 수 없다. 이 스킬은 그 구멍을 사후에 메운다.

## 무엇을 만드는가

8개 섹션으로 구성된 이슈 본문:

Why · Scope(4-버킷 표 + 서브에이전트 리포트) · Acceptance Criteria · Out of Scope ·
Parent / Related · Audit · TODO 후속 · 관계 / Cross-refs

`--reason` 으로 넘긴 예외 사유는 Audit 섹션의 `> [!IMPORTANT]` 콜아웃 안에
**한 글자도 바꾸지 않고** 들어간다. 제목 형식은
`docs(ssot): #<PR#> 역공학 — <PR 제목 60자 절단>` 이다.

## 언제 쓰고 언제 안 쓰는가

**쓴다** — 급해서, 또는 외부 기여라서 명세 없이 머지된 PR 을 발견했고, SSOT 커버리지를
회복해야 할 때.

**안 쓴다:**

- 정상 흐름을 탄 PR 에는 쓰지 않는다. 이미 PRD/TRD 인용 이슈와 연결돼 있으면
  overlap 으로 판단해 exit 3 으로 거부한다(`--force-overlap` 으로만 강행 가능).
- 빠진 명세가 실제로 없을 때. 5개 갭 섹션이 전부 `(none)` 이면 exit 4 로 거부하고
  일반 리뷰를 권한다. **빈 껍데기 이슈를 만들지 않는다.**
- 대화 내용을 이슈로 남기고 싶을 때 → `gh-issue:create`.
- 기능을 프롬프트로 뽑고 싶을 때 → `reverse-engineering-analysis`. 이 스킬은 PR 을
  명세로 되돌리고, 저쪽은 기능을 재구현 프롬프트로 되돌린다.

## 호출 형식

```
/spec-flow:pr-to-ssot-issue <PR#> --reason "<사유>" [--parent <N>] [--remote <name>]
                            [--milestone "<name>"] [--label <name>]...
                            [--dry-run] [--force-overlap] [--no-next-hint]
```

| 인자 / 플래그 | 기본값 | 설명 |
|---|---|---|
| `<PR#>` | 필수 | 역공학할 PR 번호(양의 정수) |
| `--reason "<text>"` | **필수** | 예외 사유. **10자 이상 강제**, 미달이면 exit 2 |
| `--parent <issue#>` | PR 본문의 `Closes #N` | 부모 이슈. 없으면 비워 두고 경고 |
| `--remote <name>` | `origin` | 대상 remote |
| `--milestone "<name>"` | 부모/PR 에서 상속 | `--apply` 시 사전 검증 |
| `--label <name>` | `documentation`, `priority:medium` | 반복 지정 가능. 사전 검증 |
| `--dry-run` | off | `.claude/.pr-to-ssot.<PR#>.draft.md` 만 쓰고 이슈 생성 생략 |
| `--force-overlap` | off | 이미 SSOT 연결이 있어도 강행 |
| `--no-next-hint` | off | 최종 보고에서 `Next:` 라인 생략 |

## 동작 단계

1. **전제 검증(fail-fast)** — PR 번호가 양의 정수인가, `--reason` 이 10자 이상인가,
   PR 상태가 `OPEN` 또는 `MERGED` 인가. `CLOSED`(미머지)는 거부한다.
2. **diff 수집 + 4-버킷 분류** — 변경 파일을 code / schema / infra / docs 로 나누고
   버킷마다 "어느 SSOT 섹션이 위험한가" 가설을 붙인다. overlap 가드도 여기서 작동.
3. **서브에이전트 갭 분석** — repo 의 PRD/TRD 를 읽고 Glossary / API 계약 /
   Data Models / Deployment / Cross-refs 5개 섹션으로 리포트를 받는다.
4. **본문 렌더링** — 8-섹션 + ai-metrics 푸터.
5. **생성** — 드래프트 작성 → 미리보기 → (`--dry-run` 이면 여기서 종료) →
   라벨/마일스톤 사전 검증 → `gh issue create --body-file` → 부모 backlink(soft-fail).

## 주의사항 / 제약

- **원본 PR 은 읽기 전용이다.** `gh pr edit`, `gh pr comment`, `gh pr review` 를 절대
  실행하지 않고 PR 에 라벨도 붙이지 않는다.
- **라벨/마일스톤을 자동 생성하지 않는다.** 없으면 목록을 보여주고 멈춘다.
  기본 라벨 이름은 repo 마다 다르므로 실제 존재하는 이름으로 바꿔 호출해야 한다.
- **`--reason` 없이는 진행하지 않는다.** 감사 추적이 이 스킬의 존재 이유다.
- **remote 가 없으면 조용히 폴백하지 않는다.**
- **중간 실패 시 롤백하지 않는다.** 부분 상태를 보고하고 멈춘다.
- `GH_DISABLE_AI_METRICS=1` 이면 메트릭 관련 동작을 억제한다.
- `/gh-flow:issue` 로 자동 연결되지 않는다. 힌트만 출력한다.

## 종료 코드

| 코드 | 의미 |
|---|---|
| 0 | 성공(이슈 생성 또는 `--dry-run` 드래프트 작성) |
| 1 | 그 밖의 실패(remote 없음, 라벨 없음, `gh` 오류) |
| 2 | `--reason` 누락 또는 10자 미만 |
| 3 | 이미 PRD/TRD 인용 이슈와 연결됨 |
| 4 | 갭 섹션이 전부 `(none)` |

## 이어지는 스킬

`gh-flow:issue` — 등록된 SSOT 이슈를 받아 구현 루프를 돌린다.
