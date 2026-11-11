---
name: context-reset
description: Use when the conversation context is getting long, cluttered, or near compaction and work must continue in a fresh context, or when the user asks to reset/clear/초기화 context, save progress (진행사항 저장), or resume (이어하기/복원) from a saved progress note.
---

# 컨텍스트 초기화

## 개요
대화 내용을 버려도 작업이 끊기지 않도록, 진행사항을 **전보체**로 `.claude/progress.md`에 저장하고 새 컨텍스트에서 그 파일만 읽고 이어간다.

모델은 `/clear`를 직접 실행할 수 없다. 저장 후 사용자에게 `/clear` → `/context-reset 복원`을 안내한다.

## 모드
- 인자 없음 / `저장` → **저장 모드**
- `복원` / `resume` / `이어하기` → **복원 모드**

## 저장 모드
1. `git status`, `git diff --stat`, 최근 커밋으로 실제 상태 확인. 기억에만 의존 금지.
2. `.claude/progress.md`를 아래 형식으로 **덮어쓰기** (이전 내용 중 아직 유효한 것만 유지).
3. 사용자에게 한 줄 보고 + 다음 단계 안내:
   `저장 완료. /clear 후 "/context-reset 복원" 입력.`

### 파일 형식 (이 순서, 이 제목 그대로)
```markdown
# 진행사항 (YYYY-MM-DD HH:MM)
## 목표
- 사용자 요청 한 줄. 원문 핵심어 유지.
## 완료
- 퀴즈 데이터 배열 분리. index.html:120. 커밋 a1b2c3d.
## 진행중
- 결과화면 재시작 버튼. 포커스 이동 미처리.
## 다음
1. 재시작 시 점수 초기화 확인.
2. 브라우저 스모크 테스트.
## 결정·제약
- 외부 의존성 금지(AGENTS.md). 사용자 확정: 문항 10개.
## 막힘·주의
- 없음.
```

### 전보체 규칙
- 한 항목 = 한 줄. 조사·어미 최소화, 명사형/`~함`·`~완료`·`~미착수` 종결.
- 인사·서술·추측·사과 금지. 사실, 파일:줄, 커밋 해시, 명령어만.
- 빈 섹션은 `- 없음.`
- 전체 40줄 이내. 넘치면 완료 항목부터 병합.
- 비밀값(토큰·비밀번호) 기록 금지. 위치만 적음.

## 복원 모드
1. `.claude/progress.md` 읽기. 없으면 "저장된 진행사항 없음" 보고 후 중단.
2. `git status`/`git log -3`로 파일 내용과 실제 상태 대조. 불일치 시 보고.
3. 3줄 이내로 요약 보고 후 `## 다음` 1번부터 착수.

## 흔한 실수
| 실수 | 대처 |
|------|------|
| 대화 기억만으로 작성 | git으로 검증 후 작성 |
| 문장형 서술로 길어짐 | 항목당 한 줄, 40줄 제한 |
| "다음" 섹션이 모호함("마무리하기") | 바로 실행 가능한 구체 행동으로 |
| 사용자 결정사항 누락 | `결정·제약`에 반드시 기록 — 새 컨텍스트에서 재질문 방지 |
| 파일 누적(append) | 매번 덮어쓰기 |
