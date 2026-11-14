---
name: game-save
description: Use when a game needs to remember things between visits (최고 점수, 랭킹, 설정, 음소거, 진행 저장, 이어하기) in a static page — safe versioned localStorage with try/catch and fallbacks.
---

# 게임 저장 (최고점·설정)

## 개요
서버 없는 정적 페이지이므로 `localStorage`를 쓴다. 단, 사생활 보호 모드·차단 설정에서 **읽기/쓰기가 예외를 던질 수 있으므로** 저장이 실패해도 게임은 정상 동작해야 한다.

## 코드
```js
const SAVE_KEY = "space-quiz:v1";            // 게임 이름 + 스키마 버전
const DEFAULT_SAVE = { best: 0, muted: false, plays: 0 };

function loadSave() {
  try {
    const raw = localStorage.getItem(SAVE_KEY);
    const data = raw ? JSON.parse(raw) : {};
    return { ...DEFAULT_SAVE, ...(data && typeof data === "object" ? data : {}) };
  } catch { return { ...DEFAULT_SAVE }; }
}
function writeSave(s) {
  try { localStorage.setItem(SAVE_KEY, JSON.stringify(s)); } catch { /* 저장 불가: 무시 */ }
}

const save = loadSave();
// 게임오버 시
const isNewBest = score > save.best;
if (isNewBest) save.best = score;
save.plays++; writeSave(save);
```

## 규칙
- 키에 **버전**을 넣는다. 저장 구조가 바뀌면 `v2`로 올리고 필요하면 `v1`을 읽어 변환.
- 불러온 값은 신뢰하지 않는다: 숫자는 `Number.isFinite`로 확인, 화면에 표시할 문자열(닉네임 등)은 `textContent`로만 출력.
- 저장은 의미 있는 시점에만 (게임오버, 설정 변경). 매 프레임 저장 금지.
- 신기록이면 결과 화면에 "🎉 최고 기록!"을 표시하고 `aria-live`로 안내.
- "기록 초기화" 버튼을 둘 경우 `confirm` 대신 화면 내 확인 단계를 둔다.
- 이름·이메일 등 개인정보는 저장하지 않는다.

## 확인
`game-playtest`에서: 한 판 → 새로고침 → 최고점 유지 확인, 그리고 `localStorage`가 막힌 상황(아래)에서도 에러 없이 동작 확인.
```js
await page.addInitScript(() => {
  Object.defineProperty(window, "localStorage", { get() { throw new Error("blocked"); } });
});
```

## 흔한 실수
| 실수 | 대처 |
|------|------|
| `JSON.parse` 예외로 게임 전체 멈춤 | try/catch + 기본값 병합 |
| 새 설정 필드가 옛 저장에 없어 `undefined` | `{...DEFAULT_SAVE, ...data}` |
| 퀴즈 진행 도중 상태까지 저장해 꼬임 | MVP는 최고점·설정만 |
