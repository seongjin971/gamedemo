"""Independent serialized export validation; system Python, no Blender."""
import json,math,hashlib
from pathlib import Path
from collections import Counter
OUT=Path(__file__).resolve().parent;SRC=OUT.parent/'PavingV15/paving-v15-mesh.json';FILE=OUT/'paving-v16-mesh.json'
before=json.loads(SRC.read_text());g=json.loads(FILE.read_text());m=json.loads((OUT/'fracture-metadata.json').read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def sub(a,b):return [a[i]-b[i] for i in range(3)]
def cross(a,b):return [a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]]
def dot(a,b):return sum(x*y for x,y in zip(a,b))
p=g['positions'];n=g['normals'];ids=g['indices'];qa={'mesh_sha256':sha(FILE),'source_sha256':sha(SRC),'vertex_prefix_exact':all(g[k][:len(before[k])]==before[k] for k in ['positions','normals','uv','colors']),'unchanged_parts_exact':True,'new_parts':[],'triangles':len(ids)//3,'nonpositive':0,'degenerate':0,'max_normal_error':0,'max_new_uv_error':0,'new_nonfinite':0}
for part in m['parts']:
 a=part['index_start'];b=a+part['index_count']
 if 'original_index_start' in part:
  old=part['original_index_start'];qa['unchanged_parts_exact'] &= ids[a:b]==before['indices'][old:old+part['index_count']]
for i in range(0,len(n),3):qa['max_normal_error']=max(qa['max_normal_error'],abs(math.sqrt(dot(n[i:i+3],n[i:i+3]))-1))
for t in range(0,len(ids),3):
 tri=ids[t:t+3];a,b,c=[p[3*i:3*i+3] for i in tri];cr=cross(sub(b,a),sub(c,a))
 if dot(cr,cr)<1e-24:qa['degenerate']+=1
 if not all(dot(cr,n[3*i:3*i+3])>0 for i in tri):qa['nonpositive']+=1
for i in range(len(before['positions'])//3,len(p)//3):
 qa['max_new_uv_error']=max(qa['max_new_uv_error'],abs(g['uv'][2*i]-p[3*i]/12.4),abs(g['uv'][2*i+1]-p[3*i+2]/6.2))
 qa['new_nonfinite']+=sum(not math.isfinite(v) for v in p[i*3:i*3+3]+n[i*3:i*3+3]+g['uv'][i*2:i*2+2])
for part in m['parts']:
 if not part['name'].startswith('V16_'):continue
 edges=Counter();directed=Counter();volume=0;area_top=0;coords=[]
 for t in range(part['index_start'],part['index_start']+part['index_count'],3):
  tri=[tuple(round(x,7) for x in p[3*i:3*i+3]) for i in ids[t:t+3]];coords+=tri;cr=cross(sub(tri[1],tri[0]),sub(tri[2],tri[0]));area_top+=max(0,cr[1])*.5;volume+=dot(tri[0],cross(tri[1],tri[2]))/6
  for a,b in zip(tri,tri[1:]+tri[:1]):edges[tuple(sorted((a,b)))]+=1;directed[(a,b)]+=1
 closed=all(v==2 for v in edges.values()) and all(v==directed[(b,a)] for (a,b),v in directed.items())
 q={'name':part['name'],'closed_oriented':closed,'signed_volume':volume,'projected_top_area':area_top,'bounds':[[f(v[k] for v in coords) for k in range(3)] for f in [min,max]]}
 if part['name'].startswith('V16_Hero'):
  s=next(s for s in m['selected_records'] if 'V16_'+s['name']==part['name']);poly=s['raw_polygon_world_xz'];area=abs(sum(a[0]*b[1]-a[1]*b[0] for a,b in zip(poly,poly[1:]+poly[:1])))*.5;q['expected_area']=area;q['area_error']=abs(area_top-area)
 qa['new_parts'].append(q)
qa['passed']=qa['vertex_prefix_exact'] and qa['unchanged_parts_exact'] and not qa['nonpositive'] and not qa['degenerate'] and not qa['new_nonfinite'] and qa['max_normal_error']<1e-5 and qa['max_new_uv_error']<1e-6 and all(q['closed_oriented'] and q['signed_volume']>0 and q.get('area_error',0)<1e-5 for q in qa['new_parts']) and qa['triangles']<120000
def orient(a,b,c):return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
def inside(point,poly):
 ans=False
 for a,b in zip(poly,poly[1:]+poly[:1]):
  if (a[1]>point[1])!=(b[1]>point[1]) and point[0]<(b[0]-a[0])*(point[1]-a[1])/(b[1]-a[1])+a[0]:ans=not ans
 return ans
def overlap(p,q):
 if any(max(x[k] for x in p)<=min(x[k] for x in q) or max(x[k] for x in q)<=min(x[k] for x in p) for k in [0,1]):return False
 crossing=any(orient(a,b,c)*orient(a,b,d)<-1e-12 and orient(c,d,a)*orient(c,d,b)<-1e-12 for a,b in zip(p,p[1:]+p[:1]) for c,d in zip(q,q[1:]+q[:1]))
 return crossing or any(inside(x,q) for x in p) or any(inside(x,p) for x in q)
def hull(points):
 pts=sorted(set(points));lower=[];upper=[]
 for x in pts:
  while len(lower)>=2 and orient(lower[-2],lower[-1],x)<=0:lower.pop()
  lower.append(x)
 for x in reversed(pts):
  while len(upper)>=2 and orient(upper[-2],upper[-1],x)<=0:upper.pop()
  upper.append(x)
 return lower[:-1]+upper[:-1]
oldmeta=json.loads((OUT.parent/'PavingV14/hybrid-metadata.json').read_text());outlines={s['name']:s['polygon_world_xz'] for s in oldmeta['hero_stones']};selected_names={s['name'] for s in m['selected_records']}
for s in m['selected_records']:outlines[s['name']]=s['raw_polygon_world_xz']
qa['outline_or_fill_overlap_errors']=[]
for s in m['selected_records']:
 for name,poly in outlines.items():
  if name!=s['name'] and overlap(s['raw_polygon_world_xz'],poly):qa['outline_or_fill_overlap_errors'].append([s['name'],name])
for part in m['parts']:
 if not part['name'].startswith('V16_joint_fill'):continue
 number=int(part['name'].split('_')[3]);parent=next(s['name'] for s in m['selected_records'] if s['number']==number)
 points=hull([(p[3*i],p[3*i+2]) for i in ids[part['index_start']:part['index_start']+part['index_count']]])
 for name,poly in outlines.items():
  if name!=parent and overlap(points,poly):qa['outline_or_fill_overlap_errors'].append([part['name'],name])
qa['exact_world_bounds_preserved']=all(f(g['positions'][k::3])==f(before['positions'][k::3]) for k in range(3) for f in [min,max])
qa['valid_indices_and_strides']=len(p)%3==0 and len(ids)%3==0 and min(ids)>=0 and max(ids)<len(p)//3 and len(n)==len(p) and len(g['uv'])==len(p)//3*2 and len(g['colors'])==len(p)//3*4
qa['new_colors_white_finite']=all(math.isfinite(v) and v==1 for v in g['colors'][len(before['colors']):])
qa['passed'] &= not qa['outline_or_fill_overlap_errors'] and qa['exact_world_bounds_preserved'] and qa['valid_indices_and_strides'] and qa['new_colors_white_finite']
(OUT/'export-qa.json').write_text(json.dumps(qa,indent=2));assert qa['passed'],qa
print('PAVING_V16_INDEPENDENT_QA_PASS',qa['triangles'],qa['mesh_sha256'])
