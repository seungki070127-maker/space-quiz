// 선수의 "물리 이동"을 담당합니다: 속도 벡터, 가속/감속, 방향 전환.
// 애니메이션은 전혀 모릅니다. 대신 현재 속도(speed)를 PlayerAnimator가 읽어 갑니다.
import * as THREE from 'three';
import { clamp, damp, angleDelta } from './math.js';

export class PlayerController {
  /**
   * @param {THREE.Object3D} model 움직일 모델
   * @param {object} cfg CONFIG.move
   * @param {number} yawOffset 모델이 기본으로 바라보는 방향 보정값
   */
  constructor(model, cfg, yawOffset = 0) {
    this.model = model;
    this.cfg = cfg;
    this.yawOffset = yawOffset;

    this.position = new THREE.Vector3();   // 현재 위치
    this.velocity = new THREE.Vector3();   // 현재 속도 벡터 (m/s)
    this.heading = 0;                      // 몸이 바라보는 방향(yaw). 0이면 +Z
    this.speed = 0;                        // 속도 크기 (애니메이션이 사용)

    this._desired = new THREE.Vector3();   // 매 프레임 재사용하는 임시 벡터
  }

  /**
   * @param {number} dt 지난 프레임 시간(초)
   * @param {{right:number, forward:number, strength:number, sprint:boolean}} input
   * @param {number} cameraYaw 카메라가 바라보는 수평 방향. 입력을 "화면 기준"으로 바꾸는 데 씁니다.
   */
  update(dt, input, cameraYaw) {
    const c = this.cfg;

    // 1) 입력(화면 기준)을 세계 좌표의 방향으로 변환
    //    카메라 앞 방향 f = (sin, 0, cos), 오른쪽 r = (-cos, 0, sin)
    const sin = Math.sin(cameraYaw), cos = Math.cos(cameraYaw);
    const dirX = sin * input.forward - cos * input.right;
    const dirZ = cos * input.forward + sin * input.right;

    // 2) 목표 속도 = 방향 × (걷기 또는 스프린트 최고 속도) × 입력 세기
    let targetSpeed = (input.sprint ? c.sprintSpeed : c.runSpeed) * input.strength;

    //    급하게 방향을 틀면 잠깐 느려지게 해서 "미끄러지며 도는" 느낌을 줄입니다.
    if (input.strength > 0.01 && this.speed > 0.5) {
      const wantYaw = Math.atan2(dirX, dirZ);
      const turn = Math.abs(angleDelta(this.heading, wantYaw)) / Math.PI;   // 0(같은 방향) ~ 1(정반대)
      targetSpeed *= 1 - c.turnSlowdown * turn;
    }
    const len = Math.hypot(dirX, dirZ) || 1;
    this._desired.set((dirX / len) * targetSpeed, 0, (dirZ / len) * targetSpeed);

    // 3) 현재 속도를 목표 속도 쪽으로 "초당 최대 a 만큼만" 바꿉니다 → 관성이 생깁니다.
    const speedingUp = this._desired.lengthSq() > this.velocity.lengthSq();
    const maxChange = (speedingUp ? c.acceleration : c.deceleration) * dt;
    const diff = this._desired.sub(this.velocity);            // 목표 - 현재
    const diffLen = diff.length();
    if (diffLen <= maxChange) this.velocity.add(diff);
    else this.velocity.addScaledVector(diff, maxChange / diffLen);

    // 4) 위치 = 위치 + 속도 × 시간
    this.position.addScaledVector(this.velocity, dt);
    this.position.x = clamp(this.position.x, -c.bounds.x, c.bounds.x);
    this.position.z = clamp(this.position.z, -c.bounds.z, c.bounds.z);
    this.speed = this.velocity.length();

    // 5) 몸은 "실제로 움직이는 방향"을 부드럽게 따라 돕니다.
    if (this.speed > 0.2) {
      const moveYaw = Math.atan2(this.velocity.x, this.velocity.z);
      this.heading += angleDelta(this.heading, moveYaw) * damp(c.turnRate, dt);
    }

    // 6) 계산 결과를 모델에 반영
    this.model.position.copy(this.position);
    this.model.rotation.y = this.heading + this.yawOffset;
  }
}
