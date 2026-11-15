# 3D 선수 이동 · 애니메이션 블렌딩 (Three.js)

Three.js로 만든 선수 캐릭터 이동 데모입니다. 속도에 따라 Idle / Run / Sprint 애니메이션이 부드럽게 섞이고, 3인칭 카메라가 선수를 따라갑니다.

> 이 폴더는 저장소의 다른 파일(`index.html` 퀴즈, `soccer.html`)과 달리 **외부 라이브러리(Three.js)** 를 사용하고 여러 파일로 나뉘어 있습니다.

## 실행

ES 모듈과 모델 파일을 불러와야 해서 파일을 더블클릭하면 동작하지 않습니다. 간단한 로컬 서버로 여세요.

```bash
cd three-player
python3 -m http.server 8000     # 또는: npx serve
# 브라우저에서 http://localhost:8000
```

| 조작 | 키 |
|---|---|
| 이동 | WASD / 방향키 / 화면 왼쪽 아래 조이스틱 |
| 스프린트 | Shift (조이스틱은 끝까지 밀기) |
| 카메라 회전 | Q / E |

## 구조

```
three-player/
├── index.html              화면 틀, Three.js 주소(import map), HUD
└── src/
    ├── main.js             시작점. 모듈을 만들고 매 프레임 순서대로 호출
    ├── config.js           조정값 모음 (속도, 블렌딩, 카메라, 모델 주소)
    ├── Input.js            키보드 + 조이스틱 → 이동 입력
    ├── loadPlayer.js       GLTFLoader로 모델·애니메이션 로드
    ├── PlayerController.js 물리 이동 (속도 벡터, 가속/감속, 방향 전환)
    ├── PlayerAnimator.js   AnimationMixer 블렌딩 + 재생 속도 동기화
    ├── ThirdPersonCamera.js 부드럽게 따라가는 3인칭 카메라
    ├── world.js            조명, 잔디, 경기장 선
    └── math.js             damp, clamp 등 작은 함수
```

매 프레임 흐름은 한 방향입니다.

```
Input ─▶ PlayerController ─▶ PlayerAnimator
(입력)    (속도·위치·방향)     (속도를 읽어 애니메이션 블렌딩)
                │
                └─▶ ThirdPersonCamera (위치를 읽어 추적)
```

이동과 애니메이션을 나눈 이유: 애니메이션은 "지금 속도가 얼마인가"만 알면 되므로, 나중에 AI 선수나 네트워크 선수가 생겨도 `PlayerAnimator`는 그대로 쓸 수 있습니다.

## 핵심 개념

### 1. 애니메이션 블렌딩 (PlayerAnimator.js)

세 애니메이션을 모두 재생해 두고 **가중치(weight)** 만 바꿉니다.

```
속도   0 ─────── runSpeed ─────── sprintSpeed
       Idle 100%   Run 100%        Sprint 100%
```

- 사이 속도에서는 양옆 두 동작을 비율대로 섞습니다.
- 가중치는 목표값으로 조금씩 따라가게 해서(`blend.smoothing`) 튀지 않습니다.
- `crossFadeTo`는 킥·넘어지기처럼 "A에서 B로 한 번 넘어가는" 동작에 알맞고, 속도가 계속 변하는 이동에는 가중치 조절이 더 자연스러워 이쪽을 썼습니다.

### 2. 이동 속도와 재생 속도 동기화

- 클립마다 "원래 표현하는 이동 속도"(`naturalSpeed`)를 적어 둡니다.
- 재생 배율 = 실제 속도 ÷ 지금 섞인 동작의 naturalSpeed. 선수가 빨라지면 다리도 빨리 움직여 **발 미끄러짐**이 줄어듭니다.
- Run과 Sprint는 클립 길이가 달라도 한 걸음 주기가 같은 시간에 끝나도록 `timeScale`을 따로 보정해서, 섞이는 동안 양발 박자가 맞습니다.

### 3. 물리 이동 (PlayerController.js)

- 입력 방향은 **카메라 기준**으로 해석합니다 (W = 화면 안쪽).
- 속도는 목표 속도로 "초당 최대 가속도만큼" 다가가서 관성이 생깁니다.
- 몸은 입력 방향이 아니라 **실제 이동 방향**을 부드럽게 따라 돕니다.
- 급하게 방향을 틀면 잠깐 느려집니다 (`turnSlowdown`).

### 4. 3인칭 카메라 (ThirdPersonCamera.js)

- 목표 위치(선수 뒤·위)와 목표 시선(선수 가슴 + 이동 방향 약간 앞)을 매 프레임 계산하고, `lerp`로 조금씩 다가갑니다.
- `damp(k, dt) = 1 - e^(-k·dt)` 를 써서 화면 주사율(60Hz/120Hz)이 달라도 같은 느낌으로 움직입니다.

## 내 모델로 바꾸기

1. `.glb` 파일을 `three-player/models/` 에 넣습니다.
2. `src/config.js` 의 `model.url` 을 `'./models/player.glb'` 로 바꿉니다.
3. 브라우저 콘솔에 찍히는 "불러온 애니메이션 클립" 이름을 보고 `animations` 의 `clip` 값을 맞춥니다.
4. 발이 미끄러져 보이면 `naturalSpeed` 를 조절합니다. 발이 뒤로 밀리면 값을 낮추고, 제자리에서 헛도는 것 같으면 높입니다.
5. 모델이 뒤로 달리면 `model.yawOffset` 을 `0` 또는 `Math.PI` 로 바꿉니다.

기본 모델은 three.js 공식 예제의 Soldier이며 Sprint 클립이 없어서 Walk를 run 자리에, Run을 sprint 자리에 연결해 두었습니다. 모델을 못 불러오면 파란 캡슐 모양의 임시 캐릭터로 이동과 카메라만 확인할 수 있습니다.
