# STL(Meshy) → 게임용 스킨 데이터. 옷 경계(밑단·소매·목깃·양말)는 메시를 평면으로 잘라서 반듯한 선으로 만든다
import numpy as np, base64, json
P=np.load("P.npy").astype(np.float64); F=np.load("F.npy").astype(np.int64)
J={}
for s,R in ((-1,0),(1,1)):
    J[11+R]=(-0.045,1.44,s*0.20); J[13+R]=(-0.04,1.16,s*0.29); J[15+R]=(0.03,0.91,s*0.35); J[19+R]=(0.05,0.74,s*0.34)
    J[23+R]=(-0.02,0.92,s*0.11); J[25+R]=(-0.04,0.50,s*0.145); J[27+R]=(-0.04,0.08,s*0.17); J[29+R]=(-0.11,0.03,s*0.17); J[31+R]=(0.15,0.03,s*0.185)
    J[7+R]=(0.0,1.69,s*0.085)
J[0]=(0.117,1.69,0.0)
J={k:np.array(v,float) for k,v in J.items()}

# ---- 1) 평면으로 자르기: 경계를 가로지르는 삼각형을 나눠 경계가 평면 위 직선이 되게 ----
def cut(P,F,pt,n,region):
    n=np.asarray(n,float); n/=np.linalg.norm(n); pt=np.asarray(pt,float)
    P=list(map(np.asarray,P)); d=[(p-pt)@n for p in P]; eps=1e-6
    cache={}; out=[]
    def mid(i,j):
        k=(min(i,j),max(i,j))
        if k not in cache:
            t=d[i]/(d[i]-d[j]); P.append(P[i]+(P[j]-P[i])*t); d.append(0.0); cache[k]=len(P)-1
        return cache[k]
    for f in F:
        a,b,c=f; ds=[d[a],d[b],d[c]]
        if not region((P[a]+P[b]+P[c])/3) or min(ds)>=-eps or max(ds)<=eps: out.append(f); continue
        sg=[1 if x>eps else (-1 if x<-eps else 0) for x in ds]
        # 같은 쪽에 혼자 있는 꼭짓점이 맨 앞에 오도록 돌림(감는 방향 유지)
        for r in range(3):
            v=[f[(r+k)%3] for k in range(3)]; s=[sg[(r+k)%3] for k in range(3)]
            if s[0]!=0 and s[1]!=s[0] and s[2]!=s[0]: break
        A,B,C=v
        if s[1]==0:                                  # B 가 평면 위: A-C 만 자름
            m=mid(A,C); out+= [[A,B,m],[B,C,m]]
        elif s[2]==0:
            m=mid(A,B); out+= [[A,m,C],[m,B,C]]
        else:
            ab=mid(A,B); ac=mid(A,C); out+= [[A,ab,ac],[ab,B,C],[ab,C,ac]]
    return np.array(P),np.array(out)

ax=lambda R:(J[13+R]-J[11+R])/np.linalg.norm(J[13+R]-J[11+R])
def on_axis(R,y):                                  # 위팔 축 위에서 높이가 y 인 점
    a=J[11+R]; v=J[13+R]-a; return a+v*((y-a[1])/v[1])
CUTS=[ ("shirt_hem", (0,0.948,0),(0,1,0), lambda c: abs(c[2])<0.25 and 0.85<c[1]<1.05),
       ("shorts_hem",(0,0.625,0),(0,1,0), lambda c: abs(c[2])<0.30 and 0.55<c[1]<0.70),
       ("sock_top",  (0,0.43,0),(0,1,0),  lambda c: abs(c[2])<0.30 and 0.38<c[1]<0.48),
       ("sock_band", (0,0.10,0),(0,1,0),  lambda c: c[1]<0.14),
       ("boot",      (0,0.072,0),(0,1,0), lambda c: c[1]<0.12),
       ("neckline",  (0,1.545,0),(0,1,0), lambda c: abs(c[2])<0.13 and 1.49<c[1]<1.60)]
for R,sg in ((0,-1),(1,1)):
    CUTS.append(("sleeve%d"%R, on_axis(R,1.295), ax(R), lambda c,sg=sg: c[2]*sg>0.17 and 1.18<c[1]<1.42))
for name,pt,nrm,reg in CUTS:
    P,F=cut(P,F,pt,nrm,reg)
print("after cuts: verts",len(P),"faces",len(F))

# ---- 2) 뼈 가중치 ----
hipC=(J[23]+J[24])/2; shC=(J[11]+J[12])/2; headC=(J[7]+J[8])/2
segs={0:(hipC,hipC+(shC-hipC)*0.35,0.16),1:(hipC+(shC-hipC)*0.35,shC,0.17),2:(shC+(headC-shC)*0.25,headC+np.array([0,0.06,0]),0.11)}
for R in (0,1):
    segs[3+R]=(J[23+R],J[25+R],0.085); segs[5+R]=(J[25+R],J[27+R],0.062); segs[7+R]=(J[29+R],J[31+R],0.05)
    segs[9+R]=(J[11+R],J[13+R],0.055); segs[11+R]=(J[13+R],J[19+R],0.045)
