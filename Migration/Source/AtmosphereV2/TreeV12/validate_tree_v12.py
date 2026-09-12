from pathlib import Path
import json,hashlib,ast,numpy as np
W=Path(__file__).resolve().parent;D=W/'derivative';S=W.parent/'TreeV11';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
d=json.loads((D/'tree-v12-mesh.json').read_text());p=np.array(d['positions']).reshape(-1,3);n=np.array(d['normals']).reshape(-1,3);uv=np.array(d['uv']).reshape(-1,2);c=np.array(d['colors']).reshape(-1,4);ids=np.array(d['indices']).reshape(-1,3)
assert all(np.isfinite(a).all() for a in (p,n,uv,c));assert len(p)==len(n)==len(uv)==len(c);assert ids.min()>=0 and ids.max()<len(p);assert len(ids)==157999
cross=np.cross(p[ids[:,1]]-p[ids[:,0]],p[ids[:,2]]-p[ids[:,0]]);summed=n[ids].sum(axis=1);dots=(cross*summed).sum(axis=1);area=np.linalg.norm(cross,axis=1)*.5;alignment=dots/(2*area*np.linalg.norm(summed,axis=1));normerr=np.abs(np.linalg.norm(n,axis=1)-1)
assert dots.min()>0 and area.min()>1e-12 and normerr.max()<1e-5
assert abs(p[:,1].max()-6.34)<1e-5 and abs(np.ptp(p[:,0])-6.3)<1e-5
old=json.loads((S/'derivative/tree-v11-art-directed-mesh.json').read_text());op=np.array(old['positions']).reshape(-1,3);oi=np.array(old['indices']).reshape(-1,3);ouv=np.array(old['uv']).reshape(-1,2)
assert np.array_equal(ouv[oi],uv[ids])
oc=np.cross(op[oi[:,1]]-op[oi[:,0]],op[oi[:,2]]-op[oi[:,0]]);angle=(oc*cross).sum(axis=1)/(np.linalg.norm(oc,axis=1)*np.linalg.norm(cross,axis=1));visible=p[ids,1].max(axis=1)>.02
assert np.isfinite(angle).all() # Orientation to old face is diagnostic: large rotations alone do not prove a fold.
tree=ast.parse((W/'build_tree_v12.py').read_text());paths=ast.literal_eval(next(a.value for a in tree.body if isinstance(a,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='paths' for t in a.targets)))
ob=op[oi].reshape(-1,3)[:,[0,2,1]]*np.array([-1,-1,1]);nb=p[ids].reshape(-1,3)[:,[0,2,1]]*np.array([-1,-1,1]);xz=ob[:,[0,2]];forks=[]
for name,points,radius in paths:
 points=np.array(points);dist=np.full(len(ob),999.);near=np.zeros((len(ob),2));progress=np.zeros(len(ob));lengths=np.linalg.norm(np.diff(points,axis=0),axis=1);cum=np.r_[0,np.cumsum(lengths)]
 for j,(a,b) in enumerate(zip(points[:-1],points[1:])):
  v=b-a;t=np.clip(((xz-a)*v).sum(axis=1)/(v*v).sum(),0,1);q=a+t[:,None]*v;dd=np.linalg.norm(xz-q,axis=1);take=dd<dist;near[take]=q[take];dist[take]=dd[take];progress[take]=(cum[j]+t[take]*lengths[j])/cum[-1]
 sample=(dist<radius*.65)&(progress>.18)&(progress<.76)&(np.abs(ob[:,1])<.70)
 oldr=np.sqrt(dist**2+ob[:,1]**2);newr=np.sqrt(((nb[:,[0,2]]-near)**2).sum(axis=1)+nb[:,1]**2);ratio=newr[sample]/np.maximum(oldr[sample],1e-8)
 forks.append(dict(region=name,sampledTriangleCorners=int(sample.sum()),medianPerpendicularRadiusRatio=float(np.median(ratio)),medianReductionPercent=float(100*(1-np.median(ratio))),ratio10to90Percentile=np.percentile(ratio,[10,90]).tolist()))
preserved={k:sha(S/k)==v for k,v in json.loads((W/'protected-v11-hashes.json').read_text()).items()};assert all(preserved.values())
r=dict(passed=True,measuredForkRadii=forks,sourceTriangleUVExact=True,visibleFaceOrientationMinimum=float(angle[visible].min()),visibleFacesRotatedOver90Degrees=int((angle[visible]<=0).sum()),vertices=len(p),triangles=len(ids),minimumArea=float(area.min()),minimumFaceMeanNormalAlignment=float(alignment.min()),strictNonpositiveDots=int((dots<=0).sum()),unityThresholdOutliers=int((dots < -1e-10).sum()),maximumNormalLengthError=float(normerr.max()),nativeBounds=[p.min(axis=0).tolist(),p.max(axis=0).tolist()],uvBounds=[uv.min(axis=0).tolist(),uv.max(axis=0).tolist()],whiteVertexColors=bool((c==1).all()),preservedV11Files=preserved,sha256={f.name:sha(f) for f in [D/'tree-v12-mesh.json',D/'tree-v12.blend',W/'build_tree_v12.py']})
(D/'export-qa.json').write_text(json.dumps(r,indent=2));print(json.dumps({k:v for k,v in r.items() if k!='preservedV11Files'},indent=2))
