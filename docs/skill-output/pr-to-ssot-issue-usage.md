# pr-to-ssot-issue 사용 결과

> **한 줄 요약** — 예외 PR 번호를 받아 8-섹션 SSOT 추적 이슈를 생성합니다.
> **이 문서는 실행 기록이 아닙니다** — 대상이 될 PR 이 없어 실행하지 못했습니다.

```
PR#  ──▶  /spec-flow:pr-to-ssot-issue  ──▶  SSOT 이슈 1건   [실행 불가]
```

## 1. 실행하려던 명령

```
/spec-flow:pr-to-ssot-issue <PR#> --reason "<사유>" [--parent <N>] [--dry-run]
```

## 2. 입력 — 확보하지 못함

입력은 대상 repo 에 실재하는 PR 번호다. 스킬은 git remote 로 대상 repo 를 확정한 뒤
`gh pr view <PR#>` 로 상태가 `OPEN`/`MERGED` 인지 확인한다. PR 이 없으면 어떤
인자로도 진행할 수 없다.

```
$ git remote get-url origin
git@github.com:dEitY719/spec-flow-skills.git

$ gh pr list --repo dEitY719/spec-flow-skills --state all --limit 100
(빈 출력, exit 0)

$ gh pr view 1 --repo dEitY719/spec-flow-skills --json number,state
GraphQL: Could not resolve to a PullRequest with the number of 1. (repository.pullRequest)
(exit 1)
```

커밋 1건으로 시작된 신규 repo 라 PR 이 한 건도 없다.

## 3. 결과 — 없음

산출물이 없다. `--dry-run` 조차 실행하지 않았다. `--dry-run` 은 GitHub *쓰기* 만
생략할 뿐 PR 조회는 그대로 수행하므로 Step 1 전제 검증에서 멈춘다.

이 스킬은 이런 상황에서 추측으로 진행하지 않고 닫히도록 설계돼 있다 — remote 를
모르면 조용히 폴백하지 않고, 갭이 비면 빈 껍데기 이슈를 만들지 않고 exit 4 로
거부한다. 여기서 실행 결과를 지어내 적는 것은 그 설계 의도와 정반대다.

**실행 가능해지는 조건** — 이 repo 에 PR 이 하나 머지되거나, 다른 repo 체크아웃에서
그 repo 의 예외 PR 을 대상으로 호출하면 된다. 스킬의 결함이 아니라 이 repo 에 아직
이력이 없어서 생긴 공백이다.

사용법과 제약은 [visual guide](../skill-guides/pr-to-ssot-issue.html) 를 참고한다.
