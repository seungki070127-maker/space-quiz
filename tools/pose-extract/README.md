# 영상 → 포즈 동작 추출 (MediaPipe)

`soccer.html` 선수들의 달리기 동작(`RUN_CLIP_DATA`)을 영상에서 뽑을 때 쓴 스크립트입니다. 게임 실행에는 필요 없고, 다른 영상으로 동작을 다시 만들 때만 씁니다.

```bash
python3 -m venv venv && . venv/bin/activate
pip install mediapipe opencv-python-headless
curl -o pose_heavy.task https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_heavy/float16/latest/pose_landmarker_heavy.task
mkdir fr && ffmpeg -i 영상.mp4 -vf fps=30 fr/%04d.png

python detect.py 1 320      # 1) 프레임을 조각내 확대한 뒤 사람마다 관절 33개 인식 → det_1_320.json
python track.py             # 2) 프레임 사이에서 같은 선수를 이어 붙여 목록 출력 → tracks.json
python build_clip.py        # 3) 고른 구간을 깔끔한 한 사이클로 정리 → run_clip.json, clip_side.png(확인용 그림)
```

`run_clip.json` 의 내용을 `soccer.html` 의 `RUN_CLIP_DATA` 에 붙여 넣으면 됩니다.

## 영상마다 고쳐야 하는 값

- `detect.py` 의 `TILES`, `TS`, `UP`: 경기 화면이 있는 영역과 확대 배율 (지금은 1080×2340 세로 녹화 기준)
- `track.py` 의 프레임 범위와 파일 이름
- `build_clip.py` 첫 줄의 `T[4]` 와 `63 <= f <= 76`: 사용할 선수 번호와 프레임 구간. `track.py` 출력에서 오래 이어지고 `vis` 가 높고 `ankleSep std` 가 큰(다리를 크게 움직이는) 것을 고릅니다.

## build_clip.py 가 하는 일

1. 좌우 관절이 뒤바뀐 프레임 바로잡기
2. 몸 기준 축 잡기: 위는 몸통 평균 방향, 앞은 발이 가장 크게 흔들리는 방향 (옆에서 찍힌 영상은 깊이가 부정확해서)
3. 뼈 길이를 게임 선수 규격으로 고정하고 방향만 영상에서 가져오기
4. 반 걸음 구간을 찾아 좌우를 뒤집어 붙여 끊김 없는 한 사이클로 만들기
5. 떨림 제거, 발이 땅에 닿게 올리기, 얼굴·손·발끝 점 채우기

작은 화면 속 선수에서는 어깨·팔꿈치·손목·골반·무릎·발목 12개 관절만 믿을 만해서, 나머지 21개는 이 12개로부터 계산해 채웁니다.
