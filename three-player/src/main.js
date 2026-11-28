// 시작점: 각 모듈을 만들고 매 프레임 순서대로 업데이트합니다.
//
//   Input ──▶ PlayerController ──▶ PlayerAnimator
//   (입력)     (속도·위치·방향)      (속도에 맞춰 애니메이션 블렌딩)
//                    │
//                    └──▶ ThirdPersonCamera (위치를 부드럽게 추적)
import * as THREE from 'three';
import { CONFIG } from './config.js';
import { Input } from './Input.js';
import { loadPlayer } from './loadPlayer.js';
import { PlayerController } from './PlayerController.js';
import { PlayerAnimator } from './PlayerAnimator.js';
import { ThirdPersonCamera } from './ThirdPersonCamera.js';
import { buildWorld } from './world.js';

const $ = (id) => document.getElementById(id);

// --- 렌더러 · 장면 · 카메라 ---
const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.setSize(innerWidth, innerHeight);
renderer.shadowMap.enabled = true;
document.body.prepend(renderer.domElement);

const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(50, innerWidth / innerHeight, 0.1, 300);
const { sun } = buildWorld(scene);

addEventListener('resize', () => {
  camera.aspect = innerWidth / innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(innerWidth, innerHeight);
});

// --- 선수 로드 후 각 시스템 생성 ---
$('msg').textContent = '선수 모델을 불러오는 중…';
const { model, clips, isPlaceholder } = await loadPlayer(CONFIG.model);
scene.add(model);
$('msg').textContent = isPlaceholder ? '모델을 불러오지 못해 임시 캐릭터로 표시합니다. config.js의 model.url을 확인하세요.' : '';

const input = new Input($('stick'), $('knob'));
const controller = new PlayerController(model, CONFIG.move, isPlaceholder ? 0 : CONFIG.model.yawOffset);
const animator = new PlayerAnimator(model, clips, CONFIG.animations, CONFIG.blend, CONFIG.move);
const follow = new ThirdPersonCamera(camera, CONFIG.camera);

// --- 메인 루프 ---
const clock = new THREE.Clock();
function frame() {
  // 탭을 오래 떠났다 돌아왔을 때 순간이동하지 않도록 dt 상한을 둡니다.
  const dt = Math.min(clock.getDelta(), 0.1);

  controller.update(dt, input.getMove(), follow.yaw);       // 1) 물리 이동
  animator.update(dt, controller.speed);                    // 2) 속도에 맞춰 애니메이션
  follow.update(dt, controller.position, controller.velocity, input.getCameraTurn());   // 3) 카메라

  // 그림자용 조명이 선수를 따라다니게 (그림자 범위를 작게 유지해 선명하게)
  sun.position.set(controller.position.x - 20, 30, controller.position.z + 12);
  sun.target.position.copy(controller.position);

  updateHud();
  renderer.render(scene, camera);
  requestAnimationFrame(frame);
}

function updateHud() {
  const w = animator.weights;
  $('hSpeed').textContent = controller.speed.toFixed(1);
  $('wIdle').style.width = `${w.idle * 100}%`;
  $('wRun').style.width = `${w.run * 100}%`;
  $('wSprint').style.width = `${w.sprint * 100}%`;
  $('hRate').textContent = animator.rate.toFixed(2);
}

// 콘솔에서 값을 들여다보거나 자동 테스트할 때 쓰는 손잡이
window.demo = { CONFIG, controller, animator, follow, camera, isPlaceholder };
requestAnimationFrame(frame);
