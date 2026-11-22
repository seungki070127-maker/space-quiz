# FBX(Meshy, 모양만 있는 모델) → 게임 선수 몸 (지금 쓰는 모델)

```bash
pip install numpy fast-simplification matplotlib
python face.py 모델.fbx 4 18000 0.6   # 면 1만 8천 개로 줄이고 얼굴만 살짝 흐리게(반복 4번, 세기 0.6) → P_low.npy, F_low.npy, 비교 그림
# P_low → 게임 축([앞, 위, 오른쪽], 키 1.82m) 으로 바꿔 P.npy / F.npy 저장 (face.py 다음 단계, 아래 한 줄)
python -c "import numpy as np;P=np.load('P_low.npy');s=1.82/(P[:,2].ptp());np.save('P.npy',np.stack([-P[:,1],P[:,2]-P[:,2].min(),-P[:,0]],1)*s);np.save('F.npy',np.load('F_low.npy'))"
python bake_fbx.py                      # 관절·옷 경계를 이 모델에 맞춘 bake → body.json
```

- 얼굴을 덜/더 흐리게: `face.py` 의 두 번째 숫자(반복 횟수)와 네 번째 숫자(세기)를 바꿉니다.
- `bake_fbx.py` 는 `../bake.py` 와 같고, 관절(J)과 반바지 밑단(0.60m)·목선(1.555m)·소매(1.28m) 높이, 팔/다리 구분 규칙만 이 모델에 맞게 바꿨습니다.
