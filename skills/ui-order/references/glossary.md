# UI/UX glossary (condensed)

Step 1 uses this to turn a vague word into a component name. Format:
한글 용어 (English) — 한 줄 뜻. Paraphrased from "바이브 코더를 위한 UI/UX 용어 사전"
(geniuskey, https://geniuskey.github.io/vibe-coding/ui-ux/).

## 모호한 말 -> 정확한 말

| 사용자가 한 말 | 주문서에 쓸 말 |
|----------------|----------------|
| "좀 예쁘게 해줘" | 간격 8의 배수로 통일, radius 12px, 그림자 약하게, 글자 4단계 타입 스케일, 행간 1.6 |
| "왼쪽에 메뉴 같은 거" | 240px 고정 사이드바 + 현재 항목 active 표시, 1024 미만은 드로어 |
| "버튼 좀 많이" | primary 1 + ghost 취소 1, 나머지 명령은 더보기 드롭다운 메뉴 |
| "로딩이 이상해" | 목록은 스켈레톤, 0건은 엠프티 스테이트, 실패는 재시도 버튼이 있는 에러 상태 |
| "알림 띄워줘" | 저장 성공은 토스트, 삭제 확인은 모달, 지속 경고는 상단 배너 — 어느 것인지 확인 |
| "폰에서도 되게" | 모바일 퍼스트, 브레이크포인트 640 / 1024, 드로어 또는 하단 탭, 세이프 에어리어 여백 |
| "세련되게", "고급스럽게" | 스타일 이름 (미니멀 등) 또는 레퍼런스 앱 이름 + 200ms ease-out + 약한 그림자 |
| "글씨 좀 예쁘게" | 행간 · 굵기 단계 · 제목/본문/캡션 위계 |

## 헷갈리는 짝

| 짝 | 구분 기준 |
|----|-----------|
| 모달 / 팝오버 | 모달은 스크림으로 뒤를 막는다; 팝오버는 막지 않고 붙어서 뜬다 |
| 토스트 / 배너 | 토스트는 잠깐 뒤 사라진다; 배너는 자리를 차지하고 남는다 |
| 탭 / 세그먼티드 | 탭은 다른 내용으로 이동; 세그먼티드는 같은 내용의 보기 방식만 바꾼다 |
| 사이드바 / 드로어 | 사이드바는 늘 보인다; 드로어는 열어야 나온다 |
| 칩 / 배지 | 칩은 누를 수 있는 라벨; 배지는 숫자·점 표시 |
| 플레이스홀더 / 레이블 | 플레이스홀더는 입력하면 사라지므로 레이블이 따로 필요하다 |
| 스피너 / 스켈레톤 | 스피너는 "기다려"; 스켈레톤은 "이런 모양이 온다" |

## 레이아웃

- 뷰포트 (viewport) — 브라우저에서 실제로 보이는 영역
- 컨테이너 (container) — 폭을 제한하고 가운데 정렬하는 상자
- 그리드 · 컬럼 (grid / column) — 화면을 세로 n등분한 격자
- 거터 · gap (gutter) — 컬럼·요소 사이 간격
- padding / margin — 테두리 안쪽 여백 / 바깥 거리
- sticky / fixed / absolute — 스크롤 중 붙음 / 화면 고정 / 부모 기준 좌표
- z-index — 겹침 순서; overflow — 넘침 처리; truncate — 말줄임

## 화면 골격

- 헤더 · 앱 바 (header / app bar) — 맨 위 띠
- 사이드바 (sidebar) — 측면 내비 기둥; 레일 (rail) — 아이콘 폭만 남긴 사이드바
- 히어로 (hero) — 첫 화면의 큰 제목·이미지 영역
- 메인 (main) — 본문; 어사이드 · 패널 (aside / panel) — 본문 옆 보조 영역
- 푸터 (footer) — 맨 아래 띠

## 기기

- 베젤 (bezel) — 기기 하드웨어 테두리 (화면 안 여백이 아님)
- 노치 (notch) — 카메라가 화면을 차지한 자리
- 세이프 에어리어 (safe area) — 노치·홈 인디케이터를 피한 안전 영역
- 스테이터스 바 (status bar) — OS 가 쓰는 최상단 띠

## 화면 종류

- 랜딩 (landing) — 소개부터 가입까지 한 장
- 대시보드 (dashboard) — KPI + 추이 + 필터
- 목록-상세 (list-detail) — 왼쪽 목록, 오른쪽 상세
- 설정 (settings) — 섹션 목록 + 즉시 저장 폼
- 로그인 (auth) — 가운데 카드: 입력 2개 + 주 버튼 + SSO
- 온보딩 (onboarding) — 첫 사용 단계 안내
- 에러 페이지 (404) — 이유 + 홈으로 버튼
- 체크아웃 (checkout) — 입력 폼 + 고정 주문 요약

## 대시보드

- 필터 바 (filter bar) — 화면 전체 숫자를 거르는 상단 줄
- 날짜 범위 선택 (date range picker) — 시작~끝 + 프리셋
- KPI 카드 (stat card) — 핵심 숫자 하나, 3~4개가 한도
- 델타 (delta) — 전 기간 대비 증감 (지표마다 좋은 방향이 다를 수 있음)
- 스파크라인 (sparkline) — 축 없는 작은 추이선
- 차트 선택 — 추이 라인, 비교 바, 비율 도넛 (5조각 이하), 분포 히스토그램

## 버튼

- 주 버튼 (primary) — 화면의 핵심 행동 하나 (CTA)
- 보조 버튼 (secondary / outline) — 회색 또는 테두리만
- 고스트 · 텍스트 버튼 (ghost) — 배경 없이 글자만
- 위험 버튼 (destructive) — 되돌릴 수 없는 행동, 빨강
- 아이콘 버튼 (icon button) — 아이콘만; 더보기는 케밥 메뉴
- FAB — 떠 있는 원형 버튼 (Material 전용 문법)

## 폼

- 텍스트 필드 (input) — 레이블 / 플레이스홀더 / 헬퍼 텍스트 3단
- 체크박스 (checkbox) — 다중 선택; 라디오 (radio) — 단일 선택
- 스위치 (switch) — 누르는 즉시 적용되는 켬/끔
- 슬라이더 (slider) — 범위 값
- 셀렉트 (select) — 목록 선택; 콤보박스 (combobox) — 검색되는 셀렉트
- 유효성 검증 (validation) — 틀린 입력의 테두리·메시지 표시

## 내비게이션

- 탭 (tabs), 세그먼티드 컨트롤 (segmented control)
- 브레드크럼 (breadcrumb) — 현재 경로
- 페이지네이션 (pagination), 무한 스크롤 (infinite scroll), 더 보기 (load more)
- 드롭다운 메뉴 (menu), 컨텍스트 메뉴 (context menu)
- 스테퍼 · 위저드 (stepper) — 단계 진행
- 드로어 (drawer) + 스크림 (scrim); 하단 탭 (bottom navigation)

## 콘텐츠

- 카드 (card), 리스트 아이템 (list item, leading/trailing 요소)
- 테이블 · 데이터 그리드 (table / data grid) — 정렬·필터·고정 헤더
- 아바타 (avatar), 배지 (badge), 칩 · 태그 (chip / tag)
- 툴팁 (tooltip) — 짧은 hover 설명
- 아코디언 (accordion) — 접고 펴기
- 캐러셀 (carousel) — 좌우 넘기기 + 페이지 인디케이터

## 오버레이

- 모달 · 다이얼로그 (modal) — 답할 때까지 뒤를 막음; 컨펌 다이얼로그
- 팝오버 (popover) — 요소 옆에 붙는 논모달 패널
- 바텀 시트 · 액션 시트 (bottom sheet) — 아래에서 올라오는 패널
- 토스트 · 스낵바 (toast / snackbar) — 잠깐 뜨는 알림 (스낵바는 되돌리기 포함)
- 배너 · 얼럿 (banner / alert) — 남아 있는 안내 띠

## 대기 · 빈칸

- 스피너 (spinner) — 짧은 대기
- 프로그레스 바 (progress bar) — 끝이 보이는 작업
- 스켈레톤 (skeleton) — 들어올 내용의 회색 뼈대
- 엠프티 스테이트 (empty state) — 0건 화면 + 다음 행동
- 에러 상태 (error state) — 실패 이유 + 재시도

## 이미지 · 아이콘

- 종횡비 (aspect ratio), object-fit cover / contain
- 히어로 이미지 오버레이 — 사진 위 글자 가독성
- 지연 로딩 (lazy loading), 이미지 플레이스홀더
- 아이콘 세트 — Lucide (웹), Material Symbols, SF Symbols; 아웃라인 / 필드
- 파비콘 (favicon), OG 이미지 (og:image)

## 고급 부품 (이름을 대야 나온다)

- 날짜 범위 선택 (date range picker)
- 파일 드롭존 (dropzone) + 드래그 오버 상태
- 태그 입력 · 오토컴플리트 (tag input / autocomplete)
- 커맨드 팔레트 (command palette, Ctrl/Cmd+K)
- 드래그 앤 드롭 정렬 (sortable)
- 인라인 편집 (inline edit)
- 스와이프 액션 (swipe action)

## 상태

- default, hover (마우스), focus / focus-visible (키보드), active / pressed,
  disabled, loading, success, error

## 토큰

- 간격 스케일 (spacing scale) — 4 / 8 / 16 / 24 / 40
- 라운드 (radius) — 0 / 6 / 12 / 20 / 999(pill)
- 그림자 · 높이 (elevation) — 0~3 단계
- 타입 스케일 (type scale) — Display / Heading / Body / Caption
- 컬러 역할 (color role) — primary, surface, on-surface, muted, semantic (success / warning / danger / info)

## 타이포그래피

- 서체 (font family) — sans-serif 기본, serif 읽을거리, monospace 코드; 한글은 Pretendard
- 굵기 (weight) — 본문 400, 제목 700~800, 한 화면 2~3단계
- 행간 (line height) — 본문 1.5~1.7
- 자간 (letter spacing) — 큰 제목은 살짝 조임
- 말줄임 (truncate / line-clamp)
- 위계 (hierarchy) — 크기·굵기·색으로 읽는 순서
- 숫자 정렬 (tabular-nums)

## 반응형

- 브레이크포인트 (breakpoint) — 레이아웃이 바뀌는 폭
- 모바일 퍼스트 (mobile first) — 좁은 화면부터
- 플루이드 / 고정 (fluid / fixed) — 늘어나는 값 / 픽셀 고정값
- 구간 예 — 모바일 1열 · 태블릿 2열 · 데스크톱 3열 · 와이드는 컨테이너 폭 제한

## 테마 · 스타일

- 머티리얼 (Material 3), 쿠퍼티노 (Cupertino / HIG), 플루언트 (Fluent 2) — 섞지 않는다
- Tailwind CSS (유틸리티 클래스), shadcn/ui (현대 SaaS 기본값), Ant Design / MUI (관리 도구)
- 다크 모드 (dark mode) — 테마와 별개인 밝기 축
- 스타일 이름 — 미니멀 · 플랫, 글래스모피즘, 뉴모피즘 (명암비 문제), 네오 브루탈리즘, 벤토 그리드

## 색 · 모션

- 헥사 코드, on-color (색 위 글자색), 명암비 (contrast), semantic 색, 그라데이션, opacity
- transition 200ms, duration 150~300ms, easing ease-out, 마이크로 인터랙션
- reduced motion (prefers-reduced-motion) — 존중해야 한다

## 접근성

- 포커스 링 (focus ring) — 지우지 않는다
- 탭 순서 (tab order) — 보이는 순서와 같게
- 명암비 — 본문 4.5:1, 큰 글자 3:1
- 터치 타깃 — 44x44px 이상
- 대체 텍스트 · aria-label — 이미지와 아이콘 버튼의 이름
- 색에만 의존하지 않기 — 아이콘·글자를 함께

## UX

- 와이어프레임 (wireframe) → 목업 (mockup) → 프로토타입 (prototype)
- 유저 플로 (user flow), 정보 구조 (IA)
- 어포던스 (affordance) — 눌릴 것처럼 보이는 성질
- CTA — 화면당 하나의 핵심 행동
- 해피 패스 (happy path) — AI 는 이것만 만든다; 예외는 요구해야 나온다
- 피드백 (feedback) — 누르면 반응이 있어야 한다

## 이름을 모를 때

번호를 단 스크린샷, 레퍼런스 앱 이름 ("Linear 사이드바처럼"), 브라우저 요소 검사,
컴포넌트 갤러리, 또는 "이 화면 각 부분의 UI 용어를 알려줘" 같은 역질문.
