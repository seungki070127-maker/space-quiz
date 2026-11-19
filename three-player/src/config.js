// 모든 조정값을 한곳에 모아 둔 파일입니다. 숫자만 바꿔서 느낌을 튜닝하세요.
// 단위: 거리 m, 속도 m/s, 각도 rad, 시간 초

export const CONFIG = {
  model: {
    // 선수 모델(.glb) 주소. 자기 모델로 바꾸려면 예: './models/player.glb'
    // 기본값은 three.js 공식 예제 모델(Soldier)입니다. 데모 확인용이니 실제 게임에선 교체하세요.
    url: 'https://threejs.org/examples/models/gltf/Soldier.glb',
    scale: 1,
    // 모델이 처음에 바라보는 방향 보정. +Z를 보면 0, -Z를 보면 Math.PI (Soldier는 -Z를 봅니다)
    yawOffset: Math.PI,
  },

  // 상태별 애니메이션 클립 이름과 "그 클립이 원래 표현하는 이동 속도"(naturalSpeed).
  // naturalSpeed는 발이 미끄러지지 않게 재생 속도를 맞추는 기준입니다.
  // 데모 모델에는 Sprint 클립이 없어서 Walk → run, Run → sprint 로 대신 연결했습니다.
  // 자기 모델에 Idle / Run / Sprint 클립이 있다면 clip 이름만 바꾸면 됩니다.
  animations: {
    idle:   { clip: 'Idle' },
    run:    { clip: 'Walk', naturalSpeed: 1.7 },
    sprint: { clip: 'Run',  naturalSpeed: 4.4 },
  },

  move: {
    runSpeed: 2.2,        // 기본 이동 최고 속도
    sprintSpeed: 6.0,     // Shift(또는 조이스틱 끝까지) 최고 속도
    acceleration: 9,      // 가속 (m/s²)
    deceleration: 12,     // 감속 (m/s²) - 가속보다 크면 "딱 멈추는" 느낌
    turnRate: 9,          // 몸을 돌리는 빠르기 (클수록 즉시 돕니다)
    turnSlowdown: 0.45,   // 급하게 방향을 틀 때 속도를 줄이는 정도 (0 = 안 줄임)
    bounds: { x: 52, z: 34 },   // 움직일 수 있는 범위(경기장 절반 크기)
  },

  blend: {
    smoothing: 8,         // 가중치가 목표값을 따라가는 빠르기 (작을수록 천천히 섞임)
    minRate: 0.6,         // 애니메이션 재생 속도 하한
    maxRate: 1.6,         // 애니메이션 재생 속도 상한
  },

  camera: {
    distance: 9,          // 선수 뒤로 떨어진 거리
    height: 5,            // 카메라 높이
    lookHeight: 1.2,      // 바라보는 지점 높이(선수 가슴께)
    lookAhead: 0.35,      // 이동 방향을 미리 보여 주는 시간
    positionDamping: 4,   // 카메라 위치가 따라가는 빠르기
    targetDamping: 8,     // 바라보는 지점이 따라가는 빠르기
    rotateSpeed: 1.8,     // Q/E 회전 속도
  },
};