adj={frozenset(p) for p in [(0,1),(1,2),(0,3),(0,4),(3,5),(4,6),(5,7),(6,8),(1,9),(1,10),(9,11),(10,12)]}
def dist(Q):
    D=np.stack([ (lambda a,b,r: np.linalg.norm(Q-(a+np.outer(np.clip(((Q-a)@(b-a))/((b-a)@(b-a)),0,1),b-a)),axis=1)/r)(*segs[k]) for k in range(13)],1)
    y,z=Q[:,1],Q[:,2]
    D[(np.abs(z)>0.255)&(y<1.40),:9]=1e9          # 팔 영역은 팔 뼈만
    D[np.ix_(y<0.60,[0,1,2,9,10,11,12])]=1e9       # 다리 영역은 다리 뼈만
    return D
D=dist(P); o=np.argsort(D,1); b1=o[:,0]; b2=o[:,1]; d1=D[np.arange(len(P)),b1]; d2=D[np.arange(len(P)),b2]
w1=np.array([0.5+0.5*np.clip((d2[i]-d1[i])/0.9,0,1) if frozenset((b1[i],b2[i])) in adj else 1.0 for i in range(len(P))])

# ---- 3) 면마다 부위(색): 면 중심 위치와 가장 가까운 뼈로 정함 → 잘라 둔 평면이 곧 경계선 ----
Cc=P[F].mean(1); Dc=dist(Cc); fb=np.argmin(Dc,1); y,z,x=Cc[:,1],Cc[:,2],Cc[:,0]
fp=np.zeros(len(F),np.uint8)                                                   # 0 피부
fp[np.isin(fb,[0,1])&(y>0.948)&(y<1.545)]=12                                    # 상의(그림)
for R,sg in ((0,-1),(1,1)):
    a=on_axis(R,1.295); s_=((Cc-a)@ax(R))
    fp[(fb==9+R)&(s_<0)]=1                                                     # 반소매(어깨 쪽)
fp[np.isin(fb,[0,3,4])&(y>=0.625)&(y<=0.948)]=2                                 # 반바지
fp[np.isin(fb,[5,6])&(y>=0.10)&(y<0.43)]=3                                      # 양말
fp[np.isin(fb,[5,6,7,8])&(y>=0.072)&(y<0.10)]=9                                 # 발목 흰 띠
fp[np.isin(fb,[7,8])|((y<0.072)&np.isin(fb,[5,6]))]=4                           # 축구화
fp[np.isin(fb,[11,12])&(y<0.93)]=10                                             # 손
hd=fb==2
fp[hd&((y>1.765)|((y>1.62)&(x<-0.035)))]=5                                      # 머리카락

# ---- 4) 상의 그림 좌표 + 옆구리 이음매 정점 복제 ----
Pv=P[:,0]; th=np.arctan2(P[:,2],P[:,0]+0.03); U=((th+np.pi/2)/(2*np.pi))%1.0; Vv=np.clip(0.1+(P[:,1]-0.948)/(1.545-0.948)*0.9,0.1,1.0)
u=np.full(len(P),0.5); v=np.full(len(P),0.02)
texv=np.unique(F[fp==12]); u[texv]=U[texv]; v[texv]=Vv[texv]
P=list(P); u=list(u); v=list(v); b1=list(b1); b2=list(b2); w1=list(w1); F=F.copy(); dup={}
for fi in np.where(fp==12)[0]:
    f=F[fi]; us=[u[i] for i in f]
    if max(us)-min(us)>0.5:
        for k,i in enumerate(f):
            if u[i]<0.5:
                if i not in dup:
                    P.append(P[i]); u.append(u[i]+1); v.append(v[i]); b1.append(b1[i]); b2.append(b2[i]); w1.append(w1[i]); dup[i]=len(P)-1
                F[fi,k]=dup[i]
P=np.array(P,np.float32); n=len(P)
out={"n":n,"pos":base64.b64encode(P.tobytes()).decode(),
     "uv":base64.b64encode(np.stack([u,v],1).astype(np.float32).tobytes()).decode(),
     "idx":base64.b64encode(F.astype(np.uint16).tobytes()).decode(),
     "skin":base64.b64encode(np.stack([np.array(b1),np.array(b2),np.round(np.array(w1)*255),np.zeros(n)],1).astype(np.uint8).tobytes()).decode(),
     "fpart":base64.b64encode(fp.tobytes()).decode(),
     "joints":{str(k):[round(float(c),3) for c in v_] for k,v_ in J.items()}}
json.dump(out,open("body.json","w"),separators=(",",":"))
print("verts",n,"faces",len(F),"bytes",len(json.dumps(out)),"face parts",np.bincount(fp,minlength=13))
