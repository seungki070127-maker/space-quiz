# STL(Meshy) → 게임용 스킨 데이터: 위치·UV·뼈 2개 가중치·부위(색) 를 계산해 base64 로 저장
import numpy as np, base64, json
P=np.load("P.npy").astype(np.float64); F=np.load("F.npy").astype(np.int64)
# 측정한 기준 관절 (좌표 [앞, 위, 오른쪽] m). s=-1 왼쪽, +1 오른쪽
J={}
for s,R in ((-1,0),(1,1)):
    J[11+R]=(-0.045,1.44,s*0.20); J[13+R]=(-0.04,1.16,s*0.29); J[15+R]=(0.03,0.91,s*0.35); J[19+R]=(0.05,0.74,s*0.34)
    J[23+R]=(-0.02,0.92,s*0.11); J[25+R]=(-0.04,0.50,s*0.145); J[27+R]=(-0.04,0.08,s*0.17); J[29+R]=(-0.11,0.03,s*0.17); J[31+R]=(0.15,0.03,s*0.185)
    J[7+R]=(0.0,1.69,s*0.085)
J[0]=(0.117,1.69,0.0)
J={k:np.array(v) for k,v in J.items()}
hipC=(J[23]+J[24])/2; shC=(J[11]+J[12])/2; headC=(J[7]+J[8])/2
# 뼈 번호: 0 골반 1 가슴 2 머리 3/4 허벅지 5/6 정강이 7/8 발 9/10 위팔 11/12 아래팔(손 포함)
segs={0:(hipC,hipC+(shC-hipC)*0.35,0.16),1:(hipC+(shC-hipC)*0.35,shC,0.17),2:(shC+(headC-shC)*0.25,headC+np.array([0,0.06,0]),0.11)}
for R in (0,1):
    segs[3+R]=(J[23+R],J[25+R],0.085); segs[5+R]=(J[25+R],J[27+R],0.062); segs[7+R]=(J[29+R],J[31+R],0.05)
    segs[9+R]=(J[11+R],J[13+R],0.055); segs[11+R]=(J[13+R],J[19+R],0.045)
adj={frozenset(p) for p in [(0,1),(1,2),(0,3),(0,4),(3,5),(4,6),(5,7),(6,8),(1,9),(1,10),(9,11),(10,12)]}
def segd(p,a,b):
    ab=b-a; t=np.clip(((p-a)@ab)/(ab@ab),0,1); return np.linalg.norm(p-(a+np.outer(t,ab)),axis=1)
D=np.stack([segd(P,a,b)/r for k,(a,b,r) in sorted(segs.items())],1)        # (nv,13) 반지름으로 나눈 거리
# 몸 바깥쪽 판정 보조: 팔 영역(|z|>0.25 이고 손목 아래·위)과 다리(y<0.6)는 해당 뼈만 고려
y,z,x=P[:,1],P[:,2],P[:,0]
armzone=(np.abs(z)>0.255)&(y<1.40)
D[armzone][:, :9]=1e9
for i in np.where(armzone)[0]: D[i,:9]=1e9
legzone=(y<0.60)
for i in np.where(legzone)[0]: D[i,[0,1,2,9,10,11,12]]=1e9
order=np.argsort(D,1); b1=order[:,0]; b2=order[:,1]
d1=D[np.arange(len(P)),b1]; d2=D[np.arange(len(P)),b2]
w1=np.ones(len(P))
for i in range(len(P)):
    if frozenset((b1[i],b2[i])) in adj:
        t=np.clip((d2[i]-d1[i])/0.9,0,1); w1[i]=0.5+0.5*t
# 부위(색): 0 SKIN 1 SHIRT 2 SHORTS 3 SOCK 4 BOOT 5 HAIR 6 TRIM 7 HEM 9 WHITE 10 HAND 11 DARK 12 TEX
part=np.zeros(len(P),dtype=np.uint8)
torso=np.isin(b1,[0,1])&(y>0.94)&(y<1.565)
part[torso]=12
part[np.isin(b1,[0,1])&(y>=1.545)&(y<1.575)]=6                                    # 목깃
part[np.isin(b1,[9,10])&(y>1.295)]=1                                                   # 반소매
sh=np.isin(b1,[0,3,4])&(y>=0.625)&(y<=0.96); part[sh]=2
part[np.isin(b1,[5,6])&(y>=0.10)&(y<0.43)]=3; part[np.isin(b1,[5,6,7,8])&(y>=0.075)&(y<0.10)]=9
part[np.isin(b1,[7,8])|((y<0.075)&np.isin(b1,[5,6]))]=4
part[np.isin(b1,[11,12])&(y<0.93)]=10
head=(b1==2)
part[head&((y>1.765)|((y>1.62)&(x<-0.035)))]=5                                    # 머리카락: 정수리와 뒤통수
for s in (-1,1):                                                                     # 눈썹·눈(얼굴 앞쪽 점 중 가까운 것)
    e=np.array([0.098,1.712,s*0.034]); de=np.linalg.norm(P-e,axis=1); part[head&(de<0.014)&(x>0.07)]=11
    b=np.array([0.1,1.738,s*0.036]); db=np.linalg.norm(P-b,axis=1); part[head&(db<0.013)&(x>0.07)]=5
# 유니폼 그림 좌표: 몸통 둘레(왼쪽 옆구리 0, 앞 0.25, 오른쪽 0.5, 뒤 0.75), 높이
u=np.full(len(P),0.5); v=np.full(len(P),0.02)
th=np.arctan2(z,x-(-0.03)); u_t=((th+np.pi/2)/(2*np.pi))%1.0; v_t=0.1+(y-0.94)/(1.565-0.94)*0.9
tex=part==12; u[tex]=u_t[tex]; v[tex]=np.clip(v_t[tex],0.1,1.0)
# 이음매(왼쪽 옆구리)를 가로지르는 삼각형은 정점을 복제해 u 를 +1 로
P=list(P); u=list(u); v=list(v); part=list(part); b1=list(b1); b2=list(b2); w1=list(w1); F=F.copy()
for fi,f in enumerate(F):
    if all(part[i]==12 for i in f):
        us=[u[i] for i in f]
        if max(us)-min(us)>0.5:
            for k,i in enumerate(f):
                if u[i]<0.5:
                    P.append(P[i]); u.append(u[i]+1); v.append(v[i]); part.append(12); b1.append(b1[i]); b2.append(b2[i]); w1.append(w1[i]); F[fi,k]=len(P)-1
P=np.array(P,np.float32); n=len(P)
out={"n":n,"pos":base64.b64encode(P.tobytes()).decode(),
     "uv":base64.b64encode(np.stack([u,v],1).astype(np.float32).tobytes()).decode(),
     "idx":base64.b64encode(F.astype(np.uint16).tobytes()).decode(),
     "skin":base64.b64encode(np.stack([np.array(b1),np.array(b2),np.round(np.array(w1)*255),np.array(part)],1).astype(np.uint8).tobytes()).decode(),
     "joints":{str(k):[round(float(c),3) for c in v_] for k,v_ in J.items()}}
json.dump(out,open("body.json","w"),separators=(",",":"))
print("verts",n,"faces",len(F),"json bytes",len(json.dumps(out)), "parts",np.bincount(np.array(part),minlength=13))
