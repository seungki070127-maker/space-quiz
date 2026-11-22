# GLB(그림이 있는 Meshy 모델) → 상대 팀 선수 몸 (`BODY2_DATA`)

원래 그림(텍스처)을 그대로 입혀서 모델과 같은 모습으로 나오게 합니다.

1. GLB 에서 꺼내기: 정점 → `P0.npy`, 그림 좌표 → `UV0.npy`, 면 → `I0.npy`, 기본색 그림 → `base_full.png` (2048 으로 줄여 `tex.jpg`)
2. `python dec2.py 30000` — 이음매 정점을 합쳐 구멍 없이 면 3만 개로 줄이고, 새 꼭짓점의 그림 좌표는 같은 UV 조각의 원래 면에서 다시 구함 → `P.npy F.npy UV.npy`
3. `python bake_tex.py` — 관절(J) 위치와 뼈 가중치 → `body2.json` (그림은 base64 로 안에 넣음)

`body2.json` 내용을 `soccer3d.html` 의 `const BODY2_DATA=` 뒤에 붙여 넣으면 됩니다. 모델이 바뀌면 `bake_tex.py` 의 관절 위치를 새 모델에 맞게 고칩니다.
