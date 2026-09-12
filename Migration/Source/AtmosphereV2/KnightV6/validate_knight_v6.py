"""Independent pure Python audit matching live Unity NativeMesh cross/dot rule."""
import json,math,hashlib
from pathlib import Path
W=Path(__file__).resolve().parent;S=W.parent/'KnightV5';ROOT=next(p for p in W.parents if (p/'ArtSource').is_dir());OUT=ROOT/'.dream-loop/unity-atmosphere-v2/knight-v6'
old=json.loads((S/'knight-v5-unity-meshes.json').read_text());new=json.loads((W/'knight-v6-unity-meshes.json').read_text());helmet=json.loads((W/'helmet-v6-unity-mesh.json').read_text())
assert old['coordinateBasis']==new['coordinateBasis']==helmet['coordinateBasis']
assert [e['gameObjectName'] for e in old['objects']]==[e['gameObjectName'] for e in new['objects']]
cross=lambda a,b:[a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]]
dot=lambda a,b:sum(x*y for x,y in zip(a,b))
def check(e,strict):
 ps=e['positions'];ns=e['normals'];uv=e['uv'];ids=e['indices'];n=e['vertexCount'];assert len(ps)==len(ns)==n*3 and len(uv)==n*2 and len(ids)==e['triangleCount']*3
 assert all(math.isfinite(v) for array in (ps,ns,uv) for v in array);assert all(type(i)==int and 0<=i<n for i in ids)
 maxerr=max(abs(math.sqrt(dot(ns[i:i+3],ns[i:i+3]))-1) for i in range(0,len(ns),3));assert maxerr<1e-5
 minarea=math.inf;minimum=1;negative=0;unityoutliers=0
 for i in range(0,len(ids),3):
  ix=ids[i:i+3];a,b,c=[ps[k*3:k*3+3] for k in ix];normal=[sum(ns[k*3+j] for k in ix) for j in range(3)]
  face=cross([b[j]-a[j] for j in range(3)],[c[j]-a[j] for j in range(3)]);length=math.sqrt(dot(face,face));area=length*.5;minarea=min(minarea,area);alignment=dot(face,normal)
  if alignment<0:negative+=1
  if alignment < -1e-10:unityoutliers+=1
  if length>0:minimum=min(minimum,alignment/(length*math.sqrt(dot(normal,normal))))
 if strict:assert minarea>1e-12 and minimum>0 and unityoutliers==0 and negative==0,(e['gameObjectName'],minarea,minimum,negative)
 return dict(name=e['gameObjectName'],vertices=n,triangles=e['triangleCount'],minArea=minarea,minFaceAverageNormalAlignment=minimum,negativeDotTriangles=negative,unityOutliers=unityoutliers,unityOutlierThreshold=-1e-10,maxNormalLengthError=maxerr,bounds=[[min(ps[k::3]),max(ps[k::3])] for k in range(3)])
before=[check(e,False) for e in old['objects']];after=[check(e,True) for e in new['objects']+helmet['objects']]
preserved=[a['gameObjectName'] for a,b in zip(new['objects'],old['objects']) if a==b]
assert 'Heavy_folded_crimson_cape' in preserved and len(preserved)==5
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
report=dict(passed=True,capeRecordExact=True,recordNamesOrderExact=True,exactRecords=preserved,workingUnityConvention='NativeMesh uses Dot(Cross(pb-pa,pc-pa),na+nb+nc); outlier threshold -1e-10; every final normalized dot additionally strictly positive',before=before,after=after,sha256={p.name:sha(p) for p in [W/'knight-v6-unity-meshes.json',W/'helmet-v6-unity-mesh.json',W/'knight-v6.blend',W/'build_knight_v6.py',S/'knight-v5-unity-meshes.json',S/'knight-v5.blend']})
(W/'export-qa.json').write_text(json.dumps(report,indent=2));(OUT/'export-qa.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
