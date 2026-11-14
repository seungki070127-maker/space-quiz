---
name: game-playtest
description: Use after any game behavior change and before saying a game feature is done (테스트, 플레이테스트, 확인, 동작 검증) — drives the page in headless Chromium through start → play → feedback → score/progress → game over/results → restart, on desktop, mobile, dark mode and reduced motion, and checks console errors.
---

# 플레이테스트 (브라우저 스모크 테스트)

## 개요
"코드상 맞아 보임"은 확인이 아니다. 실제 브라우저에서 **처음부터 끝까지 한 판**을 돌리고, 결과를 증거(출력·스크린샷)로 보고한다. Playwright와 Chromium은 환경에 설치돼 있다 — `playwright install` 하지 말 것.

## 1단계: 범용 스모크 (항상)
```bash
node .claude/skills/game-playtest/smoke.cjs index.html <스크래치패드 경로>
```
- 데스크톱 / 모바일(360px, 터치) / 다크+reduced-motion 3가지로 실행
- 페이지 에러·콘솔 에러, 가로 스크롤 검사
- 보이는 버튼을 차례로 눌러 결과(재시작) 화면까지 진행, 시작·끝 스크린샷 저장
- 스크린샷은 스크래치패드에 저장하고 Read로 직접 열어 확인한다. 저장소에 커밋하지 않는다.

## 2단계: 게임별 흐름 검증 (동작을 바꿨다면 필수)
변경한 동작을 겨냥해 스크래치패드에 짧은 스크립트를 쓴다. 반드시 확인할 것:

| 항목 | 확인 방법 |
|------|-----------|
| 답/행동 피드백 | 정답·오답 각각 실행 후 클래스(`.correct`/`.wrong`)와 안내 문구 확인 |
| 점수·진행도 | 행동 전/후 점수 텍스트, 진행바 `aria-valuenow`/width 비교 |
| 결과 화면 | 최종 점수와 등급 문구가 기대값과 일치 |
| 재시작 | 재시작 후 점수 0, 1번 문제/초기 상태로 복귀 |
| 키보드만으로 | `page.keyboard.press("Tab"/"Enter"/"Space")`로 한 판 완주 가능 |
| 저장(있다면) | 새로고침 후 최고점 유지 (`game-save` 참고) |

현재 퀴즈 예시 — 정답을 모두 고르면 10/10이 나와야 한다:
```js
// 정답 인덱스는 페이지의 Q 배열에서 읽는다
const answers = await page.evaluate(() => Q.map(q => q.a));
for (const a of answers) {
  await page.locator(".opt").nth(a).click();
  await page.locator("#next").click();
}
if ((await page.textContent(".big")).trim() !== "10 / 10") throw new Error("만점 아님");
await page.locator("#again").click();
if ((await page.textContent("#sc")) !== "0") throw new Error("재시작 후 점수 초기화 안 됨");
```
실시간 게임(캔버스)은 `page.keyboard.down/up`과 `page.waitForTimeout`으로 입력을 흉내 내고, 가능하면 `window.S` 같은 상태 객체를 `page.evaluate`로 읽어 판정한다.

## 보고 형식
- 실행한 명령과 결과(✅/❌)를 그대로 적는다. 실패를 숨기지 않는다.
- 확인하지 못한 항목은 "미확인"으로 명시.

## 흔한 실수
| 실수 | 대처 |
|------|------|
| 첫 화면만 보고 통과 처리 | 결과 화면 + 재시작까지 |
| 데스크톱만 확인 | 360px 모바일, 다크모드 포함 |
| 애니메이션 중 클릭 실패 | `reducedMotion: "reduce"` 또는 짧은 대기 |
| 스크린샷을 찍고 안 봄 | Read로 열어 눈으로 확인 |
