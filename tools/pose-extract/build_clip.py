# 여러 걸음을 겹쳐 평균 내서 달리기 한 사이클을 만든다 (선수 한 명이 길게 달리는 영상용)
import json, sys, numpy as np, cv2
TRACKS = [int(a) for a in sys.argv[1:]] or [2]           # track.py 출력에서 고른 번호들
T = json.load(open("tracks.json"))
SW = [(11,12),(13,14),(15,16),(23,24),(25,26),(27,28),(29,30),(31,32)]
J = [11,12,13,14,15,16,23,24,25,26,27,28]
def swap(P):
    Q = P.copy()
    for a,b in SW: Q[a], Q[b] = P[b].copy(), P[a].copy()
    return Q
def mirror(P):
    Q = swap(P); Q[:,2] *= -1; return Q
def unit(v): return v/(np.linalg.norm(v)+1e-9)
def limbdir(v):                                             # 옆으로 벌어지는 성분은 작게 제한 (깊이 잡음 억제)
    v = unit(v); v[2] = np.clip(v[2], -0.22, 0.22); return unit(v)
def rebuild(P):                                             # 뼈 길이는 게임 선수 규격, 방향만 영상에서
    O = np.zeros((33,3)); side = np.array([0,0,1.0])
    spine = (P[11]+P[12])/2-(P[23]+P[24])/2; spine[2] = 0; spine = unit(spine)
    tw = np.clip((P[27,0]-P[28,0])*0.12, -0.12, 0.12)
    hip = unit(side + np.array([-tw,0,0])); sh = unit(side + np.array([tw*1.3,0,0]))
    O[24], O[23] = hip*0.115, -hip*0.115
    shc = spine*0.54; O[12], O[11] = shc+sh*0.21, shc-sh*0.21
    for hp,kn,an in ((23,25,27),(24,26,28)):
        O[kn] = O[hp]+limbdir(P[kn]-P[hp])*0.44; O[an] = O[kn]+limbdir(P[an]-P[kn])*0.44
    for s_,e,w in ((11,13,15),(12,14,16)):
        O[e] = O[s_]+limbdir(P[e]-P[s_])*0.27; O[w] = O[e]+limbdir(P[w]-P[e])*0.25
    return O

samples = []                                                # (반 사이클 위상 0~0.5, 자세)
for ti in TRACKS:
    tr = T[ti]; t = np.array([f for f, _ in tr], float); W = np.array([d["world"] for _, d in tr], float); n = len(W)
    for i in range(1, n):                                   # 좌우 뒤바뀜 1차 보정(연속성)
        if np.linalg.norm(swap(W[i])[J]-W[i-1][J]) < np.linalg.norm(W[i][J]-W[i-1][J]): W[i] = swap(W[i])
    hipC = (W[:,23]+W[:,24])/2; shC = (W[:,11]+W[:,12])/2
    u = (shC-hipC).mean(0); u /= np.linalg.norm(u)
    A = np.concatenate([W[:,27]-hipC, W[:,28]-hipC]); A = A - np.outer(A@u, u)
    f = np.linalg.svd(A - A.mean(0))[2][0]; f -= u*np.dot(f,u); f /= np.linalg.norm(f)
    votes = [np.dot((W[:,0]-shC).mean(0), f), np.dot((W[:,31]-W[:,29]).mean(0)+(W[:,32]-W[:,30]).mean(0), f)]
    if votes[0] < 0: f = -f
    th = np.radians(float(LEAN)) if (LEAN := 14) else 0
    u, f = np.cos(th)*u - np.sin(th)*f, np.cos(th)*f + np.sin(th)*u
    r = np.cross(f, u)
    if np.dot((W[:,24]-W[:,23]).mean(0), r) < 0: W = np.array([swap(w) for w in W])
    L = np.stack([(W-hipC[:,None])@f, (W-hipC[:,None])@u, (W-hipC[:,None])@r], -1)
    d = L[:,27,0]-L[:,28,0]; sep = np.abs(d)
    # 걸음 박자 찾기. MediaPipe가 좌우를 자주 헷갈리므로 좌우와 무관한 "두 발목의 앞뒤 간격"으로 맞춘다:
    #   sep ≈ a + b·cos(2π(t−t0)/Th),  Th = 반 사이클(한 걸음) 길이
    best = (-9, 0, 0)
    for Th in np.arange(4.0, 9.01, 0.05):
        for t0 in np.arange(0, Th, 0.1):
            c = np.corrcoef(sep, np.cos(2*np.pi*(t-t0)/Th))[0,1]
            if c > best[0]: best = (c, Th, t0)
    c, Th, t0 = best; v = ((t-t0)/Th) % 1                    # v=0: 두 발이 가장 벌어진 순간
    print(f"track {ti}: frames {int(t[0])}-{int(t[-1])} n={n} votes={np.round(votes,2)} step={Th:.2f} frames, cycle={2*Th/30:.2f}s, fit r={c:.2f}")
    for i in range(n):
        P = L[i].copy()
        # 좌우 이름을 영상 인식 결과 대신 동작으로 정한다. "기준 다리" = v=0 에서 앞에 있던 다리(이후 뒤로 밀려남)
        if 0.35 < v[i] < 0.65: lead_is_L = P[27,1] < P[28,1]          # 엇갈리는 순간: 땅을 딛고 있는(발목이 낮은) 쪽
        else: lead_is_L = (P[27,0] > P[28,0]) == (v[i] < 0.5)
        legs_swapped = not lead_is_L
        # 팔: 기준 다리와 같은 쪽 팔은 처음엔 뒤에 있다가 앞으로 나온다
        if 0.38 < v[i] < 0.62: arms_swapped = legs_swapped
        else: arms_swapped = not ((P[15,0] < P[16,0]) == (v[i] < 0.5))
        Q = P.copy()
        if legs_swapped:
            for a_, b_ in ((23,24),(25,26),(27,28)): Q[a_], Q[b_] = P[b_].copy(), P[a_].copy()
        if arms_swapped:
            for a_, b_ in ((11,12),(13,14),(15,16)): Q[a_], Q[b_] = P[b_].copy(), P[a_].copy()
        Q[:,2] = 0                                          # 좌우를 다시 정했으므로 옆 방향 성분은 버린다
        samples.append((v[i]*0.5, rebuild(Q)))              # 반 사이클 위상 0~0.5

