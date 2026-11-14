---
name: game-loop
description: Use when implementing a game in a single self-contained index.html — game state machine (title/playing/paused/gameover), requestAnimationFrame loop with fixed timestep, keyboard/pointer/touch input, canvas or DOM rendering, pause on tab hide.
---

# 게임 루프 구현 (단일 index.html)

## 개요
외부 라이브러리 없이 `index.html` 하나에 CSS·JS를 담는다. 구조는 **CONFIG(데이터) → state(상태) → update(로직) → render(그리기)** 로 분리한다.

## 뼈대
```js
const CONFIG = { speed: 120, lives: 3, spawnEvery: 1.2 };   // 기획서의 숫자
const S = { mode: "title", t: 0, score: 0, lives: CONFIG.lives, entities: [] };

const STEP = 1 / 60; let acc = 0, last = 0;
function frame(now) {
  const dt = Math.min((now - last) / 1000, 0.25); last = now;
  if (S.mode === "playing") {
    acc += dt;
    while (acc >= STEP) { update(STEP); acc -= STEP; }   // 고정 타임스텝: 기기 속도와 무관
  }
  render();
  requestAnimationFrame(frame);
}
requestAnimationFrame(t => { last = t; requestAnimationFrame(frame); });

function setMode(m) { S.mode = m; /* 화면 전환, 포커스 이동, aria-live 안내 */ }
```

## 상태 머신
- `title` → `playing` ↔ `paused` → `gameover` → (재시작) `playing`
- 재시작은 **`resetState()` 한 함수**로 모든 값을 초기화한다. 흩어진 `x = 0` 금지.
- `document.addEventListener("visibilitychange", …)`: 탭이 숨으면 `paused`로.

## 입력
- 키보드: `keydown`/`keyup`으로 `keys` Set 관리, `e.code` 사용 (`ArrowLeft`, `Space`). 게임 키는 `preventDefault()`로 스크롤 방지.
- 포인터: `pointerdown`/`pointermove` 하나로 마우스·터치 통합. 캔버스엔 `touch-action: none`.
- `Esc`/`P` = 일시정지, `Enter`/`Space` = 시작·재시작.
- 화면 버튼(시작, 일시정지, 재시작)은 실제 `<button>`으로 — 키보드 포커스 가능해야 한다.

## 렌더링 선택
- 객체 수십 개 이하·UI 위주(퀴즈, 카드, 퍼즐) → **DOM**. 동적 텍스트는 `textContent`로 (innerHTML에 사용자/데이터 문자열 직접 넣지 않기).
- 많은 움직이는 객체(슈팅, 러너) → **`<canvas>`**. `devicePixelRatio` 반영해 선명하게, 창 크기 변경 시 리사이즈.
- 캔버스 게임도 점수·목숨·상태 안내는 DOM(`aria-live="polite"`)에 둔다 — 스크린리더용.

## 접근성·환경
- `prefers-reduced-motion`: 흔들림·파티클 줄이기 (`game-juice` 참고).
- `prefers-color-scheme`: CSS 변수로 색 지정, 캔버스는 `getComputedStyle`로 변수 읽어 그리기.
- 모바일 폭(360px)에서 가로 스크롤 없어야 한다.

## 완료 전
`game-playtest` 스킬로 시작→플레이→게임오버→재시작 흐름을 브라우저에서 확인한다.

## 흔한 실수
| 실수 | 대처 |
|------|------|
| `dt` 없이 프레임마다 고정 이동 | 120Hz 화면에서 2배 빨라짐 — 고정 타임스텝 |
| 재시작 시 타이머·배열 남음 | `resetState()`에서 전부 초기화, `setInterval` 쓰지 말 것 |
| 탭 복귀 시 거대한 dt로 순간이동 | `dt` 상한 0.25초 |
| 게임오버 후 키 입력이 계속 로직 실행 | 입력 핸들러에서 `S.mode` 확인 |
