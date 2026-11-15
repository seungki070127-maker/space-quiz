// 자주 쓰는 작은 수학 함수들

/** 프레임 속도와 무관한 "부드럽게 따라가기" 비율. lerp(a, b, damp(k, dt)) 형태로 씁니다. */
export const damp = (k, dt) => 1 - Math.exp(-k * dt);

export const clamp = (v, min, max) => Math.min(max, Math.max(min, v));

/** 0~1 사이로 정규화: v가 a면 0, b면 1 */
export const invLerp = (a, b, v) => clamp((v - a) / (b - a), 0, 1);

/** 두 각도의 차이를 -π ~ π 로 (가까운 쪽으로 돌기 위해) */
export const angleDelta = (from, to) => {
  const d = to - from;
  return Math.atan2(Math.sin(d), Math.cos(d));
};
