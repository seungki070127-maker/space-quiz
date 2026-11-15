# 영상 → 포즈 동작 추출 (MediaPipe)

`soccer.html` 선수들의 달리기 동작(`RUN_CLIP_DATA`)을 영상에서 뽑을 때 쓴 스크립트입니다. 게임 실행에는 필요 없고, 다른 영상으로 동작을 다시 만들 때만 씁니다.

```bash
python3 -m venv venv && . venv/bin/activate
pip install mediapipe opencv-python-headless
curl -o pose_heavy.task https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_heavy/float16/latest/pose_landmarker_heavy.task
mkdir fr && ffmpeg -i 영상.mp4 -vf fps=30 fr/%04d.png

python detect.py 1 79       # 1) 프레임을 조각내 확대한 뒤 사람마다 관절 33개 인식 → det_1_79.json
python track.py             # 2) 프레임 사이에서 같은 선수를 이어 붙여 목록 출력 → tracks.json
python build_clip.py 0      # 3) 고른 선수(번호)의 여러 걸음을 겹쳐 한 사이클로 정리 → run_clip.json, clip_side.png(확인용 그림)
```

`run_clip.json` 의 내용을 `soccer.html` 의 `RUN_CLIP_DATA` 에 붙여 넣으면 됩니다.

## 영상마다 고쳐야 하는 값

- `detect.py` 의 `TILES`, `TS`, `UP`: 경기 화면이 있는 영역과 확대 배율 (지금은 1080×2340 세로 녹화 기준)
- `detect.py` / `track.py` 의 프레임 범위와 파일 이름 (`det_1_79.json`), `detect.py` 의 사람 크기 제한(`h < 60 or h > 750`)
- `build_clip.py` 의 `LEVEL_CAMERA`(수평 정측면 영상이면 True, 위에서 내려다본 게임 화면이면 False), `ARM_FIX`(팔이 잘 안 잡힌 영상만 True)
- `python build_clip.py 0` 의 숫자: 사용할 선수 번호. `track.py` 출력에서 오래 이어지고 `vis` 가 높고 `ankleSep std` 가 큰(다리를 크게 움직이는) 것을 고릅니다. 여러 개를 적으면 함께 평균 냅니다.

## build_clip.py 가 하는 일

1. 몸 기준 축 잡기: 위는 몸통 평균 방향, 앞은 발이 가장 크게 흔들리는 방향 (옆에서 찍힌 영상은 깊이가 부정확해서)
2. 걸음 박자 찾기: 좌우와 무관한 "두 발목의 앞뒤 간격"에 주기 함수를 맞춰 한 걸음 길이와 각 프레임의 위상을 구함
3. 좌우 이름을 동작으로 다시 정하기: MediaPipe가 작은 선수의 좌우를 자주 헷갈려서, 위상을 기준으로 어느 다리·팔이 앞에 있어야 하는지로 판단
4. 모든 걸음을 반 사이클 위에 겹쳐 위상별 중앙값 내기 (잘못 인식된 프레임의 영향 감소)
5. 좌우를 뒤집어 나머지 반을 붙여 끊김 없는 한 사이클 만들기
6. 뼈 길이를 게임 선수 규격으로 고정, 팔 흔들림 보강(`ARM_GAIN`, `ELBOW_MIN`), 발이 땅에 닿게 올리기, 얼굴·손·발끝 점 채우기

작은 화면 속 선수에서는 어깨·팔꿈치·손목·골반·무릎·발목 12개 관절만 믿을 만해서, 나머지 21개는 이 12개로부터 계산해 채웁니다.
