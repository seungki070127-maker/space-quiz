# 3D 모델(STL) → 게임 선수 몸

`soccer3d.html` 의 `BODY_DATA` 를 만드는 스크립트입니다. 게임 실행에는 필요 없습니다.

```bash
pip install numpy fast-simplification
python prepare.py 모델.stl 14000   # 축 맞춤·크기(키 1.82m)·면 수 줄이기 → P.npy, F.npy
python bake.py                      # 뼈 가중치·부위(색)·상의 그림 좌표 → body.json
```

`body.json` 내용을 `soccer3d.html` 의 `const BODY_DATA=` 뒤에 붙여 넣으면 됩니다.

## 모델이 바뀌면 고칠 곳 (bake.py)

- `J`: 기준 자세 관절 위치(어깨·팔꿈치·손목·골반·무릎·발목·발). 모델 단면을 재서 맞춥니다.
- 부위 높이: 상의(0.94~1.565m), 반소매 끝(1.295m), 반바지(0.625~0.96m), 양말(0.10~0.43m), 축구화(0.075m 아래), 머리카락.

STL 에는 색이 없어서, 색은 게임 유니폼 색으로 칠합니다.
