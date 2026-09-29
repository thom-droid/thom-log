---
layout: post
title:  "AI-DLC와 Claude Code의 토큰 최적화 — RTK보다 먼저 해야 할 일"
date:   2026-09-28 15:00:00 +0900
categories: [ai, claude-code, productivity]
---

AI 에이전트로 개발하다 보면 “CLI 출력이 너무 길다”, “작업 하나에 왜 이렇게 많은 토큰이 쓰이지?”라는 질문을 하게 된다. Windows 환경에서 AI-DLC 2.8.2, Claude Code, RTK(Rust Token Killer)를 함께 사용하며 확인한 결론은 단순하다.

> RTK는 셸 출력량을 줄이는 도구이고, 전체 토큰 사용량은 workflow와 context 설계까지 함께 봐야 한다.

이 글에서는 RTK의 역할과 한계를 구분하고, AI-DLC 작업에서 실제 비용을 측정하는 방법과 우선순위가 높은 최적화 방법을 정리한다.

## 1. RTK가 줄이는 것과 줄이지 못하는 것

Claude Code가 셸 명령을 실행하면 일반적으로 다음과 같은 흐름을 거친다.

```text
Claude Code → Bash command → stdout → Claude context
```

RTK를 사용하면 셸 명령의 출력을 압축해 Claude의 context로 전달한다.

```text
Claude Code → Bash command → RTK → 압축된 stdout → Claude context
```

예를 들어 `git diff`, `git status`, 테스트 로그, `docker logs`, 재귀 검색 결과처럼 출력이 긴 명령에서 효과가 크다.

Windows에서 전역 hook을 초기화하는 예시는 다음과 같다.

```powershell
rtk init -g
rtk --version
rtk gain
```

다만 RTK의 절감률을 Claude 전체 토큰 절감률로 해석하면 안 된다. Claude가 사용하는 전체 context에는 다음 항목도 포함된다.

- system prompt와 Claude Code instructions
- `CLAUDE.md`와 AI-DLC stage instructions
- 대화 history와 workflow 상태
- Read, Grep, Glob 결과
- subagent prompt와 결과
- model output, thinking, prompt cache

가령 전체 input이 200k이고 셸 출력이 60k라고 하자. RTK가 셸 출력의 80%를 줄여도 셸 출력은 12k가 될 뿐이다. 전체 input은 약 152k가 되어 전체 절감률은 약 24%다.

```text
RTK 셸 출력 절감률 ≠ Claude 전체 토큰 절감률
```

## 2. 가장 먼저 확인할 지표: usage ledger

AI-DLC와 Claude Code를 함께 사용할 때는 RTK의 자체 통계와 Claude 전체 사용량을 분리해서 기록해야 한다. AI-DLC 세션에서 다음 파일을 확인할 수 있다.

```text
aidlc/.aidlc-sessions/usage-ledger.json
```

주요 항목은 다음과 같다.

- input tokens
- output tokens
- model
- stage와 workflow
- session
- estimated cost

usage tracking을 끄는 환경 변수나 설정이 있다면 측정 전에 제거한다.

```json
{
  "env": {
    "AIDLC_DISABLE_USAGE_TRACKING": "1"
  }
}
```

실제 비용을 판단할 때는 `rtk gain`의 절감량보다 usage ledger의 전체 input token 변화를 우선해서 본다.

## 3. RTK 효과를 확인하는 A/B 테스트

RTK의 효과를 체감이 아니라 숫자로 확인하려면 같은 commit에서 비슷한 작업을 두 번 실행한다.

### RTK OFF

1. 기준 commit으로 이동한다.
2. RTK를 비활성화한다.
3. 같은 AI-DLC task를 실행한다.
4. usage ledger에서 input, output, total token을 기록한다.

### RTK ON

동일한 commit으로 복원한 뒤 RTK를 활성화하고 같은 task를 다시 실행한다.

```powershell
git reset --hard <same-commit>
rtk gain
```

비교 표는 다음처럼 작성할 수 있다.

| 지표 | RTK OFF | RTK ON | 변화 |
|---|---:|---:|---:|
| Claude input | 180k | 141k | -21.7% |
| Claude output | 23k | 22k | -4.3% |
| 총 token | 203k | 163k | -19.7% |
| Bash output | 51k | 11k | -78.4% |

여기서 가장 중요한 운영 지표는 `Claude 전체 input token 감소율`이다. 셸 출력 절감량은 원인 분석에 유용하지만, 실제 context와 비용이 얼마나 줄었는지는 usage ledger로 확인해야 한다.

## 4. 모든 출력이 RTK의 대상은 아니다

RTK는 주로 Bash tool call의 출력에 개입한다. Claude Code의 builtin 도구인 `Read`, `Grep`, `Glob`은 일반적으로 RTK Bash hook의 대상이 아니다.

따라서 다음 명령은 RTK 효과가 큰 편이다.

```text
git diff, git status
mvn test, gradle build, npm test
docker logs
find, recursive grep
```

반대로 모든 파일 읽기를 무조건 `rtk cat`으로 바꿀 필요는 없다. Claude의 builtin 도구가 필요한 범위만 읽어 준다면 오히려 더 효율적일 수 있다. 중요한 것은 “모든 출력을 압축한다”가 아니라 “context에 들어가는 불필요한 출력을 줄인다”는 원칙이다.

## 5. 가장 큰 차이를 만드는 것은 workflow profile

