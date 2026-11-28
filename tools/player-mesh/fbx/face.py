import sys,numpy as np, fast_simplification as fs
sys.path.insert(0,'.')
from view import load,render
V,F=load(sys.argv[1])
z=V[:,2]; top=z.max(); H=top-z.min()
head=V[z>top-0.13*H]; print('head y range',head[:,1].min(),head[:,1].max(),'x',head[:,0].min(),head[:,0].max())
# 얼굴 방향: 머리 높이에서 가장 튀어나온 쪽(±y)
band=V[(z>top-0.09*H)&(z<top-0.06*H)]; fy=-1 if abs(band[:,1].min())>abs(band[:,1].max()) else 1; print('face dir y',fy)
def neighbors(F,n):
    import collections
    E=np.concatenate([F[:,[0,1]],F[:,[1,2]],F[:,[2,0]]]); E=np.concatenate([E,E[:,::-1]])
    order=np.argsort(E[:,0]); E=E[order]; starts=np.searchsorted(E[:,0],np.arange(n+1)); return E[:,1],starts
def smooth(P,F,w,it):
    nb,st=neighbors(F,len(P)); cnt=np.diff(st).clip(1)
    for k in range(it):
        for lam in (0.55,-0.57):
            S=np.zeros_like(P); np.add.at(S,np.repeat(np.arange(len(P)),np.diff(st)),P[nb]); avg=S/cnt[:,None]
            P=P+lam*w[:,None]*(avg-P)
    return P
P2,F2=fs.simplify(V.astype(np.float32),F.astype(np.int32),target_reduction=1-int(sys.argv[3] if len(sys.argv)>3 else 14000)/len(F)); P2=P2.astype(float)
# 머리 영역 가중치: 목 위에서 0→1, 얼굴 앞쪽은 더 강하게
z2=P2[:,2]; neck=top-0.135*H; w=np.clip((z2-neck)/(0.03*H),0,1)
front=np.clip((P2[:,1]*fy - np.median(head[:,1]*fy))/0.04,0,1); w=w*(0.5+0.5*front)*float(sys.argv[4] if len(sys.argv)>4 else 1)
P3=smooth(P2,F2,w,int(sys.argv[2]) if len(sys.argv)>2 else 12)
np.save('P_low.npy',P3); np.save('F_low.npy',F2)
hz=(np.array([head[:,0].min()-.03,head[:,1].min()-.03,top-0.16*H]),np.array([head[:,0].max()+.03,head[:,1].max()+.03,top+.01]))
az=-90 if fy<0 else 90
render(V,F,'head_orig.png',views=((5,az),(5,az+45)),zoom=hz)
render(P3,F2,'head_low.png',views=((5,az),(5,az+45)),zoom=hz)
render(P3,F2,'full_low.png',views=((5,az),(5,az+90)))
print(len(P3),len(F2))
