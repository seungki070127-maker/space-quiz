# 최소 FBX 바이너리 읽기: 노드 트리와 배열 속성(압축 포함)
import struct, zlib, sys, numpy as np
def read(path):
    b=open(path,'rb').read(); ver=struct.unpack_from('<I',b,23)[0]; big=ver>=7500
    def prop(o):
        t=chr(b[o]); o+=1
        if t in 'YCILFD':
            fmt={'Y':'<h','C':'<?','I':'<i','L':'<q','F':'<f','D':'<d'}[t]; v=struct.unpack_from(fmt,b,o)[0]; return v,o+struct.calcsize(fmt)
        if t in 'fdlib':
            n,enc,cl=struct.unpack_from('<III',b,o); o+=12; raw=b[o:o+cl]; o+=cl
            if enc: raw=zlib.decompress(raw)
            dt={'f':'<f4','d':'<f8','l':'<i8','i':'<i4','b':'b'}[t]; return np.frombuffer(raw,dtype=dt,count=n),o
        if t in 'SR':
            n=struct.unpack_from('<I',b,o)[0]; o+=4; v=b[o:o+n]; return (v.decode('utf8','replace') if t=='S' else v),o+n
        raise ValueError(t)
    def node(o):
        if big: end,np_,pl=struct.unpack_from('<QQQ',b,o); o+=24
        else: end,np_,pl=struct.unpack_from('<III',b,o); o+=12
        nl=b[o]; o+=1; name=b[o:o+nl].decode(); o+=nl
        if end==0: return None,o
        props=[]
        for _ in range(np_): v,o=prop(o); props.append(v)
        kids=[]
        while o<end:
            c,o2=node(o)
            if c is None: o=o2; break
            kids.append(c); o=o2
        return {'name':name,'props':props,'kids':kids},end
    o=27; out=[]
    while o<len(b)-200:
        n,o2=node(o)
        if n is None: break
        out.append(n); o=o2
    return out
def find(nodes,name):
    for n in nodes:
        if n['name']==name: yield n
        yield from find(n['kids'],name)
if __name__=='__main__':
    t=read(sys.argv[1])
    def show(n,d=0):
        if d>4: return
        ps=[(type(p).__name__, (p.shape if hasattr(p,'shape') else (str(p)[:40]))) for p in n['props'][:3]]
        print('  '*d+n['name'],ps)
        for k in n['kids'][:12]: show(k,d+1)
    for n in t:
        if n['name'] in ('Objects','Connections','GlobalSettings'): show(n)
