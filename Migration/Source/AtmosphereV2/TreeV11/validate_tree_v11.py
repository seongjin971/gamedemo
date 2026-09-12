"""Independent native Unity export validation; no Blender or Unity dependency."""
from pathlib import Path
import json,hashlib, numpy as np
W=Path(__file__).resolve().parent;D=W/'derivative'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
protected=json.loads((W/'protected-input-hashes.json').read_text())
checks={n:sha(W/n)==h for n,h in protected.items()};assert all(checks.values())
results=[]
for filename in ['tree-v11-base-mesh.json','tree-v11-art-directed-mesh.json']:
 d=json.loads((D/filename).read_text());p=np.array(d['positions']).reshape(-1,3);n=np.array(d['normals']).reshape(-1,3);uv=np.array(d['uv']).reshape(-1,2);c=np.array(d['colors']).reshape(-1,4);idx=np.array(d['indices']).reshape(-1,3)
 assert len(p)==len(n)==len(uv)==len(c)
 assert all(np.isfinite(a).all() for a in (p,n,uv,c));assert idx.min()>=0 and idx.max()<len(p)
 assert len(idx)>=120000 and len(idx)<=180000
 lengths=np.linalg.norm(n,axis=1);assert np.max(np.abs(lengths-1))<1e-5
 a,b,e=p[idx[:,0]],p[idx[:,1]],p[idx[:,2]];cross=np.cross(b-a,e-a);summed=n[idx].sum(axis=1);dot=(cross*summed).sum(axis=1);area=np.linalg.norm(cross,axis=1)*.5
 alignment=dot/(np.linalg.norm(cross,axis=1)*np.linalg.norm(summed,axis=1))
 assert area.min()>1e-12 and dot.min()>0
 assert abs(np.ptp(p[:,1])-6.4)<1e-5 and abs(p[:,1].min()+.06)<1e-6 and abs(np.ptp(p[:,0])-6.3)<1e-5
 root=p[p[:,1]<-.06+6.4*.08];centre=(root.min(axis=0)+root.max(axis=0))*.5;assert max(abs(centre[0]),abs(centre[2]))<1e-5
 results.append(dict(file=filename,sha256=sha(D/filename),vertices=len(p),triangles=len(idx),finite=True,indexRangeValid=True,minimumTriangleArea=float(area.min()),minimumFaceMeanNormalAlignment=float(alignment.min()),strictNonpositiveDotTriangles=int((dot<=0).sum()),unityNegativeDotOutliers=int((dot < -1e-10).sum()),maxNormalLengthError=float(np.max(np.abs(lengths-1))),boundsUnity=[p.min(axis=0).tolist(),p.max(axis=0).tolist()],spansUnity=np.ptp(p,axis=0).tolist(),rootRegionXZCentre=centre[[0,2]].tolist(),uvBounds=[uv.min(axis=0).tolist(),uv.max(axis=0).tolist()],uvUniqueCount=len(np.unique(uv,axis=0)),whiteVertexColor=bool((c==1).all())))
report=dict(passed=True,workingConvention='Unity Cross(pb-pa,pc-pa) dot (na+nb+nc), strict positive additionally; threshold -1e-10',protectedOriginalFilesUnchanged=checks,results=results)
(D/'export-qa.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
