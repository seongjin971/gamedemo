"""Conditional local source correction. Pure Python; no DCC required for export.
Rigidly translate the single proven occluding slab 11mm down.
Every original X/Z, UV, index, color, and normal is preserved. Buried minimum Y
extends 11mm as explicitly approved; no rescale or AABB renormalization.
"""
import json, math, hashlib
from pathlib import Path
from collections import defaultdict,Counter
OUT=Path(__file__).resolve().parent;SOURCE=OUT.parent/'PavingV14/paving-v14-mesh.json'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def cross(a,b):return [a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]]
def minus(a,b):return [a[k]-b[k] for k in range(3)]
def dot(a,b):return sum(a[k]*b[k] for k in range(3))
def norm(a):return math.sqrt(dot(a,a))
source_hash=sha(SOURCE)
assert source_hash=='00ee641f13bdc841a4d0fd531379380a33952ee8f952133e750380e9e4be5c59'
before=json.loads(SOURCE.read_text());after=json.loads(SOURCE.read_text())
meta=json.loads((OUT.parent/'PavingV14/hybrid-metadata.json').read_text())
diag=json.loads((OUT/'before-v14-footprint-report.json').read_text())
hit=next(v for v in diag['views'] if v['view']=='full' and v['emitter']=='right')
name='HeroScanSlab_280_bottom_left_large'
assert hit['core_occluded_fraction']>.15 and hit['occluded_luminance_fraction']>.25 and set(hit['occluding_bodies'])=={name}
part=next(p for p in meta['parts'] if p['name']==name)
indices=after['indices'];active=set(indices[part['index_start']:part['index_start']+part['index_count']])
outside=set(indices[:part['index_start']]+indices[part['index_start']+part['index_count']:]);assert not(active&outside)
p=after['positions'];base=before['positions'];delta=.011
for i in active:
 p[3*i+1]=round(p[3*i+1]-delta,9)
# Translation's inverse-transpose is identity: preserve original geometry-derived
# cap normals and every hard split exactly; recomputing would add needless drift.
after['id']='paving-v15-local-drainage';after['name']='PavingV15LocalDrainage'

# Independent checks operate on final serialized geometry and all original parts.
target=OUT/'paving-v15-mesh.json';target.write_text(json.dumps(after,separators=(',',':')))
g=json.loads(target.read_text());p=g['positions'];ns=g['normals'];ids=g['indices']
qa={'source_sha256':source_hash,'mesh_sha256':sha(target),'triangles':len(ids)//3,'vertices':len(p)//3,
 'unchanged_arrays':{k:g[k]==before[k] for k in ['uv','indices','colors','normals']},
 'all_xz_unchanged':all(p[k]==base[k] for k in range(len(p)) if k%3!=1),
 'outside_vertices_unchanged':all(p[3*i:3*i+3]==base[3*i:3*i+3] and ns[3*i:3*i+3]==before['normals'][3*i:3*i+3] for i in outside),
 'bounds_before':[[f(base[k::3]) for k in range(3)] for f in [min,max]],
 'bounds_after':[[f(p[k::3]) for k in range(3)] for f in [min,max]],
 'modified_body':name,'modified_body_index_range':[part['index_start'],part['index_start']+part['index_count']],
 'modified_vertices':len(active),'max_down_m':max(base[3*i+1]-p[3*i+1] for i in active),
 'body_bounds_after':[[f(p[3*i+k] for i in active) for k in range(3)] for f in [min,max]],
 'strict_positive_triangle_normals':0,'nonpositive_triangle_normals':0,'degenerate_triangles':0,
 'closed_bodies':0,'bad_bodies':[],'max_unit_normal_error':max(abs(norm(ns[i:i+3])-1) for i in range(0,len(ns),3))}
assert all(math.isfinite(v) for k in ['positions','normals','uv','colors'] for v in g[k])
for t in range(0,len(ids),3):
 tri=ids[t:t+3];a,b,c=[p[3*i:3*i+3] for i in tri];n=cross(minus(b,a),minus(c,a));length=norm(n)
 if length<1e-12:qa['degenerate_triangles']+=1
 if all(dot(n,ns[3*i:3*i+3])>0 for i in tri):qa['strict_positive_triangle_normals']+=1
 else:qa['nonpositive_triangle_normals']+=1
for part0 in meta['parts'][1:]:
 edges=Counter();oriented=Counter();volume=0
 for t in range(part0['index_start'],part0['index_start']+part0['index_count'],3):
  tri=[tuple(round(v,7) for v in p[3*i:3*i+3]) for i in ids[t:t+3]]
  volume+=dot(tri[0],cross(tri[1],tri[2]))/6
  for a,b in zip(tri,tri[1:]+tri[:1]):edges[tuple(sorted((a,b)))]+=1;oriented[(a,b)]+=1
 closed=all(c==2 for c in edges.values()) and all(oriented[(a,b)]==oriented[(b,a)] for a,b in oriented)
 if closed and volume>0:qa['closed_bodies']+=1
 else:qa['bad_bodies'].append({'name':part0['name'],'closed':closed,'signed_volume':volume})
qa['bounds_note']='Exact X/Z preserved; buried min Y extends 11mm by explicit authorization. No normalization.'
qa['rigid_translation_error']=max(abs((base[3*i+1]-p[3*i+1])-delta) for i in active)
qa['passed']=all(qa['unchanged_arrays'].values()) and qa['all_xz_unchanged'] and qa['outside_vertices_unchanged'] and qa['rigid_translation_error']<1e-8 and qa['max_down_m']<=.015000001 and qa['nonpositive_triangle_normals']==0 and qa['degenerate_triangles']==0 and not qa['bad_bodies'] and qa['max_unit_normal_error']<1e-5
(OUT/'export-qa.json').write_text(json.dumps(qa,indent=2));assert sha(SOURCE)==source_hash
assert qa['passed'],qa
print(json.dumps(qa,indent=2))
