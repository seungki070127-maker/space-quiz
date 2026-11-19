# 1단계: Meshy 등에서 받은 STL → 게임 좌표([앞, 위, 오른쪽] m, 키 1.82m)로 바꾸고 면 수를 줄여 P.npy / F.npy 로 저장
#   사용: python prepare.py 모델.stl [목표 면 수=14000]
#   STL 축 가정: z 위, -y 앞(얼굴 방향), -x 몸의 오른쪽. 다른 모델이면 아래 L= 줄의 축 바꾸기를 고치세요.
import sys, struct, numpy as np, fast_simplification as fs
f=open(sys.argv[1],'rb').read(); n=struct.unpack('<I',f[80:84])[0]
T=np.frombuffer(f[84:84+50*n],dtype=np.dtype([('n','<f4',3),('v','<f4',(3,3)),('a','<u2')]))['v'].astype(np.float64)
s=1.82/(T[...,2].max()-T[...,2].min())
L=np.stack([-T[...,1], T[...,2]-T[...,2].min(), -T[...,0]],-1)*s
V=L.reshape(-1,3); q=np.round(V/1e-5).astype(np.int64)
u,inv=np.unique(q,axis=0,return_inverse=True); P=np.zeros((len(u),3)); np.add.at(P,inv.ravel(),V); P/=np.bincount(inv.ravel())[:,None]
F=inv.reshape(-1,3); F=F[(F[:,0]!=F[:,1])&(F[:,1]!=F[:,2])&(F[:,0]!=F[:,2])]
target=int(sys.argv[2]) if len(sys.argv)>2 else 14000
P2,F2=fs.simplify(P.astype(np.float32),F.astype(np.int32),target_reduction=max(0,1-target/len(F)))
np.save("P.npy",P2); np.save("F.npy",F2); print("verts",len(P2),"faces",len(F2))
