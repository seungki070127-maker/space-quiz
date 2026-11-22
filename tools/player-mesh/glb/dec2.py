# 그림 좌표(UV) 지키며 면 수 줄이기 (2판): 원래 메시의 UV 조각(섬)을 구해, 새 면의 세 꼭짓점을 모두 같은 섬의 가장 가까운 원래 면에 투영
import numpy as np, fast_simplification as fs, sys
from scipy.spatial import cKDTree
P=np.load('P0.npy').astype(np.float64); UV=np.load('UV0.npy').astype(np.float64); I=np.load('I0.npy').astype(np.int64)
s=1.82/(P[:,1].max()-P[:,1].min())
G=np.stack([P[:,2],P[:,1]-P[:,1].min(),-P[:,0]],1)*s
# UV 섬: 인덱스로 이어진 면끼리(GLB 는 이음매에서 정점이 나뉘어 있음)
par=np.arange(len(G))
def find(a):
    r=a
    while par[r]!=r: r=par[r]
    while par[a]!=r: par[a],a=r,par[a]
    return r
for a,b,c in I:
    ra,rb,rc=find(a),find(b),find(c); par[rb]=ra; par[rc]=ra
isl=np.array([find(i) for i in range(len(G))]); fisl=isl[I[:,0]]
print('islands',len(np.unique(fisl)))
target=int(sys.argv[1]) if len(sys.argv)>1 else 20000
q=np.round(G/1e-6).astype(np.int64); uq,winv=np.unique(q,axis=0,return_inverse=True); winv=winv.ravel()   # 이음매 정점 합쳐서(구멍 방지) 줄이기
Gw=np.zeros((len(uq),3)); Gw[winv]=G; Iw=winv[I]; Iw=Iw[(Iw[:,0]!=Iw[:,1])&(Iw[:,1]!=Iw[:,2])&(Iw[:,0]!=Iw[:,2])]
P2,F2=fs.simplify(Gw.astype(np.float32),Iw.astype(np.int32),target_reduction=1-target/len(Iw)); P2=P2.astype(np.float64)
T=G[I]; C=T.mean(1); tree=cKDTree(C)
N0=np.cross(T[:,1]-T[:,0],T[:,2]-T[:,0]); N0/=np.linalg.norm(N0,axis=1)[:,None]+1e-15
T2=P2[F2]; C2=T2.mean(1); N2=np.cross(T2[:,1]-T2[:,0],T2[:,2]-T2[:,0]); N2/=np.linalg.norm(N2,axis=1)[:,None]+1e-15
d,cand=tree.query(C2,k=12); score=d+0.02*(1-np.einsum('ij,ikj->ik',N2,N0[cand])); best=cand[np.arange(len(F2)),np.argmin(score,1)]
fi=fisl[best]
def project(pts,tris):          # 점을 삼각형 위 가장 가까운 점의 무게중심 좌표로(삼각형 밖이면 가장자리로 잘라 냄)
    A,B,Cc=G[I[tris,0]],G[I[tris,1]],G[I[tris,2]]; e0=B-A; e1=Cc-A; v=pts-A
    d00=(e0*e0).sum(1); d01=(e0*e1).sum(1); d11=(e1*e1).sum(1); d20=(v*e0).sum(1); d21=(v*e1).sum(1); den=d00*d11-d01*d01+1e-18
    b1=(d11*d20-d01*d21)/den; b2=(d00*d21-d01*d20)/den; b0=1-b1-b2
    b=np.clip(np.stack([b0,b1,b2],1),0,None); b/=b.sum(1)[:,None]+1e-18
    q=A*b[:,:1]+B*b[:,1:2]+Cc*b[:,2:]; dist=np.linalg.norm(pts-q,axis=1)
    uv=UV[I[tris,0]]*b[:,:1]+UV[I[tris,1]]*b[:,1:2]+UV[I[tris,2]]*b[:,2:]; return uv,dist
outUV=[]
for k in range(3):
    pts=T2[:,k]; dd,cc=tree.query(pts,k=24)
    uvbest=np.zeros((len(pts),2)); dbest=np.full(len(pts),1e9)
    for j in range(cc.shape[1]):
        t=cc[:,j]; ok=fisl[t]==fi
        uv,dist=project(pts,t); better=ok&(dist<dbest); uvbest[better]=uv[better]; dbest[better]=dist[better]
    # 같은 섬에서 못 찾은 꼭짓점: 가장 좋은 원래 면으로
    miss=dbest>=1e8; uv,_=project(pts[miss],best[miss]); uvbest[miss]=uv
    outUV.append(uvbest)
print('corner miss',[int(((u==0).all(1)).sum()) for u in outUV])
Pn=T2.reshape(-1,3); UVn=np.stack(outUV,1).reshape(-1,2)
key=np.concatenate([np.round(Pn/1e-5),np.round(UVn/1e-4)],1).astype(np.int64)
u,inv=np.unique(key,axis=0,return_inverse=True); inv=inv.ravel()
Pu=np.zeros((len(u),3)); UVu=np.zeros((len(u),2)); Pu[inv]=Pn; UVu[inv]=UVn
np.save('P.npy',Pu); np.save('F.npy',inv.reshape(-1,3)); np.save('UV.npy',UVu); print('faces',len(F2),'verts',len(Pu))
