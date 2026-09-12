"""Independent numeric review of eight drop-in native meshes."""
import json,math,hashlib
from pathlib import Path
OUT=Path(__file__).resolve().parent
rows=[]
for pattern in ['masonry-v12-*.json','facade-v12-*.json']:
 for path in sorted(OUT.glob(pattern)):
  d=json.loads(path.read_text());p=d['positions'];n=d['normals'];ix=d['indices'];count=len(p)//3
  assert len(p)==len(n)==count*3 and len(d['uv'])==count*2
  assert all(math.isfinite(v) for key in ['positions','normals','uv'] for v in d[key])
  assert min(ix)>=0 and max(ix)<count and len(ix)%3==0
  bounds=[[min(p[a::3]) for a in range(3)],[max(p[a::3]) for a in range(3)]];assert bounds==[[-.5]*3,[.5]*3]
  negative=degenerate=0;minimum=1e10
  for i in range(0,len(ix),3):
   a,b,c=[p[3*k:3*k+3] for k in ix[i:i+3]];u=[b[k]-a[k] for k in range(3)];v=[c[k]-a[k] for k in range(3)]
   cross=[u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]]
   avg=[sum(n[3*vertex+k] for vertex in ix[i:i+3]) for k in range(3)];dot=sum(cross[k]*avg[k] for k in range(3));minimum=min(minimum,dot)
   negative+=dot<=0;degenerate+=sum(q*q for q in cross)<1e-20
  normerror=max(abs(math.sqrt(sum(v*v for v in n[i:i+3]))-1) for i in range(0,len(n),3))
  assert not negative and not degenerate and normerror<1e-5
  budget=800 if path.name.startswith('masonry') else 180;assert len(ix)//3<=budget
  rows.append({'id':d['id'],'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'triangles':len(ix)//3,'vertices':count,'unit_bounds_exact':True,'finite':True,'valid_indices':True,'negative_normal_dots':negative,'degenerate_triangles':degenerate,'minimum_cross_dot_sum_corner_normals':minimum,'max_normal_length_error':normerror,'budget':budget})
assert len(rows)==8,len(rows)
result={'status':'PASS','meshes':rows,'limitations':'Numeric export validation does not establish native visual acceptance.'};(OUT/'independent-validation.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
