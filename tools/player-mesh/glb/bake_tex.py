# 그림(텍스처)이 있는 모델 → 게임 뼈대용 데이터(색 부위 나누기 없이 원래 그림 그대로)
import numpy as np, base64, json
P=np.load("P.npy").astype(np.float64); F=np.load("F.npy").astype(np.int64); UV=np.load("UV.npy").astype(np.float32)
J={}
for s,R in ((-1,0),(1,1)):
    J[11+R]=(-0.03,1.42,s*0.20)
    J[23+R]=(-0.02,0.92,s*0.10); J[25+R]=(-0.03,0.48,s*0.125); J[27+R]=(-0.06,0.10,s*0.155); J[29+R]=(-0.12,0.03,s*0.16); J[31+R]=(0.14,0.03,s*0.17)
    J[7+R]=(0.0,1.66,s*0.085)
J[13]=(-0.03,1.12,-0.305); J[15]=(0.0,0.87,-0.245); J[19]=(0.0,0.78,-0.21)     # 왼팔: 옆으로 내림
J[14]=(0.0,1.12,0.300); J[16]=(0.10,0.92,0.21); J[20]=(0.11,0.84,0.18)        # 오른팔: 손이 허리띠 앞
J[0]=(0.12,1.66,0.0)
J={k:np.array(v,float) for k,v in J.items()}
hipC=(J[23]+J[24])/2; shC=(J[11]+J[12])/2; headC=(J[7]+J[8])/2
segs={0:(hipC,hipC+(shC-hipC)*0.35,0.16),1:(hipC+(shC-hipC)*0.35,shC,0.17),2:(shC+(headC-shC)*0.25,headC+np.array([0,0.08,0]),0.12)}
for R in (0,1):
    segs[3+R]=(J[23+R],J[25+R],0.085); segs[5+R]=(J[25+R],J[27+R],0.062); segs[7+R]=(J[29+R],J[31+R],0.05)
    segs[9+R]=(J[11+R],J[13+R],0.055); segs[11+R]=(J[13+R],J[19+R],0.065)
adj={frozenset(p) for p in [(0,1),(1,2),(0,3),(0,4),(3,5),(4,6),(5,7),(6,8),(1,9),(1,10),(9,11),(10,12)]}
def dist(Q):
    D=np.stack([ (lambda a,b,r: np.linalg.norm(Q-(a+np.outer(np.clip(((Q-a)@(b-a))/((b-a)@(b-a)),0,1),b-a)),axis=1)/r)(*segs[k]) for k in range(13)],1)
    y,z=Q[:,1],Q[:,2]
    D[(np.abs(z)>0.235)&(y<1.36),:9]=1e9          # 팔 영역은 팔 뼈만
    D[np.ix_(y<0.62,[0,1,2,9,10,11,12])]=1e9       # 다리 영역은 다리 뼈만
    x=Q[:,0]; D[y<0.76,9:]=1e9; D[(z>0)&(y<0.95)&(x<0.03),12]=1e9   # 손 아래(허리 옆 권총집)는 팔이 아님
    return D
D=dist(P); o=np.argsort(D,1); b1=o[:,0]; b2=o[:,1]; d1=D[np.arange(len(P)),b1]; d2=D[np.arange(len(P)),b2]
w1=np.array([0.5+0.5*np.clip((d2[i]-d1[i])/0.9,0,1) if frozenset((b1[i],b2[i])) in adj else 1.0 for i in range(len(P))])
n=len(P)
out={"n":n,"pos":base64.b64encode(P.astype(np.float32).tobytes()).decode(),"uv":base64.b64encode(UV.tobytes()).decode(),
     "idx":base64.b64encode(F.astype(np.uint16).tobytes()).decode(),
     "skin":base64.b64encode(np.stack([b1,b2,np.round(w1*255),np.zeros(n)],1).astype(np.uint8).tobytes()).decode(),
     "joints":{str(k):[round(float(c),3) for c in v_] for k,v_ in J.items()},
     "tex":"data:image/jpeg;base64,"+base64.b64encode(open("tex.jpg","rb").read()).decode()}
json.dump(out,open("body2.json","w"),separators=(",",":"))
print("verts",n,"faces",len(F),"bytes",len(json.dumps(out)),"bones",np.bincount(b1,minlength=13))
