# Slot checklist and defaults

Step 2 walks this file. A slot counts as **specified** only when the request (or an
existing project convention) gives a name or a number for it. "예쁘게", "적당히",
"깔끔하게" specify nothing.

Only the slots relevant to the request matter: a single button does not need a
breakpoint question, a dashboard does. Ask about the missing slot with the biggest
visual or behavioural consequence first.

## Screen-level slots

| Slot | What must be decided | Default if unanswered |
|------|----------------------|-----------------------|
| 화면 | Screen type(s): 대시보드, 목록-상세, 설정, 랜딩, 로그인, 온보딩, 404, 체크아웃 | Infer from the request; ask only if two types fit |
| 레이아웃 | Skeleton regions and their sizes | 상단 앱 바 56px + 좌측 고정 사이드바 240px + 본문; 컨테이너 max-width 1200px 가운데 정렬 |
| 내용 | How repeated items are shown: 카드 그리드 / 리스트 / 테이블 | 카드 그리드 (데스크톱 3열 / 태블릿 2열 / 모바일 1열, gap 16px); 비교·정렬이 필요한 데이터는 테이블 |
| 부품 | Named components and which overlay type each interaction uses | See component families below |
| 상태 | Interaction states and exception screens | 버튼 hover / focus-visible / disabled / loading; 데이터 화면은 로딩·빈·에러 3종 (always required) |
| 토큰 | Spacing, radius, shadow, type scale, color roles | 간격 8의 배수 (4 / 8 / 16 / 24 / 40); radius 12px; 그림자 약하게 (1단계); 색은 primary / surface / muted / semantic 역할로 |
| 글자 | Font, sizes, line height, truncation, numbers | 4단계 타입 스케일: Display 36/800, Heading 24/700, Body 16/400, Caption 13/400; 본문 행간 1.6, 왼쪽 정렬; 카드 제목 2줄 line-clamp; 숫자 열은 tabular-nums 오른쪽 정렬 |
| 반응형 | Breakpoints and what changes at each | 모바일 퍼스트, 브레이크포인트 640 / 1024; 1024 미만에서 사이드바는 드로어(스크림 포함)로 |
| 접근성 | Minimum a11y bar | 포커스 링 유지, 명암비 4.5:1 이상, 터치 타깃 44px 이상, 아이콘 버튼에 aria-label, 색만으로 의미 전달 금지 |

Cross-cutting defaults:

- **Stack** — if the project has none: Tailwind + shadcn/ui, 미니멀 스타일, 라이트/다크 모두
  (시스템 설정 따름). If the project already uses a library, follow it and do not ask.
- **Motion** — 전환 200ms ease-out; `prefers-reduced-motion` 이면 애니메이션 끔.
- **Icons** — Lucide outline 20px (버튼 안), 한 세트로 통일, 이모지 아이콘 금지.
- **Theme** — 한 테마만 (Material / Cupertino / Fluent 를 섞지 않는다).

## Component-family slots

### 버튼

| Slot | Default |
|------|---------|
| 위계 — primary / secondary(outline) / ghost / destructive | 화면당 primary 1개; 취소는 ghost; 되돌릴 수 없는 행동은 destructive |
| 크기 · padding | 높이 40px, padding 12px 20px (모바일 터치 영역 44px 이상) |
| radius | 12px (토큰과 동일) |
| 상태 | hover / focus-visible / disabled / loading (제출 중 disabled + 스피너) |
| 아이콘 | 없음; 아이콘만 있는 버튼이면 aria-label 필수 |
| 명령이 많을 때 | primary 1 + ghost 1, 나머지는 더보기(케밥) 드롭다운 메뉴 |

### 폼 입력

| Slot | Default |
|------|---------|
| 텍스트 3단 | 레이블은 항상 입력칸 밖 위; 플레이스홀더는 예시만; 헬퍼 텍스트는 아래 |
| 선택 방식 | 다중 = 체크박스, 단일 = 라디오, 즉시 적용 설정 = 스위치, 긴 목록 = 셀렉트 (검색 필요하면 콤보박스) |
| 유효성 검증 | 인라인 검증 — blur 시 검사, 빨간 테두리 + 아래 메시지 + 아이콘 |
| 제출 | primary 제출 버튼, 제출 중 loading, 실패 시 폼 상단 에러 배너 |

### 내비게이션

| Slot | Default |
|------|---------|
| 주 내비 | 데스크톱 240px 고정 사이드바 (현재 항목 active 표시); 1024 미만 드로어; 모바일 앱이면 하단 탭 3~5개 |
| 화면 전환 | 다른 내용 = 탭, 같은 내용의 보기 방식 = 세그먼티드 컨트롤 |
| 깊은 계층 | 브레드크럼 |
| 긴 목록 | 페이지네이션; 아래에 푸터가 있으면 무한 스크롤 대신 "더 보기" |
| 여러 단계 | 스테퍼 |

### 콘텐츠 컨테이너

| Slot | Default |
|------|---------|
| 표현 방식 | 카드 / 리스트 / 테이블 중 하나를 사람이 정한다 (질문 대상) |
| 테이블 | 고정 헤더, 정렬 가능 열, 숫자 열 tabular-nums 오른쪽 정렬 |
| 카드 | 제목 2줄 line-clamp, 썸네일은 16:9 + object-fit cover |
| 라벨 | 누를 수 있으면 칩, 숫자·점 알림이면 배지 |
| 긴 설명 | 짧으면 툴팁, 길거나 상호작용이 있으면 팝오버 |

### 오버레이

| Slot | Default |
|------|---------|
| 흐름을 끊는가 | 끊어야 하면 모달(스크림 포함), 아니면 논모달 (팝오버·토스트·배너) |
| 확인 · 삭제 | 컨펌 다이얼로그 (destructive 버튼 + ghost 취소) |
| 완료 피드백 | 토스트 3초 자동 사라짐; 되돌리기가 필요하면 스낵바 |
| 지속 경고 | 상단 배너 (닫기 전까지 유지) |
| 모바일 선택지 | 바텀 시트 |
| 닫기 | Esc, 스크림 클릭, 닫기 아이콘 버튼 (aria-label) |

### 대기 · 빈칸 (데이터 화면이면 항상 필수)

| Slot | Default |
|------|---------|
| 로딩 | 목록·카드는 스켈레톤; 1초 내외의 짧은 동작만 스피너; 끝이 보이는 작업은 프로그레스 바 |
| 빈 상태 | 엠프티 스테이트 = 그림 또는 아이콘 + 한 줄 안내 + 다음 행동 버튼 (예: 생성) |
| 에러 | 이유 한 줄 + 재시도 버튼; 막다른 화면 금지 |

### 이미지 · 아이콘

| Slot | Default |
|------|---------|
| 종횡비 | 썸네일 16:9, 사진 4:3, 프로필 1:1 — 고정 |
| 맞춤 | object-fit cover |
| 로딩 | 회색 플레이스홀더로 자리 확보 + 화면 밖 이미지는 lazy |
| 사진 위 글자 | 어두운 그라데이션 오버레이 |
| 아이콘 | Lucide outline; 16px 글자 옆, 20px 버튼 안, 24px 툴바·탭 바; 선택된 탭만 filled |

## What never needs asking

Do not spend one of the five questions on a slot the defaults above already cover
well and the user is unlikely to care about (exact shadow values, easing curve,
icon stroke width). Put those in the draft as `(기본값)` and move on.
