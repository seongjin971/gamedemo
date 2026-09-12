"""Normal-only diagnostic derivative. Prepared only; run after root releases QA.

Default computes a report in memory. --export writes a separately named candidate
only after every invariant passes. Never modifies the frozen PavingV13 source.
"""
import argparse,collections,hashlib,json,math
from pathlib import Path

OUT=Path(__file__).resolve().parent;SOURCE=OUT.parent/'PavingV13'
EXPECTED='dd46aefd74c0470bfea77fee2d22df8c72a1d2d47a75d18e7e6944c0c8f87e3c'

def sha(data):return hashlib.sha256(data).hexdigest()
def canonical(values):return json.dumps(values,separators=(',',':')).encode()
def cross(a,b,c):
 x,y,z=(b[k]-a[k] for k in range(3));u,v,w=(c[k]-a[k] for k in range(3))
 return (y*w-z*v,z*u-x*w,x*v-y*u)
def unit(v):
 length=math.sqrt(sum(x*x for x in v));assert length>1e-15
 return tuple(x/length for x in v)
def dot(a,b):return sum(x*y for x,y in zip(a,b))
def angle(a,b):return math.degrees(math.acos(max(-1,min(1,dot(unit(a),unit(b))))))
def on_or_inside(x,z,poly):
 inside=False
 for a,b in zip(poly,poly[1:]+poly[:1]):
  dx,dz=b[0]-a[0],b[1]-a[1];length=dx*dx+dz*dz
  t=max(0,min(1,((x-a[0])*dx+(z-a[1])*dz)/length)) if length else 0
  if (x-a[0]-t*dx)**2+(z-a[1]-t*dz)**2<=1e-12:return True
  if ((a[1]>z)!=(b[1]>z)) and x<(b[0]-a[0])*(z-a[1])/(b[1]-a[1])+a[0]:inside=not inside
 return inside

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--export',action='store_true');args=parser.parse_args()
 raw=(SOURCE/'paving-v13-mesh.json').read_bytes();assert sha(raw)==EXPECTED,'frozen source hash changed'
 g=json.loads(raw);metadata=json.loads((SOURCE/'hybrid-metadata.json').read_text())
 original_normals=list(g['normals']);p=g['positions'];uv=g['uv'];idx=g['indices'];vertex_count=len(p)//3
 frozen={key:sha(canonical(g[key])) for key in ['positions','indices','uv','colors']}
 normals=list(original_normals);changed=set();eligible=set();cap_ids=set();reports=[]
 for part,stone in zip(metadata['parts'][1:],metadata['hero_stones']):
  assert part['name']==stone['name'];indices=idx[part['index_start']:part['index_start']+part['index_count']]
  used=set(indices);poly=stone['cap_polygon_world_xz']
  # Classify from actual cap boundary/height, never from a global Y-normal
  # threshold that could accidentally include a shallow bevel or another slab.
  is_cap_vertex={i:p[3*i+1]>-.08 and on_or_inside(p[3*i],p[3*i+2],poly) for i in used}
  cap=[];noncap_used=set();area_sums=collections.defaultdict(lambda:[0.,0.,0.]);groups=collections.defaultdict(set)
  plane_sum=[0.,0.,0.]
  for k in range(0,len(indices),3):
   tri=indices[k:k+3];pts=[p[i*3:i*3+3] for i in tri];face=cross(*pts)
   if face[1]>0 and all(is_cap_vertex[i] for i in tri):
    cap.append((tri,face));cap_ids.update(tri)
    for axis in range(3):plane_sum[axis]+=face[axis]
    for i in tri:
     key=tuple(p[i*3:i*3+3])+tuple(uv[i*2:i*2+2]);groups[key].add(i)
     for axis in range(3):area_sums[key][axis]+=face[axis]
   else:noncap_used.update(tri)
  assert cap,('no cap faces',part['name'])
  shared=set().union(*groups.values())&noncap_used
  # Preserve exact topology: any rare cap/side shared index remains unchanged,
  # rather than modifying its side normal or inserting a new vertex/index.
  for key,ids in groups.items():
   smooth=unit(area_sums[key])
   for i in ids-shared:
    eligible.add(i)
    normals[i*3:i*3+3]=[round(x,9) for x in smooth]
    if normals[i*3:i*3+3]!=original_normals[i*3:i*3+3]:changed.add(i)
  new_plane=[0.,0.,0.]
  for tri,face in cap:
   weight=math.sqrt(dot(face,face));mean=[sum(normals[3*i+a] for i in tri)/3 for a in range(3)]
   for axis in range(3):new_plane[axis]+=weight*mean[axis]
  tilt=stone['plane_slope_xz'];reference=unit((-tilt[0],1.,-tilt[1]))
  reports.append({'name':part['name'],'cap_triangles':len(cap),'cap_position_uv_groups':len(groups),'shared_cap_side_vertices_preserved':len(shared),'geometry_cap_mean_normal':unit(plane_sum),'smoothed_cap_mean_normal':unit(new_plane),'mean_normal_angle_change_degrees':angle(plane_sum,new_plane),'authored_plane_reference':reference})
 # Evaluate every triangle, including the untouched bed, bevels, sides and
 # bottoms. A failed normal candidate is not exported; no index flip/fallback
 # or weakened threshold masks a failure.
 positive=0;minimum_dot=float('inf');minimum_cos=1.
 for k in range(0,len(idx),3):
  tri=idx[k:k+3];face=cross(*(p[i*3:i*3+3] for i in tri));mean=[sum(normals[i*3+a] for i in tri) for a in range(3)]
  value=dot(face,mean);assert value>0,('normal derivative flips a face',k//3,value)
  positive+=1;minimum_dot=min(minimum_dot,value);minimum_cos=min(minimum_cos,dot(unit(face),unit(mean)))
 assert all(math.isfinite(v) for v in normals)
 lengths=[math.sqrt(sum(v*v for v in normals[i:i+3])) for i in range(0,len(normals),3)]
 assert max(abs(x-1) for x in lengths)<1e-6
 assert all(normals[3*i:3*i+3]==original_normals[3*i:3*i+3] for i in range(vertex_count) if i not in eligible)
 g['normals']=normals;g['id']='paving-v13-normals1-cap-area-weighted';g['name']='PavingV13Normals1CapAreaWeighted'
 assert all(sha(canonical(g[key]))==digest for key,digest in frozen.items())
 assert changed and changed<=eligible<=cap_ids
 report={'status':'QA_PASSED_UNRENDERED_NORMAL_DIAGNOSTIC','source_mesh_sha256':EXPECTED,'preserved_array_sha256':frozen,'triangles':len(idx)//3,'vertices':vertex_count,'changed_normal_vertices':len(changed),'cap_eligible_vertices':len(eligible),'positive_dot':positive,'negative_or_zero_dot':0,'minimum_positive_dot':minimum_dot,'minimum_face_mean_normal_cosine':minimum_cos,'normal_length_range':[min(lengths),max(lengths)],'all_noncap_normals_unchanged':True,'all_positions_indices_uv_colors_unchanged':True,'maximum_stone_cap_mean_angle_change_degrees':max(s['mean_normal_angle_change_degrees'] for s in reports),'stone_reports':reports,'limits':['Normal smoothing does not change the rounded pad silhouette, physical raised arris, residual-height shadows, source course repetition or water BRDF.','Separate per-stone averaging preserves each geometry plane rather than flattening the floor to global Y-up.','Native appearance is unverified until a new explicit diagnostic capture.']}
 payload=canonical(g);report['mesh_sha256']=sha(payload)
 assert sha((SOURCE/'paving-v13-mesh.json').read_bytes())==EXPECTED
 if args.export:
  (OUT/'paving-v13-normals1-mesh.json').write_bytes(payload)
  (OUT/'normals-qa.json').write_text(json.dumps(report,indent=2))
 print(json.dumps({k:v for k,v in report.items() if k!='stone_reports'},indent=2))

if __name__=='__main__':main()
