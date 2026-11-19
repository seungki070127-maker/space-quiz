// AnimationMixer로 Idle / Run / Sprint 를 "속도에 따라" 섞어 줍니다.
//
// 핵심 아이디어 (1차원 블렌드 스페이스):
//   속도 0 ───────── runSpeed ───────── sprintSpeed
//   Idle 100%        Run 100%           Sprint 100%
//   그 사이 속도에서는 양옆 두 애니메이션을 비율대로 섞습니다(weight 조절).
//
// crossFadeTo 는 "A에서 B로 정해진 시간 동안 넘어가기"에 좋고(예: 킥, 넘어지기),
// 이동처럼 속도가 계속 변하는 동작은 weight 를 직접 조절하는 쪽이 더 자연스럽습니다.
import * as THREE from 'three';
import { clamp, damp, invLerp } from './math.js';

const STATES = ['idle', 'run', 'sprint'];

export class PlayerAnimator {
  /**
   * @param {THREE.Object3D} model
   * @param {THREE.AnimationClip[]} clips GLTF에서 읽은 클립 목록
   * @param {object} animCfg CONFIG.animations
   * @param {object} blendCfg CONFIG.blend
   * @param {{runSpeed:number, sprintSpeed:number}} moveCfg 블렌드 기준 속도
   */
  constructor(model, clips, animCfg, blendCfg, moveCfg) {
    this.mixer = new THREE.AnimationMixer(model);
    this.animCfg = animCfg;
    this.blendCfg = blendCfg;
    this.moveCfg = moveCfg;

    this.actions = {};                                   // 상태 이름 → AnimationAction
    this.weights = { idle: 1, run: 0, sprint: 0 };       // 현재(부드럽게 변하는) 가중치
    this.rate = 1;                                       // 이동 애니메이션 재생 속도 배율

    for (const state of STATES) {
      const clip = THREE.AnimationClip.findByName(clips, animCfg[state].clip);
      if (!clip) { console.warn(`"${animCfg[state].clip}" 클립이 없습니다 (${state})`); continue; }
      const action = this.mixer.clipAction(clip);
      action.play();                                     // 전부 재생해 두고 weight 로만 보이게/안 보이게 조절
      action.setEffectiveWeight(this.weights[state]);
      this.actions[state] = action;
    }
    // sprint 클립이 없으면 run 을 빠르게 재생하는 것으로 대신합니다.
    this.hasSprint = !!this.actions.sprint;
  }

  /**
   * @param {number} dt
   * @param {number} speed 선수의 실제 이동 속도 (PlayerController.speed)
   */
  update(dt, speed) {
    const { runSpeed, sprintSpeed } = this.moveCfg;
    const w = this.weights;

    // 1) 속도로부터 "목표 가중치" 계산
    const moving = invLerp(0, runSpeed, speed);                          // 0 = 정지, 1 = run 속도 이상
    const sprinting = this.hasSprint ? invLerp(runSpeed, sprintSpeed, speed) : 0;
    const target = {
      idle: 1 - moving,
      run: moving * (1 - sprinting),
      sprint: moving * sprinting,
    };

    // 2) 현재 가중치를 목표로 부드럽게 이동 (갑자기 바뀌어 튀는 것 방지)
    const k = damp(this.blendCfg.smoothing, dt);
    let sum = 0;
    for (const s of STATES) { w[s] += (target[s] - w[s]) * k; sum += w[s]; }
    for (const s of STATES) w[s] /= sum || 1;                            // 합이 항상 1이 되게

    // 3) 재생 속도를 실제 이동 속도에 맞추기 (발 미끄러짐 방지)
    //    지금 섞인 동작이 "원래 표현하는 속도" = 각 클립 naturalSpeed 의 가중 평균
    const run = this.actions.run, sprint = this.actions.sprint;
    if (run) {
      const locoWeight = w.run + w.sprint;
      const mix = sprint && locoWeight > 0.001 ? w.sprint / locoWeight : 0;   // 0 = run 만, 1 = sprint 만
      const natural = THREE.MathUtils.lerp(
        this.animCfg.run.naturalSpeed, sprint ? this.animCfg.sprint.naturalSpeed : this.animCfg.run.naturalSpeed, mix);
      // 거의 서 있을 때(speed≈0)는 배율이 의미 없으므로 1로 둡니다.
      this.rate = speed > 0.1 ? clamp(speed / natural, this.blendCfg.minRate, this.blendCfg.maxRate) : 1;

      // 4) Run 과 Sprint 의 발 박자를 맞추기
      //    두 클립 길이가 달라도 "한 걸음 주기"가 같은 시간에 끝나도록 timeScale 을 각각 보정합니다.
      //    이렇게 하지 않으면 섞이는 동안 양발이 엇갈려 어색해집니다.
      //    (가중치가 0일 때도 계속 맞춰 둬야 다음에 섞일 때 박자가 어긋나지 않습니다.)
      const dRun = run.getClip().duration;
      const dSprint = sprint ? sprint.getClip().duration : dRun;
      const cycle = THREE.MathUtils.lerp(dRun, dSprint, mix);            // 지금 섞인 동작의 주기 길이
      run.timeScale = (dRun / cycle) * this.rate;
      if (sprint) sprint.timeScale = (dSprint / cycle) * this.rate;
    }

    // 5) 가중치 적용 후 믹서 진행
    for (const s of STATES) this.actions[s]?.setEffectiveWeight(w[s]);
    this.mixer.update(dt);
  }
}
