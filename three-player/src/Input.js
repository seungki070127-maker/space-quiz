// 키보드(WASD/방향키)와 화면 조이스틱 입력을 하나의 "이동 벡터"로 합쳐 줍니다.
import { clamp } from './math.js';

export class Input {
  /**
   * @param {HTMLElement} stickEl 조이스틱 바탕 요소
   * @param {HTMLElement} knobEl  조이스틱 손잡이 요소
   */
  constructor(stickEl, knobEl) {
    this.keys = new Set();              // 지금 눌려 있는 키
    this.stick = { x: 0, y: 0, id: null };
    this.stickEl = stickEl;
    this.knobEl = knobEl;

    addEventListener('keydown', (e) => {
      if (e.code.startsWith('Arrow')) e.preventDefault();   // 방향키로 화면이 스크롤되지 않게
      this.keys.add(e.code);
    });
    addEventListener('keyup', (e) => this.keys.delete(e.code));
    addEventListener('blur', () => this.keys.clear());      // 창을 벗어나면 키가 눌린 채 남지 않게

    if (stickEl) this.#bindStick();
  }

  #bindStick() {
    const el = this.stickEl;
    const radius = () => el.clientWidth / 2;
    const move = (e) => {
      const r = el.getBoundingClientRect();
      let x = (e.clientX - (r.left + r.width / 2)) / radius();
      let y = (e.clientY - (r.top + r.height / 2)) / radius();
      const len = Math.hypot(x, y);
      if (len > 1) { x /= len; y /= len; }                 // 원 밖으로 못 나가게
      this.stick.x = x; this.stick.y = y;
      this.knobEl.style.transform = `translate(${x * radius() * 0.6}px, ${y * radius() * 0.6}px)`;
    };
    const end = (e) => {
      if (e.pointerId !== this.stick.id) return;
      this.stick.id = null; this.stick.x = this.stick.y = 0;
      this.knobEl.style.transform = '';
    };
    el.addEventListener('pointerdown', (e) => { this.stick.id = e.pointerId; el.setPointerCapture(e.pointerId); move(e); });
    el.addEventListener('pointermove', (e) => { if (e.pointerId === this.stick.id) move(e); });
    el.addEventListener('pointerup', end);
    el.addEventListener('pointercancel', end);
  }

  #down(...codes) { return codes.some((c) => this.keys.has(c)); }

  /**
   * 이동 입력을 돌려줍니다.
   * right: 오른쪽(+) / 왼쪽(-), forward: 앞(+) / 뒤(-), 둘 다 -1 ~ 1
   * strength: 입력 세기 0 ~ 1, sprint: 달리기 여부
   */
  getMove() {
    let right = this.stick.x;
    let forward = -this.stick.y;                             // 화면 위쪽 = 앞
    if (this.#down('KeyD', 'ArrowRight')) right += 1;
    if (this.#down('KeyA', 'ArrowLeft')) right -= 1;
    if (this.#down('KeyW', 'ArrowUp')) forward += 1;
    if (this.#down('KeyS', 'ArrowDown')) forward -= 1;

    const len = Math.hypot(right, forward);
    if (len > 1) { right /= len; forward /= len; }           // 대각선이 더 빠르지 않게
    const strength = clamp(len, 0, 1);
    // Shift를 누르거나, 조이스틱을 끝까지 밀면 스프린트
    const sprint = this.#down('ShiftLeft', 'ShiftRight') || Math.hypot(this.stick.x, this.stick.y) > 0.92;
    return { right, forward, strength, sprint };
  }

  /** 카메라 회전 입력: Q = -1, E = +1 */
  getCameraTurn() {
    return (this.#down('KeyE') ? 1 : 0) - (this.#down('KeyQ') ? 1 : 0);
  }
}