AI-DLC 작업에서 토큰 사용량은 RTK보다 workflow profile에 더 크게 좌우될 수 있다. 작은 버그 수정에 33-stage workflow를 적용하면, 실제 변경보다 분석·검토·subagent context가 더 많이 쌓일 수 있다.

| Profile | Stage 수 | 적합한 작업 |
|---|---:|---|
| `bugfix` | 9 | 범위가 좁은 버그 수정과 회귀 테스트 |
| `express` | 10 | 기존 구조를 유지하는 작은 기능 |
| `refactor` | 10 | 동작을 유지하는 구조 개선 |
| `security-patch` | 10 | 영향 범위를 통제해야 하는 보안 수정 |
| `poc` | 8 | 짧은 검증용 구현 |
| `infra` | 13 | 인프라 관련 변경 |
| `mvp` | 23 | 중간 규모의 기능 구현 |
| `feature` | 33 | 새로운 subsystem이나 architecture 판단이 필요한 기능 |
| `enterprise` | 33 | 강한 추적성과 규제 요구가 있는 작업 |

작업 유형과 profile을 맞추는 것이 첫 번째 최적화다.

```text
일반 버그        → bugfix
작은 기존 기능   → express
리팩토링         → refactor
보안 취약점     → security-patch
신규 대규모 기능 → feature
규제·감사 대응  → enterprise
```

단순 작업에서 sensors, learnings, summary confirmation을 끄는 선택지도 있지만, 개별 옵션을 조정하기 전에 작업에 맞는 작은 profile을 고르는 편이 우선이다. production 변경에서는 sensors와 추적성의 가치가 토큰 절감보다 클 수 있다.

## 6. Prompt scope를 처음부터 좁히기

모호한 요청은 에이전트가 repository를 넓게 탐색하고, 이미 끝난 설계를 다시 검토하게 만든다.

```text
/aidlc bugfix Login doesn't work.
```

다음처럼 문제, 위치, 기대 동작, 제약 조건을 명시하면 탐색 범위와 반복 작업을 줄일 수 있다.

```text
/aidlc bugfix

Problem:
POST /login returns 500 when smsYn=Y.

Suspected location:
OtpAuthenticationSuccessHandler.java

Expected:
- ROLE_OTP_PENDING issued
- redirect /views/sms_verification.jsp

Constraints:
- Java 8
- Spring Security 5.8
- XML configuration unchanged
- add regression test

Do not redesign authentication architecture.
```

특히 다음 항목이 효과적이다.

- 문제와 재현 조건
- 예상 파일 또는 모듈
- expected behavior
- 기술적 제약
- 테스트 범위
- 변경하지 않을 영역

## 7. 지속 입력되는 context를 관리하기

`CLAUDE.md`는 매 작업에 반복해서 읽히므로 프로젝트 전체 문서를 넣기보다 항상 필요한 규칙만 남긴다.

```markdown
# Project
Java 17 / Spring Boot / PostgreSQL

# Rules
- Existing architecture first
- No new dependency without approval
- Run affected tests
- Follow existing package conventions

# References
- docs/architecture.md
- docs/db.md
```

상세 문서는 참조 파일로 분리하고, 필요한 stage에서만 읽게 한다.

또한 AI-DLC 일부 stage는 reviewer나 reverse engineering agent처럼 별도 context를 사용하는 subagent를 실행할 수 있다. 각 agent가 repository를 처음부터 다시 탐색하면 input과 cache token이 늘어난다. 작은 작업에 full `feature` workflow를 쓰지 않는 이유도 여기에 있다.

한 세션에 여러 작업을 계속 이어 붙이는 경우에는 논리 단위가 끝날 때 `/compact`를 활용한다. AI-DLC가 state와 artifact를 파일로 유지한다면 대화 context를 압축해도 workflow 상태를 복구할 수 있다.

## 8. Hook은 역할을 나눠서 확인하기

AI-DLC와 RTK는 같은 일을 하는 도구가 아니다.

```text
AI-DLC hook → workflow, state, usage tracking, sensors, audit
RTK hook    → Bash command output compression
```

가능한 구성은 다음과 같다.

```text
project settings → AI-DLC hooks
user settings    → RTK hooks
```

RTK 설치 후에는 기존 AI-DLC hook이 사라지지 않았는지 확인한다.

```powershell
aidlc --version
rtk --version
rtk gain
aidlc doctor
```

점검할 항목은 AI-DLC hook 정상 여부, RTK hook 추가 여부, PATH, Bash에서 `aidlc`와 `rtk` 실행 가능 여부다.

## 마무리: 실전 최적화 순서

AI-DLC와 Claude Code의 토큰을 줄일 때는 다음 순서가 재현성과 효과 면에서 좋다.

1. 작업에 맞는 AI-DLC profile을 선택한다.
2. prompt에 문제, 범위, 제약, 테스트를 명시한다.
3. 불필요한 source와 context read를 줄인다.
4. 긴 Bash 출력에 RTK를 적용한다.
5. subagent와 reviewer가 불필요한 작업인지 확인한다.
6. 긴 작업이 끝날 때 `/compact`를 사용한다.
7. usage ledger와 `rtk gain`을 함께 기록한다.

핵심은 다음 두 수치를 함께 보는 것이다.

```text
RTK가 shell output을 얼마나 줄였는가
+
Claude 전체 input token이 실제로 얼마나 감소했는가
```

RTK는 좋은 출발점이지만 최종 해답은 아니다. 작은 작업에는 작은 workflow를 적용하고, context의 범위를 명확히 하며, usage ledger로 결과를 측정할 때 토큰 최적화가 일회성 요령이 아니라 팀의 운영 기준이 된다.

