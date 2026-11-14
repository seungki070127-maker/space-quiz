---
name: game-juice
description: Use when a game works but feels flat, or when adding feedback effects (손맛, 타격감, 연출, 효과음, 파티클, 화면 흔들림, 콤보 표시) — dependency-free screen shake, particles, tweens and WebAudio-synthesized sound that respect reduced motion and mute.
---

# 게임 연출 (손맛 / juice)

## 개요
같은 규칙이라도 **입력 즉시 반응하는 피드백**이 있으면 재미가 크게 달라진다. 외부 이미지·사운드 파일 없이 CSS, Canvas, WebAudio로 만든다.

## 피드백 체크리스트 (행동마다 최소 2개)
| 이벤트 | 시각 | 소리 |
|--------|------|------|
| 정답/득점 | 색 반짝임, 점수 숫자 튀어오름(+10 떠오름) | 높은 짧은 음 |
| 오답/피격 | 흔들림, 빨간 플래시 | 낮은 짧은 음 |
| 콤보/연속 | 콤보 배지 확대 | 음 높이 점점 상승 |
| 게임오버 | 느려짐·페이드 | 하강음 |

## 코드 조각
```js
// 1) 모션 설정 존중
const reduceMotion = matchMedia("(prefers-reduced-motion: reduce)").matches;

// 2) 화면 흔들림 (캔버스: render에서 ctx.translate(shake.x, shake.y))
let shakeT = 0; const shake = { x: 0, y: 0 };
function addShake(s) { if (!reduceMotion) shakeT = Math.min(shakeT + s, 0.4); }
function updateShake(dt) {
  shakeT = Math.max(0, shakeT - dt); const m = shakeT * 20;
  shake.x = (Math.random() * 2 - 1) * m; shake.y = (Math.random() * 2 - 1) * m;
}

// 3) 효과음 합성 — 첫 사용자 입력 이후에만 AudioContext 생성(자동재생 정책)
let ac, muted = false;
function beep(freq = 660, dur = 0.08, type = "square", vol = 0.06) {
  if (muted) return; ac ??= new AudioContext();
  const o = ac.createOscillator(), g = ac.createGain();
  o.type = type; o.frequency.value = freq;
  g.gain.setValueAtTime(vol, ac.currentTime);
  g.gain.exponentialRampToValueAtTime(0.0001, ac.currentTime + dur);
  o.connect(g).connect(ac.destination); o.start(); o.stop(ac.currentTime + dur);
}
const SFX = { ok: () => beep(880, .1, "triangle"), bad: () => beep(160, .18, "sawtooth"),
              combo: n => beep(523 * 2 ** (Math.min(n, 12) / 12), .08, "triangle") };
```
- DOM 게임은 CSS 클래스 + `@keyframes`(pop, shake, flash)로 충분하다. 클래스를 붙인 뒤 `animationend`에서 제거.
- 파티클은 배열 풀(최대 개수 제한, 예: 200)로 관리하고 수명이 다하면 제거.

## 필수 규칙
- **음소거 토글 버튼**(`<button aria-pressed>` 🔊/🔇) 제공. 설정은 `game-save`로 저장.
- `prefers-reduced-motion`이면 흔들림·파티클·바운스 끔. 색 변화와 텍스트 피드백은 유지 — 정보는 사라지면 안 된다.
- 연출은 정보 전달을 대신하지 않는다: 정답/오답은 색 + 아이콘/텍스트(✅/❌)로 함께 표시 (색맹 고려).
- 깜빡임은 초당 3회 이하 (광과민성).

## 흔한 실수
| 실수 | 대처 |
|------|------|
| 페이지 로드 시 AudioContext 생성 | 브라우저가 막음 — 첫 클릭/키 입력 후 생성 |
| 소리가 너무 큼 | gain 0.05~0.1 |
| 흔들림이 계속 누적 | 상한(0.4초) 두기 |
| reduced-motion에서 피드백 자체가 사라짐 | 움직임만 끄고 색·텍스트는 유지 |
