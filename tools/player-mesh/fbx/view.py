import sys,numpy as np
sys.path.insert(0,'.')
from fbxread import read,find
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
def load(path):
    t=read(path); g=next(find(t,'Geometry'))
    kv={k['name']:k['props'][0] for k in g['kids'] if k['props']}
    V=kv['Vertices'].reshape(-1,3).astype(float); P=kv['PolygonVertexIndex'].astype(np.int64)
    tris=[]; poly=[]
    for i in P:
        if i<0: poly.append(-i-1); 
        else: poly.append(i); continue
        for k in range(1,len(poly)-1): tris.append((poly[0],poly[k],poly[k+1]))
        poly=[]
    return V,np.array(tris)
def render(V,F,out,views=((0,0),(0,90)),zoom=None):
    fig=plt.figure(figsize=(4*len(views),6),dpi=110)
    for k,(el,az) in enumerate(views):
        ax=fig.add_subplot(1,len(views),k+1,projection='3d')
        # Y-up assumed → plot x,z,y
        P=V
        tri=P[F]; n=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]); n/= (np.linalg.norm(n,axis=1)[:,None]+1e-12)
        a,e=np.radians(az),np.radians(el); cam=np.array([np.cos(e)*np.cos(a),np.cos(e)*np.sin(a),np.sin(e)])
        L=cam+np.array([0,0,.6]); L/=np.linalg.norm(L); sh=np.abs(n@L)*.8+.15
        order=np.argsort(-(tri.mean(1)@cam)); tri=tri[order]; sh=sh[order]
        pc=Poly3DCollection(tri,facecolors=np.c_[sh,sh,sh*.97,np.ones_like(sh)],edgecolor='none'); ax.add_collection3d(pc)
        lo,hi=(P.min(0),P.max(0)) if zoom is None else zoom
        c=(lo+hi)/2; r=(hi-lo).max()/2
        ax.set_xlim(c[0]-r,c[0]+r); ax.set_ylim(c[1]-r,c[1]+r); ax.set_zlim(c[2]-r,c[2]+r); ax.view_init(el,az); ax.set_axis_off()
    plt.tight_layout(); plt.savefig(out); plt.close()
if __name__=='__main__':
    V,F=load(sys.argv[1]); print(V.shape,F.shape,V.min(0),V.max(0))
    render(V,F,'full.png',views=((5,-90),(5,0)))
