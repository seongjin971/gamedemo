"""Read final native-local V12 export, report root-only footprint and contacts.
Uses no Blender, scene edits, or inferred crown collider. Requires NumPy.
"""
from pathlib import Path
import json,math,hashlib,numpy as np
W=Path(__file__).resolve().parent;D=W/'derivative';file=D/'tree-v12-mesh.json';p=np.array(json.loads(file.read_text())['positions']).reshape(-1,3)
def hull(points):
 points=sorted(set(map(tuple,points)))
 if len(points)<3:return points
 def cross(o,a,b):return (a[0]-o[0])*(b[1]-o[1])-(a[1]-o[1])*(b[0]-o[0])
 lower=[]
 for q in points:
  while len(lower)>=2 and cross(lower[-2],lower[-1],q)<=0:lower.pop()
  lower.append(q)
 upper=[]
 for q in reversed(points):
  while len(upper)>=2 and cross(upper[-2],upper[-1],q)<=0:upper.pop()
  upper.append(q)
 return lower[:-1]+upper[:-1]
footprints=[]
for lo,hi in [(0.12,0.7),(0.12,0.3),(0.3,0.5),(0.5,0.7)]:
 q=p[(p[:,1]>=lo)&(p[:,1]<=hi)];xz=q[:,[0,2]];r=np.linalg.norm(xz,axis=1);i=int(np.argmax(r))
 footprints.append(dict(localHeightBand=[lo,hi],vertexSamples=len(q),xzBounds=[xz.min(axis=0).tolist(),xz.max(axis=0).tolist()],convexHullXZ=hull(xz),maximumRadiusFromOrigin=float(r[i]),maximumRadiusVertex=q[i].tolist()))
theta=np.arctan2(-p[:,2],-p[:,0]);rad=np.linalg.norm(p[:,[0,2]],axis=1);contacts=[]
for i,(angle,width) in enumerate([(-2.60,.35),(-.90,.30),(.45,.32),(2.15,.40)],1):
 diff=np.arctan2(np.sin(theta-angle),np.cos(theta-angle));mask=(np.abs(diff)<width*.75)&(p[:,1]>.005)&(p[:,1]<.13)&(rad>.55);ix=np.flatnonzero(mask)
 assert len(ix)>0,(i,'No actual near-ground root samples')
 chosen=int(ix[np.argmax(rad[ix])]);contacts.append(dict(root=i,measuredVisibleContactVertex=p[chosen].tolist(),groundProjection=[float(p[chosen,0]),0,float(p[chosen,2])],radius=float(rad[chosen]),sourceVertexIndex=chosen,candidateSamples=len(ix),designDirectionRadiansBlender=angle))
r=dict(units='Meters in native Unity model-local coordinates; parent scale is not baked',polygonOrder='Counterclockwise in numerical (X,Z) plane; ordered perimeter; final first point is not repeated',coordinateBasis='Native Unity model-local already converted; transform through actual tree Transform including mesh yaw. Y bands are local, not world.',meshSHA256=hashlib.sha256(file.read_bytes()).hexdigest(),footprints=footprints,rootContacts=contacts,limitations='Convex hulls over-cover spaces between roots; use as root-only envelope evidence, not an automatic collider. Contact samples are real exported vertices near Y=0, not verified paving gaps. Crown was excluded.')
(D/'root-footprint-and-contacts.json').write_text(json.dumps(r,indent=2));print(json.dumps(dict(footprints=[{k:v for k,v in f.items() if k!='convexHullXZ'} for f in footprints],rootContacts=contacts),indent=2))
