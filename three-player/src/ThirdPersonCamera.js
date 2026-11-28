// 선수를 부드럽게 따라가는 3인칭 카메라.
// 카메라는 "선수 뒤쪽 위"의 목표 지점으로 조금씩 다가가고, 선수보다 약간 앞을 바라봅니다.
import * as THREE from 'three';
import { damp } from './math.js';

export class ThirdPersonCamera {
  /**
   * @param {THREE.PerspectiveCamera} camera
   * @param {object} cfg CONFIG.camera
   */
  constructor(camera, cfg) {
    this.camera = camera;
    this.cfg = cfg;
    this.yaw = 0;                              // 카메라가 바라보는 수평 방향 (0이면 +Z)
    this.lookTarget = new THREE.Vector3();     // 지금 바라보는 지점 (부드럽게 이동)
    this._wantPos = new THREE.Vector3();
    this._wantLook = new THREE.Vector3();
    this._started = false;
  }

  /**
   * @param {number} dt
   * @param {THREE.Vector3} playerPos
   * @param {THREE.Vector3} playerVel 이동 방향을 미리 보여 주는 데 사용
   * @param {number} turnInput -1(Q) ~ +1(E)
   */
  update(dt, playerPos, playerVel, turnInput = 0) {
    const c = this.cfg;
    this.yaw -= turnInput * c.rotateSpeed * dt;

    // 목표 위치: 선수 위치에서 카메라 방향의 반대로 distance 만큼, 위로 height 만큼
    this._wantPos.set(
      playerPos.x - Math.sin(this.yaw) * c.distance,
      playerPos.y + c.height,
      playerPos.z - Math.cos(this.yaw) * c.distance,
    );
    // 목표 시선: 선수 가슴 높이 + 이동 방향으로 살짝 앞
    this._wantLook.copy(playerPos).addScaledVector(playerVel, c.lookAhead);
    this._wantLook.y += c.lookHeight;

    if (!this._started) {                      // 첫 프레임은 바로 제자리에
      this.camera.position.copy(this._wantPos);
      this.lookTarget.copy(this._wantLook);
      this._started = true;
    } else {
      // lerp(현재, 목표, 비율): 매 프레임 남은 거리의 일정 비율만 이동 → 부드럽게 따라감
      this.camera.position.lerp(this._wantPos, damp(c.positionDamping, dt));
      this.lookTarget.lerp(this._wantLook, damp(c.targetDamping, dt));
    }
    this.camera.lookAt(this.lookTarget);
  }
}