H = 12; half = []
ph = np.array([s[0] for s in samples]); PP = np.array([s[1] for s in samples])
for b in range(H):
    c = (b+0.5)/H*0.5; w = 0.025
    while True:
        dd = np.abs(ph-c)
        m = dd < w
        if m.sum() >= 6 or w > 0.1: break
        w += 0.01
    half.append(np.median(PP[m], 0))                        # 중앙값: 잘못 인식된 프레임의 영향을 줄임
half = np.array(half); print("samples", len(samples), "per-bin ok")
cyc = np.concatenate([half, np.array([mirror(p) for p in half])])
k = np.array([1,2,1], float); k /= k.sum()
sm = sum(np.roll(cyc, s, 0)*w for s, w in zip((-1,0,1), k))
# 팔은 작은 화면에서 좌우가 자주 섞여 평균 내면 흔들림이 줄어든다 → 영상의 박자는 그대로 두고 폭만 키우고 팔꿈치를 굽힌다
ARM_GAIN, ELBOW_MIN = 2.0, 1.25
def ang(v): return np.arctan2(v[0], -v[1])                  # 아래 방향 기준, 앞쪽이 +
RB = np.array([rebuild(P) for P in sm])
for s_, e, w in ((11,13,15),(12,14,16)):
    up_a = np.array([ang(P[e]-P[s_]) for P in RB]); fo_a = np.array([ang(P[w]-P[e]) for P in RB])
    m = up_a.mean(); new_up = np.clip(m*0.3 + (up_a-m)*ARM_GAIN, -1.1, 1.0)
    bend = np.maximum(fo_a-up_a, ELBOW_MIN) + 0.25*np.maximum(0, new_up)
    for i, P in enumerate(RB):
        P[e] = P[s_] + np.array([np.sin(new_up[i]), -np.cos(new_up[i]), 0])*0.27
        fa = new_up[i]+bend[i]; P[w] = P[e] + np.array([np.sin(fa), -np.cos(fa), 0])*0.25
out = []
for P in RB:
    O = P.copy(); fwd = np.array([1.0,0,0]); up = np.array([0,1.0,0]); side = np.array([0,0,1.0])
    spine = unit((O[11]+O[12])/2-(O[23]+O[24])/2); head = (O[11]+O[12])/2 + spine*0.23
    O[0] = head+fwd*0.12
    for s,(ei,eo,ear,mo) in ((-1,(1,3,7,9)),(1,(4,6,8,10))):
        O[ei] = head+fwd*0.1+up*0.03+side*s*0.02; O[ei+1] = head+fwd*0.095+up*0.03+side*s*0.04; O[eo] = head+fwd*0.085+up*0.03+side*s*0.06
        O[ear] = head+side*s*0.09; O[mo] = head+fwd*0.1-up*0.05+side*s*0.025
    for el,w,pk,ix,tb in ((13,15,17,19,21),(14,16,18,20,22)):
        dr = unit(O[w]-O[el]); O[ix] = O[w]+dr*0.08; O[pk] = O[w]+dr*0.07; O[tb] = O[w]+dr*0.04
    for kn,an,heel,toe in ((25,27,29,31),(26,28,30,32)):
        sh = unit(O[an]-O[kn]); tdir = unit(fwd*0.9 - up*max(0.0, sh[0]*-1.2))
        O[toe] = O[an]+tdir*0.15-up*0.03; O[heel] = O[an]-fwd*0.06-up*0.05
    out.append(O)
out = np.array(out)
low = out[:,[27,28,29,30,31,32],1].min(1); out[:,:,1] += (0.04-low)[:,None]
print("hip height range", out[:,23,1].min().round(2), out[:,23,1].max().round(2))
json.dump({"fps": 24, "frames": np.round(out,2).tolist()}, open("run_clip.json","w"), separators=(",",":"))
CON=[[11,12],[11,13],[13,15],[12,14],[14,16],[11,23],[12,24],[23,24],[23,25],[24,26],[25,27],[26,28],[27,31],[28,32]]
tiles=[]
for i in range(0, 24, 2):
    im = np.full((260,200,3), 40, np.uint8); pt = lambda p: (int(100+p[0]*110), int(240-p[1]*110))
    cv2.line(im,(0,240),(200,240),(90,90,90),1)
    for a,b in CON: cv2.line(im, pt(out[i][a]), pt(out[i][b]), (0,160,255) if a%2 else (255,200,60), 3)
    cv2.circle(im, pt((out[i][7]+out[i][8])/2), 11, (220,220,220), -1); cv2.putText(im,str(i),(5,18),0,0.5,(255,255,255),1); tiles.append(im)
cv2.imwrite("clip_side.png", np.vstack([np.hstack(tiles[:6]), np.hstack(tiles[6:])]))
