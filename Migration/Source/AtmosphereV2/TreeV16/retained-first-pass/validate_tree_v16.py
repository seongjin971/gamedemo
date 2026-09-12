"""Independent final native-array validation; run only outside FPS holds."""
import json,hashlib,math
from pathlib import Path
import numpy as np
W=Path(__file__).resolve().parent;sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
old=json.loads((W.parent/'TreeV12/derivative/tree-v12-mesh.json').read_text());d=json.loads((W/'tree-v16-mesh.json').read_text());report=json.loads((W/'build-report.json').read_text());allresults=[]
for filename in ['tree-v16-mesh.json','tree-v16-covers.json','tree-v16-soil.json']:
 data=json.loads((W/filename).read_text());p=np.array(data['positions']).reshape(-1,3);n=np.array(data['normals']).reshape(-1,3);uv=np.array(data['uv']).reshape(-1,2);c=np.array(data['colors']).reshape(-1,4);ids=np.array(data['indices']).reshape(-1,3)
 assert all(np.isfinite(x).all() for x in [p,n,uv,c]);assert len(p)==len(n)==len(uv)==len(c);assert ids.min()>=0 and ids.max()<len(p)
 f=np.cross(p[ids[:,1]]-p[ids[:,0]],p[ids[:,2]]-p[ids[:,0]]);area=np.linalg.norm(f,axis=1)*.5;avg=n[ids].sum(axis=1);dots=(f*avg).sum(axis=1);align=dots/(2*area*np.linalg.norm(avg,axis=1));err=abs(np.linalg.norm(n,axis=1)-1)
 assert area.min()>1e-12 and dots.min()>0 and err.max()<1e-5
 allresults.append(dict(file=filename,triangles=len(ids),vertices=len(p),minArea=float(area.min()),minFaceMeanNormalAlignment=float(align.min()),nonpositiveFaceMeanNormals=int((dots<=0).sum()),maxUnitNormalError=float(err.max()),bounds=[p.min(axis=0).tolist(),p.max(axis=0).tolist()],sha256=sha(W/filename)))
 if filename=='tree-v16-mesh.json':
  oi=np.array(old['indices']).reshape(-1,3);ouv=np.array(old['uv']).reshape(-1,2);op=np.array(old['positions']).reshape(-1,3)
  assert len(ids)==157999 and np.array_equal(uv[ids],ouv[oi]);assert np.array_equal(c,np.ones_like(c))
  assert abs(p[:,1].max()-6.34)<1e-5 and abs(np.ptp(p[:,0])-6.3)<1e-5
  # Every source triangle is still represented, in the exact native order.
  npold=op[oi].reshape(-1,3);npnew=p[ids].reshape(-1,3);unchanged=np.linalg.norm(npnew-npold,axis=1)<1e-7
  upper=npold[:,1]>4.9;assert unchanged[upper].all()
  # Save a root-only actual-height hull for root integration's own clearance audit.
  q=p[(p[:,1]>=-.005)&(p[:,1]<=.7)][:,[0,2]]
  pts=sorted(set(map(tuple,q)))
  def cross(a,b,c):return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
  lower=[];higher=[]
  for v in pts:
   while len(lower)>1 and cross(lower[-2],lower[-1],v)<=0:lower.pop()
   lower.append(v)
  for v in reversed(pts):
   while len(higher)>1 and cross(higher[-2],higher[-1],v)<=0:higher.pop()
   higher.append(v)
  hull=lower[:-1]+higher[:-1]
  (W/'root-navigation-evidence.json').write_text(json.dumps(dict(units='native Unity model-local meters, parent TRS unbaked',heightBandLocal=[-.005,.7],convexHullXZ=hull,order='counterclockwise XZ',meshSHA256=sha(W/filename),clearanceWorld=.28,notes='Root must regenerate/audit native navigation after installing tree AND physical covers. Hull excludes crown and fully buried vertices.'),indent=2))
assert all(sha(Path(p))==h for p,h in report['sourceHashes'].items())
assert all(x['minimumTerminalBurialBelowActualSupportMeters']>.029 for x in report['rootPlans'])
out=dict(passed=True,checks=allresults,sourceTriangleUVExact=True,upperCrownAbove4_9LocalExact=True,sourceInputsUnchanged=True,rootTopEnvelopeTests=report['rootPlans'],nativeNavRecheckRequired=True,visualAcceptance='Pending actual direct preview review')
(W/'export-qa.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
