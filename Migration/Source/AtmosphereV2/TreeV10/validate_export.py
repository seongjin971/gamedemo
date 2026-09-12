"""Read-only JSON/source preservation and geometry QA; writes V10 evidence only."""
import json, math, hashlib
from pathlib import Path
ROOT=next(p for p in Path(__file__).resolve().parents if (p/'ArtSource').is_dir())
WORK=ROOT/'Migration/Source/AtmosphereV2/TreeV10';OUT=ROOT/'.dream-loop/unity-atmosphere-v2/tree-v10'
target=WORK/'tree-v10-mesh.json';d=json.loads(target.read_text());prior=json.loads((ROOT/'Migration/Source/AtmosphereV2/TreeV9/tree-v9-mesh.json').read_text());report=json.loads((OUT/'tree-v10-report.json').read_text())
p=d['positions'];n=d['normals'];uv=d['uv'];idx=d['indices'];count=len(p)//3
assert len(p)==len(n)==count*3 and len(uv)==count*2 and len(idx)%3==0
assert all(math.isfinite(x) for a in (p,n,uv) for x in a)
assert min(idx)>=0 and max(idx)<count
lengths=[math.sqrt(sum(n[i+j]**2 for j in range(3))) for i in range(0,len(n),3)]
assert max(abs(x-1) for x in lengths)<.002
degenerate=0;opposite=0;min_area=1e9
for i in range(0,len(idx),3):
    a,b,c=[p[v*3:v*3+3] for v in idx[i:i+3]];ab=[b[j]-a[j] for j in range(3)];ac=[c[j]-a[j] for j in range(3)]
    cross=[ab[1]*ac[2]-ab[2]*ac[1],ab[2]*ac[0]-ab[0]*ac[2],ab[0]*ac[1]-ab[1]*ac[0]]
    area=math.sqrt(sum(v*v for v in cross))*.5;min_area=min(min_area,area)
    if area<1e-12:degenerate+=1
    normal=[sum(n[v*3+j] for v in idx[i:i+3]) for j in range(3)]
    if sum(cross[j]*normal[j] for j in range(3))<0:opposite+=1
assert degenerate==0, 'Zero area triangle exported'
assert opposite==0, 'Triangle winding disagrees with normals'
bounds=lambda a:{'min':[min(a[j::3]) for j in range(3)],'max':[max(a[j::3]) for j in range(3)]}
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
source=ROOT/'Migration/Source/AtmosphereV2/TreeV9/tree-v9.blend'
assert sha(source)==report['source_sha256'];assert report['matrix_local']==report['source_matrix_local']
qa={'finite':True,'vertices':count,'triangles':len(idx)//3,'index_bounds':[min(idx),max(idx)],'normal_length_range':[min(lengths),max(lengths)],'degenerate_triangles':degenerate,'minimum_triangle_area':min_area,'triangles_opposed_to_average_normal':opposite,'bounds_unity':bounds(p),'previous_bounds_unity':bounds(prior['positions']),'source_v9_unchanged':True,'local_transform_identical':True,'coordinate_conversion':'(-x,z,-y); reversed triangle corners [0,2,1] exactly once','sha256':{f.name:sha(f) for f in [target,WORK/'tree-v10.blend',WORK/'build_tree_v10.py',source]}}
(WORK/'export-qa.json').write_text(json.dumps(qa,indent=2));(OUT/'export-qa.json').write_text(json.dumps(qa,indent=2));print(json.dumps(qa,indent=2))
