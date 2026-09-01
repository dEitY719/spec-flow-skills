# reverse-engineering-analysis 사용 결과

> **한 줄 요약** — 기존 기능 하나(여기서는 `.yml` 워크플로 파일)를 받아 재구현
> 프롬프트가 담긴 `analysis.md` 를 생성합니다.

```
기능/파일 경로  ──▶  /spec-flow:reverse-engineering-analysis  ──▶  analysis.md
```

## 1. 실행한 명령

```
/spec-flow:reverse-engineering-analysis "<feature or file path>" [output directory]
```

이번 예시:

```
/spec-flow:reverse-engineering-analysis .github/workflows/validate.yml \
    docs/examples/reverse-engineering-analysis/
```

## 2. 입력

`.github/workflows/validate.yml` — 이 repo 의 CI 진입점(33줄). 검사 로직이 없고
`dEitY719/harness-skills` 의 재사용 워크플로를 `@main` 으로 호출하며 `plugin-name`
과 `allow-emoji-paths` 두 입력만 넘기는 얇은 호출자다. 흥미로운 동작이 이 repo
밖에 있어서 분석 대상으로 골랐다.

## 3. 결과

[`analysis.md`](../examples/reverse-engineering-analysis/analysis.md) — 312줄,
17,963바이트. 섹션: Overview / Key Libraries / How It Works / File Map /
**AI Implementation Prompt** / Notes.

확인된 내용 일부:

- 호출되는 재사용 워크플로를 로컬 클론에서 특정 SHA 기준으로 읽어 11개 검사의
  내부를 서술했고, 그 클론이 없었다면 알 수 없는 내용임을 문서에 명시했다.
- `@main` 핀 때문에 분석에 유효기간이 있다 — upstream 머지 시 이 repo 의 커밋
  변화 없이 CI 동작이 바뀐다.
- `jq`, `python3`, PyYAML, `shellcheck` 어디에도 버전 고정이 없다. PyYAML 은
  import 되지만 설치되지 않는다.
- 가장 긴 `SKILL.md` 가 100줄 제한 대비 99줄(`prd-to-trd`). 직접 재확인했다.

AI Implementation Prompt 섹션에 프로젝트 고유 절대경로가 없음을 확인했다.

**정직한 단서** — 이 실행은 `analysis.md` 를 끝까지 쓴 뒤 최종
`[OK] analysis written: <path>` 줄을 출력하기 전에 세션이 API 오류로 종료됐다.
산출물은 실물이고 내용도 검증했지만 콘솔 최종 판정 줄은 포착되지 않았다.
