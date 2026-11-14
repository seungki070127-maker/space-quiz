---
name: game-balance
description: Use when tuning game difficulty, scoring, speed, spawn rates, timers, combos or rewards (난이도, 밸런스, 너무 쉬움/어려움, 점수 체계) — keeps all tunables in one CONFIG object, designs a difficulty curve, and verifies it with a quick headless simulation.
---

# 난이도·밸런스 조정

## 개요
감으로 숫자를 여기저기 바꾸면 무엇이 효과였는지 모른다. **모든 조정값을 `CONFIG` 한 곳에** 두고, 곡선을 설계하고, 숫자로 검증한다.

## 절차
1. 코드에서 하드코딩된 매직넘버를 찾아 `CONFIG`로 옮긴다 (동작은 그대로 유지).
2. 목표를 숫자로 정한다. 예: "처음 하는 사람이 첫 판 평균 60~90초 생존", "퀴즈 평균 정답률 60~70%".
3. 난이도 곡선을 함수로 표현한다.
4. 시뮬레이션이나 계산표로 목표와 비교한 뒤 한 번에 **한 값만** 바꾼다.
5. 변경 전/후 숫자를 사용자에게 표로 보고한다.

## 난이도 곡선 패턴
```js
const CONFIG = {
  base: { speed: 100, spawnEvery: 1.5 },
  growth: { speed: 0.04, spawn: 0.03 },   // 단계(레벨)당 증가율
  cap:   { speed: 320, spawnEvery: 0.35 },
};
const level = t => Math.floor(t / 15);               // 15초마다 1단계
const speedAt = t => Math.min(CONFIG.cap.speed, CONFIG.base.speed * (1 + CONFIG.growth.speed) ** level(t));
```
- **상한(cap) 필수** — 무한히 어려워지면 버그처럼 느껴진다.
- 톱니형 곡선: 어려운 구간 뒤에 짧은 휴식 구간을 두면 긴장감이 오래 유지된다.
- 퀴즈형: 문항 데이터에 `lv: 1~3`을 두고 쉬움→어려움 순으로 섞어 배치.

## 점수 체계
- 기본점수 + 보너스(속도·콤보)로 구성하되 **기본점수가 총점의 절반 이상**이 되게 — 보너스만 노리는 플레이 방지.
- 콤보 배율은 상한을 둔다 (예: 최대 x3).
- 결과 등급 구간은 실제 점수 분포를 보고 정한다.

## 빠른 시뮬레이션 (Node, 의존성 없음)
게임 로직이 DOM과 분리돼 있으면 `update()`를 그대로 돌려볼 수 있다. 분리가 어려우면 핵심 공식만 복사해 스크래치패드에 작성:
```js
// node sim.js — 무작위 플레이어 1000판 평균
let total = 0;
for (let n = 0; n < 1000; n++) { let t = 0, alive = true;
  while (alive && t < 600) { t += 1; if (Math.random() < hitChanceAt(t)) alive = false; }
  total += t; }
console.log("평균 생존(초)", (total / 1000).toFixed(1));
```
시뮬레이션 스크립트는 저장소가 아니라 스크래치패드에 둔다 (단일 index.html 규칙).

## 흔한 실수
| 실수 | 대처 |
|------|------|
| 여러 값 동시 변경 | 원인 파악 불가 — 한 번에 하나 |
| 곡선에 상한 없음 | cap 추가 |
| 개발자 실력 기준으로 조정 | 개발자는 상위 1% — 목표보다 약간 쉽게 |
| 밸런스 변경을 기능 변경처럼 몰래 반영 | 전/후 표로 사용자에게 보고 |
