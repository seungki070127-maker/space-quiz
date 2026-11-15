import json, numpy as np, cv2
T = json.load(open("tracks.json")); tr = [(f, d) for f, d in T[4] if 63 <= f <= 76]
W = np.array([d["world"] for _, d in tr], float)            # (n,33,3) MediaPipe world: x 오른쪽(화면), y 아래, z 깊이
n = len(W); print("frames", [f for f,_ in tr])
SW = [(11,12),(13,14),(15,16),(23,24),(25,26),(27,28)]
def swap(P):
    Q = P.copy()
    for a,b in SW: Q[a], Q[b] = P[b].copy(), P[a].copy()
    return Q
J = [11,12,13,14,15,16,23,24,25,26,27,28]
# 1) 좌우가 뒤바뀐 프레임 바로잡기 (앞 프레임과 더 비슷한 쪽 선택)
for i in range(1, n):
    if np.linalg.norm(swap(W[i])[J]-W[i-1][J]) < np.linalg.norm(W[i][J]-W[i-1][J]): W[i] = swap(W[i]); print("swap fixed at", tr[i][0])
# 2) 몸 기준 축: 위(몸통 평균), 오른쪽(골반선 평균), 앞
hipC = (W[:,23]+W[:,24])/2; shC = (W[:,11]+W[:,12])/2
u = (shC-hipC).mean(0); u /= np.linalg.norm(u)
# 옆에서 찍힌 영상이라 깊이(골반·어깨선 방향)는 믿기 어렵다 → "앞"은 발이 가장 크게 흔들리는 방향으로 잡는다
A = np.concatenate([W[:,27]-hipC, W[:,28]-hipC]); A = A - np.outer(A@u, u)
f = np.linalg.svd(A - A.mean(0))[2][0]; f -= u*np.dot(f,u); f /= np.linalg.norm(f)
votes = [np.dot((W[:,0]-shC).mean(0), f), np.dot((W[:,31]-W[:,29]).mean(0)+(W[:,32]-W[:,30]).mean(0), f)]
print("forward votes", np.round(votes,3))
if sum(v > 0 for v in votes) < 1 or (votes[0] < 0 and abs(votes[0]) > abs(votes[1])): f = -f
r = np.cross(f, u)                                          # 오른쪽 = 앞 × 위
if np.dot((W[:,24]-W[:,23]).mean(0), r) < 0: W = np.array([swap(w) for w in W]); print("global L/R relabel")
th = np.radians(12); u, f = np.cos(th)*u - np.sin(th)*f, np.cos(th)*f + np.sin(th)*u   # 달릴 때 몸통이 12도쯤 숙여진다고 보고 수직축 보정
L = np.stack([(W-hipC[:,None])@f, (W-hipC[:,None])@u, (W-hipC[:,None])@r], -1)   # (n,33,[앞,위,오른쪽])
# 3) 뼈 길이를 게임 선수 규격으로 고정 (방향만 영상에서 가져옴)
def unit(v): return v/ (np.linalg.norm(v)+1e-9)
def limbdir(v):                                             # 옆으로 벌어지는 성분은 작게 제한 (깊이 잡음 억제)
    v = unit(v); v[2] = np.clip(v[2], -0.22, 0.22); return unit(v)
def rebuild(P):
    O = np.zeros((33,3)); side = np.array([0,0,1.0])
    spine = (P[11]+P[12])/2-(P[23]+P[24])/2; spine[2] = 0; spine = unit(spine)
    tw = np.clip((P[27,0]-P[28,0])*0.12, -0.12, 0.12)       # 골반은 앞으로 나간 다리 쪽이 살짝 앞으로, 어깨는 반대로
    hip = unit(side + np.array([-tw,0,0])); sh = unit(side + np.array([tw*1.3,0,0]))
    O[24], O[23] = hip*0.115, -hip*0.115
    shc = spine*0.54; O[12], O[11] = shc+sh*0.21, shc-sh*0.21
    for hp,kn,an in ((23,25,27),(24,26,28)):
        O[kn] = O[hp]+limbdir(P[kn]-P[hp])*0.44; O[an] = O[kn]+limbdir(P[an]-P[kn])*0.44
    for s_,e,w in ((11,13,15),(12,14,16)):
        O[e] = O[s_]+limbdir(P[e]-P[s_])*0.27; O[w] = O[e]+limbdir(P[w]-P[e])*0.25
    return O
