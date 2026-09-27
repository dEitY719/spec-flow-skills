# Order template and worked example

Step 4 prints exactly this shape, then ends the turn. No AskUserQuestion, no file
writes — the user answers in the next turn.

## Output shape

```
UI 요청에 빠진 결정이 있어 구현 전에 확인합니다.

질문 (영향 큰 순, 최대 5개)
1. <질문> — 기본값: <값>
2. ...

주문서 초안
[화면] ...
[레이아웃] ...
[내용] ...
[부품] ...
[상태] ...
[토큰] ...
[글자] ...
[반응형] ...
[접근성] ...

"기본값으로 진행"이라고 답하면 위 초안대로 구현합니다.
```

Rules:

- Keep only the brackets relevant to the request. A lone button has no `[화면]` or
  `[반응형]` unless the user mentioned mobile.
- Every value the user did not give is marked `(기본값)`. Values the user gave are
  written without the mark.
- A question and its bracket must agree: the default quoted in question N is the
  value shown in the draft.
- If the project already has a stack or tokens, use those as the defaults and say so
  in the first line (예: "기존 shadcn/ui 설정을 기본값으로 썼습니다").

## Full template (all nine brackets)

```
[화면] <화면 종류>, <필요하면 로그인 / 404 / 온보딩>
[레이아웃] <골격 영역과 크기>, 컨테이너 max-width <값>
[내용] <카드 그리드 / 리스트 / 테이블>, <열 수>, gap <값>
[부품] <이름 붙은 부품>, <상호작용별 오버레이 종류>
[상태] 로딩 <스켈레톤>, 빈 상태 <엠프티 스테이트 + 버튼>, 에러 <재시도 버튼>; <부품 상태>
[토큰] 간격 <스케일>, radius <값>, 그림자 <단계>, 타입 스케일 <단계>
[글자] 본문 <크기 / 행간>, <말줄임>, <숫자 정렬>
[반응형] <모바일 퍼스트 여부>, 브레이크포인트 <값>, <구간별 변화>
[접근성] 포커스 링, 명암비 <값>, 터치 타깃 <값>, aria-label
```

## One-shot example: a complete order

This is what a fully specified order looks like — every bracket named and numbered,
plus a wireframe-first closing line. Three uses:

- **Target shape.** A Step 4 draft aims at this density; the user fills or accepts
  the `(기본값)` items until it reads like this.
- **No questions.** A request written like this passes Step 3 as-is: build it.
- **Project default.** Adapted once to the project and pasted into its `CLAUDE.md`
  (see the skill guide), it becomes the defaults Step 4 uses instead of
  `checklist.md` — mark items taken from it `(프로젝트 기본값)`.

```
◯◯◯ 도구를 만들어줘. Tailwind + shadcn/ui, 미니멀 스타일, 라이트/다크 모드 둘 다.

[화면]     대시보드 + 목록-상세 + 설정, 로그인은 SSO 버튼 하나, 없는 주소는 404.
[레이아웃] 상단 56px 앱 바 + 좌측 240px 고정 사이드바 + 본문. 컨테이너 max-width 1200px.
[내용]     본문은 카드 그리드(데스크톱 3열 / 태블릿 2열 / 모바일 1열, gap 16px).
[부품]     검색 입력, 필터는 칩, 행 클릭 시 상세는 팝오버가 아니라 모달로.
[상태]     로딩은 스켈레톤, 0건은 엠프티 스테이트(생성 버튼 포함), 실패는 재시도 버튼이 있는 에러 상태.
[토큰]     간격 8의 배수, 라운드 12px, 그림자 약하게, 글자 크기 4단계(Display/Heading/Body/Caption).
[글자]     본문 16px · 행간 1.6, 카드 제목은 2줄 line-clamp, 숫자 열은 tabular-nums.
[반응형]   모바일 퍼스트, 브레이크포인트 640/1024. 1024px 미만에서 사이드바는 드로어로.
[접근성]   포커스 링 유지, 명암비 4.5:1 이상, 아이콘 버튼에 aria-label.

먼저 와이어프레임 수준으로 만들고 스크린샷을 보여줘. 확인하면 스타일을 입히자.
```

For a whole screen or app (not a single component), end the Step 4 draft with the
same wireframe-first line: build a wireframe, show it, style it after confirmation.

## Worked example: "버튼 만들어줘"

Input: `버튼 만들어줘` (no project stack detected)

Step 1 targets: 부품 = 버튼 1개. No screen type, no data view.
Step 2 missing: 위계, 용도·레이블, 크기·padding, radius, 상태, 아이콘, 스택.
Step 3: slots missing -> output and stop.

Output:

```
UI 요청에 빠진 결정이 있어 구현 전에 확인합니다.

질문 (영향 큰 순)
1. 어떤 행동의 버튼인가요? 위계를 정해 주세요: primary(주 행동) / secondary(보조) /
   ghost(취소 등 글자만) / destructive(삭제 등 되돌릴 수 없는 행동)
   — 기본값: primary 1개, 레이블 "저장"
2. 옆에 취소 같은 두 번째 버튼이 필요한가요? — 기본값: 없음 (필요하면 ghost "취소")
3. 누른 뒤 서버 처리가 있나요? 있으면 loading 상태가 필요합니다
   — 기본값: 있음, 처리 중 disabled + 스피너
4. 크기와 모양 — 기본값: 높이 40px, padding 12px 20px, radius 12px
5. 아이콘을 넣을까요? — 기본값: 없음 (넣으면 Lucide outline 20px, 왼쪽)

주문서 초안
[부품] primary 버튼 1개, 레이블 "저장" (기본값)
[상태] hover / focus-visible / disabled / loading (기본값); 처리 중 disabled + 스피너 (기본값)
[토큰] 높이 40px, padding 12px 20px, radius 12px, 그림자 없음 (기본값);
       스택 Tailwind + shadcn/ui (기본값); 전환 200ms ease-out, prefers-reduced-motion 존중 (기본값)
[접근성] 포커스 링 유지, 명암비 4.5:1 이상, 터치 영역 44px 이상 (기본값)

"기본값으로 진행"이라고 답하면 위 초안대로 구현합니다.
```

Next turn, user says "기본값으로 진행" -> implement the draft and open the reply with
one line listing the applied defaults, e.g.
`적용한 기본값: primary "저장", 40px / 12px 20px / radius 12px, hover·focus-visible·disabled·loading, Tailwind + shadcn/ui.`

## Short example: "대시보드 만들어줘"

The questions that matter most here are different — 화면 구성 before tokens:

1. KPI 카드에 어떤 지표 3~4개를 보여줄까요? — 기본값: 사용자가 정할 때까지 자리표시 지표 3개
2. 기간 필터가 필요한가요? — 기본값: 상단 필터 바 + date range picker (최근 7일 프리셋)
3. 본문 차트는 무엇을 보여주나요? — 기본값: 추이는 라인 차트, 항목 비교는 바 차트
4. 상세 데이터 목록이 필요한가요? — 기본값: 아래에 테이블 (고정 헤더, 숫자 열 tabular-nums)
5. 모바일에서도 쓰나요? — 기본값: 모바일 퍼스트, 640 / 1024, 1024 미만 사이드바는 드로어

The draft then carries `[상태] 로딩 스켈레톤, 빈 상태 엠프티 스테이트 + 필터 초기화
버튼, 에러 재시도 버튼 (기본값)` whether or not the user asked — it is a data view.
