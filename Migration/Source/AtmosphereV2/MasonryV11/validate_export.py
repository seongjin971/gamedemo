"""Independent native-array and source omission contract audit; standard Python."""
import json, math, hashlib
from pathlib import Path
OUT=Path(__file__).resolve().parent
ROOT=next(p for p in OUT.parents if (p/'ArtSource').is_dir())
mesh=json.loads((OUT/'stairs-v11-mesh.json').read_text())
manifest=json.loads((OUT/'stair-removal-manifest.json').read_text())
bridge_path=ROOT/'Unity/Vesper/Assets/Vesper/Import/unity-scene.json'
bridge=json.loads(bridge_path.read_text());nodes={n['id']:n for n in bridge['nodes']}
assert hashlib.sha256(bridge_path.read_bytes()).hexdigest()==manifest['bridge_sha256']
seen=set()
for row in manifest['instances']:
    key=(row['nodeId'],row['instanceIndex']);assert key not in seen;seen.add(key)
    node=nodes[key[0]];original=node['instances'][key[1]]
    assert node['geometry']==row['geometry'] and node['materials']==[row['materialId']]
    assert all(row[k]==original[k] for k in ['position','quaternion','scale','color'])
p=mesh['positions'];n=mesh['normals'];ix=mesh['indices'];count=len(p)//3
assert len(p)==len(n)==count*3 and len(mesh['uv'])==count*2 and len(mesh['colors'])==count*4
assert all(math.isfinite(v) for key in ['positions','normals','uv','colors'] for v in mesh[key])
assert min(ix)>=0 and max(ix)<count and len(ix)%3==0
negative=degenerate=0;minimum=1e10
for i in range(0,len(ix),3):
    a,b,c=[p[3*k:3*k+3] for k in ix[i:i+3]];u=[b[k]-a[k] for k in range(3)];v=[c[k]-a[k] for k in range(3)]
    cross=[u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]]
    avg=[sum(n[3*vertex+k] for vertex in ix[i:i+3]) for k in range(3)]
    dot=sum(cross[k]*avg[k] for k in range(3));minimum=min(minimum,dot)
    negative+=dot<=0;degenerate+=sum(c*c for c in cross)<1e-20
assert not negative and not degenerate
norm_error=max(abs(math.sqrt(sum(v*v for v in n[i:i+3]))-1) for i in range(0,len(n),3));assert norm_error<1e-5
report={'status':'PASS','mesh_sha256':hashlib.sha256((OUT/'stairs-v11-mesh.json').read_bytes()).hexdigest(),'vertices':count,'triangles':len(ix)//3,'positive_normal_dot_triangles':len(ix)//3-negative,'minimum_cross_dot_three_corner_normals':minimum,'degenerate_triangles':degenerate,'max_normal_length_error':norm_error,'exact_source_removals':len(seen),'source_counts':manifest['counts'],'finite':True,'valid_indices':True,'limits':'Array and identity checks do not establish native visual acceptance.'}
(OUT/'independent-validation.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