B = np.array([rebuild(p) for p in L])
# 4) 반 걸음(한쪽 발이 가장 앞 → 가장 뒤) 구간을 찾고, 나머지 반은 좌우를 뒤집어 붙여 끊김 없는 한 사이클로
d = B[:,27,0]-B[:,28,0]; print("ankle fwd diff", np.round(d,2))
i0, i1 = int(np.argmax(d)), int(np.argmin(d))
if i0 > i1: i0, i1 = i1, i0
half = B[i0:i1+1]; print("half cycle frames", tr[i0][0], "-", tr[i1][0], "len", len(half))
def mirror(P):
    Q = swap(P); Q[:,2] *= -1; return Q
H = 12
def resample(seq, m):
    t = np.linspace(0, len(seq)-1, m+1)[:-1]; i = np.floor(t).astype(int); a = (t-i)[:,None,None]
    return seq[i]*(1-a)+seq[np.minimum(i+1,len(seq)-1)]*a
h1 = resample(half, H)
if d[i0] < 0: h1 = np.array([mirror(p) for p in h1])       # 사이클이 "왼발 앞"에서 시작하도록
cyc = np.concatenate([h1, np.array([mirror(p) for p in h1])])
# 5) 원형 평활(떨림 제거) 후 뼈 길이 다시 고정, 발이 땅에 닿게 올리기, 얼굴·손·발끝 점 채우기
k = np.array([1,2,3,2,1], float); k /= k.sum()
sm = sum(np.roll(cyc, s, 0)*w for s, w in zip((-2,-1,0,1,2), k))
out = []
for P in sm:
    O = rebuild(P); fwd = np.array([1.0,0,0]); up = np.array([0,1.0,0]); side = np.array([0,0,1.0])
    spine = unit((O[11]+O[12])/2-(O[23]+O[24])/2); head = (O[11]+O[12])/2 + spine*0.23
    O[0] = head+fwd*0.12
    for s,(ei,eo,ear,mo) in ((-1,(1,3,7,9)),(1,(4,6,8,10))):
        O[ei] = head+fwd*0.1+up*0.03+side*s*0.02; O[ei+1] = head+fwd*0.095+up*0.03+side*s*0.04; O[eo] = head+fwd*0.085+up*0.03+side*s*0.06
        O[ear] = head+side*s*0.09; O[mo] = head+fwd*0.1-up*0.05+side*s*0.025
    for el,w,pk,ix,tb in ((13,15,17,19,21),(14,16,18,20,22)):
        dr = unit(O[w]-O[el]); O[ix] = O[w]+dr*0.08; O[pk] = O[w]+dr*0.07; O[tb] = O[w]+dr*0.04
    for kn,an,heel,toe in ((25,27,29,31),(26,28,30,32)):
        sh = unit(O[an]-O[kn]); tdir = unit(fwd*0.9 - up*max(0.0, sh[0]*-1.2))   # 발이 뒤로 들리면 발끝이 아래로
        O[toe] = O[an]+tdir*0.15-up*0.03; O[heel] = O[an]-fwd*0.06-up*0.05
    out.append(O)
out = np.array(out)
low = out[:,[27,28,29,30,31,32],1].min(1)
out[:,:,1] += (0.04-low)[:,None]
out[:,:,0] -= out[:,[23,24],0].mean(1)[:,None]*0   # 골반 중심 = 앞뒤 원점 유지
print("hip height range", out[:,23,1].min().round(2), out[:,23,1].max().round(2))
json.dump({"fps": 24, "frames": np.round(out,3).tolist()}, open("run_clip.json","w"), separators=(",",":"))
# 확인용 그림: 옆에서 본 모습(앞=오른쪽)
CON=[[11,12],[11,13],[13,15],[12,14],[14,16],[11,23],[12,24],[23,24],[23,25],[24,26],[25,27],[26,28],[27,31],[28,32]]
tiles=[]
for i in range(0, 24, 2):
    im = np.full((260,200,3), 40, np.uint8); pt = lambda p: (int(100+p[0]*110), int(240-p[1]*110))
    cv2.line(im,(0,240),(200,240),(90,90,90),1)
    for a,b in CON: cv2.line(im, pt(out[i][a]), pt(out[i][b]), (0,160,255) if a%2 else (255,200,60), 3)
    cv2.circle(im, pt((out[i][7]+out[i][8])/2), 11, (220,220,220), -1); cv2.putText(im,str(i),(5,18),0,0.5,(255,255,255),1); tiles.append(im)
cv2.imwrite("clip_side.png", np.vstack([np.hstack(tiles[:6]), np.hstack(tiles[6:])]))
