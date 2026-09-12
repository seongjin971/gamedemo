import json,math
from pathlib import Path
import numpy as np
W=Path(__file__).resolve().parent
j=json.loads((W.parent/'TreeV12/derivative/tree-v12-mesh.json').read_text());p=np.array(j['positions']).reshape(-1,3);p=np.c_[-p[:,0],-p[:,2],p[:,1]]
r=np.linalg.norm(p[:,:2],axis=1);a=np.arctan2(p[:,1],p[:,0]);rows=[]
for ri,angle in enumerate([-2.6,-.9,.45,2.15],1):
 d=np.arctan2(np.sin(a-angle),np.cos(a-angle));mask=(abs(d)<.48)&(p[:,2]<1.3)
 print('ROOT',ri,'maxradius aboveground',r[mask&(p[:,2]>0)].max())
 for lo in np.arange(.5,1.91,.15):
  sel=mask&(r>=lo)&(r<lo+.15)
  if sel.sum(): print(round(lo,2),int(sel.sum()),np.percentile(p[sel,2],[0,50,90,100]).round(3).tolist())
