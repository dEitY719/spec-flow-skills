# reverse-engineering-analysis

## 한 줄 요약

기존 기능 하나를 분석해 `<output_dir>/analysis.md` 를 쓴다. 그 문서에서 가장 중요한
부분은 마지막의 **AI Implementation Prompt** — 다른 프로젝트의 AI 어시스턴트에
그대로 붙여넣으면 같은 기능을 다시 만들 수 있는 자기완결적 프롬프트다.

## 무엇을 만드는가

`analysis.md` 파일 1개. 필수 섹션은 다섯이다.

| 섹션 | 내용 |
|---|---|
| Overview | 1~2문장 요약 |
| Key Libraries | 표 — 라이브러리 / 버전 / 역할 |
| How It Works | 데이터 흐름과 핵심 추상화 |
| File Map | 소스 파일과 각 파일의 역할 |
| **AI Implementation Prompt** | 복사해 붙여넣는 재구현 프롬프트. 프로젝트 고유 경로가 없어야 한다 |

앞의 네 섹션은 마지막 섹션을 쓰기 위한 근거 수집이다. 분석 문서 자체가 목적이
아니라, **기능을 이식 가능한 형태로 만드는 것**이 목적이다.

## 언제 쓰고 언제 안 쓰는가

**쓴다** — 이 프로젝트에 있는 기능을 다른 프로젝트에서도 쓰고 싶을 때, 또는 남이
짜 놓은 기능의 동작 원리를 문서로 남겨야 할 때.

**안 쓴다:**

- 머지된 PR 을 추적 이슈로 되돌릴 때 → `pr-to-ssot-issue`. 저쪽은 결과물을 **명세**로
  되돌리고, 이 스킬은 결과물을 **재구현 프롬프트**로 되돌린다. 방향은 같지만 도착지가
  다르다.
- 아직 만들지 않은 기능을 설계할 때 → `prd-to-trd`. 이 스킬은 이미 존재하는 코드만
  다룬다.
- 코드베이스 전체를 이해하려 할 때. 입력은 기능 **하나**다.

## 호출 형식

```
/spec-flow:reverse-engineering-analysis "<feature or file path>" [output directory]
```

| 인자 | 필수 | 기본값 | 설명 |
|---|---|---|---|
| `<feature or file path>` | 예 | — | 기능 설명(키워드 검색) 또는 명시적 파일 경로 |
| `[output directory]` | 아니오 | `docs/` | `analysis.md` 를 쓸 디렉터리 |
| `help` / `-h` / `--help` | — | — | 도움말만 출력 |

입력 두 형태의 차이:

- **기능 설명** — `"frontend의 graph 기능"` 처럼 쓰면 Grep/Glob 으로 관련 파일을
  찾아낸다.
- **파일 경로** — `.github/workflows/ci.yml` 처럼 쓰면 검색 없이 바로 읽는다.

```
/spec-flow:reverse-engineering-analysis "frontend의 graph 기능" docs/feature/frontend-graph/
/spec-flow:reverse-engineering-analysis .github/workflows/ci.yml docs/feature/workflows-ci/
```

## 동작 단계

1. **Locate** — 키워드로 검색하거나 지정된 파일 경로를 바로 읽는다.
2. **Deep Dive** — 큰 파일은 import/export 를 먼저 훑고, 필요할 때만 본문을 읽는다.
3. **Extract Libraries** — import 문에서 라이브러리를 모으고, 패키지 매니페스트를
   **한 번만** 확인해 버전을 채운다.
4. **Explain Mechanism** — 데이터 흐름, 컴포넌트 간 인계 지점, 자명하지 않은 설계 선택.
5. **Generate AI Prompt** — 가장 중요한 단계. 자기완결적이고 바로 실행 가능해야 한다.

각 단계는 실패하면 그 자리에서 중단하고 어느 단계가 실패했는지 보고한다.

## 주의사항 / 제약

- **프롬프트에 프로젝트 고유 경로를 남기지 않는다.** 절대경로나 이 repo 에만 있는
  디렉터리 이름이 들어가면 다른 프로젝트에서 쓸 수 없다. 이식성이 품질 기준이다.
- **버전을 지어내지 않는다.** 매니페스트에서 확인되지 않으면 고정되지 않았다고 적는다.
- 대상이 다른 repo 의 리소스를 참조하는 경우(예: 재사용 워크플로), 그 내용을 볼 수
  없으면 추측하지 말고 "확인 불가"로 명시한다.
- 쓰기 전에 `references/output-template.md` 의 품질 체크리스트를 통과해야 한다.
- 출력은 `<output_dir>/analysis.md` 고정이다. 파일명을 바꾸지 않는다.
- 이 스킬은 원본 코드를 수정하지 않는다. 읽고 문서만 쓴다.

## 모델 권장

`SKILL.md` 의 메타데이터는 이 스킬만 **opus** 티어를 권장한다. 나머지 네 스킬은
sonnet 이다. 깊은 코드 분석이라 추론 표면이 넓기 때문이다.

## 이어지는 단계

`analysis.md` 를 열어 AI Implementation Prompt 섹션을 대상 프로젝트의 AI
어시스턴트에 붙여넣는다.
