"""Independent exported geometric QA, no Blender or source mutation."""
import json,math,hashlib,collections,runpy
from pathlib import Path
OUT=Path(__file__).resolve().parent;ROOT=next(p for p in OUT.parents if (p/'ArtSource').is_dir())
orientation=runpy.run_path(str(OUT.parent/'PavingV11/validate_heightfield.py'))['orientation']
g=json.loads((OUT/'paving-v13-mesh.json').read_text());m=json.loads((OUT/'hybrid-metadata.json').read_text())
p=g['positions'];n=g['normals'];uv=g['uv'];count=len(p)//3
qa=orientation(g);qa['vertices']=count
qa['finite']=all(math.isfinite(v) for k in ['positions','normals','uv','colors'] for v in g[k])
qa['attribute_lengths_match']=len(n)==count*3 and len(uv)==count*2 and len(g['colors'])==count*4
qa['indices_valid']=min(g['indices'])>=0 and max(g['indices'])<count
lens=[math.sqrt(sum(v*v for v in n[k:k+3])) for k in range(0,len(n),3)];qa['normal_length_range']=[min(lens),max(lens)]
qa['hero_count']=len(m['hero_stones']);qa['parts']=[]
def polygon_area(poly):
 return abs(sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(poly,poly[1:]+poly[:1])))*.5
qa['foreground_area_m2']=m['foreground_area_m2']
qa['stone_surface_projected_area_m2']=sum(polygon_area(s['polygon_world_xz']) for s in m['hero_stones'])
qa['flat_cap_projected_area_m2']=sum(polygon_area(s['cap_polygon_world_xz']) for s in m['hero_stones'])
qa['stone_surface_coverage_ratio']=qa['stone_surface_projected_area_m2']/qa['foreground_area_m2']
qa['flat_cap_coverage_ratio']=qa['flat_cap_projected_area_m2']/qa['foreground_area_m2']
for part in m['parts']:
 inds=g['indices'][part['index_start']:part['index_start']+part['index_count']];used=set(inds);weld={};lookup={}
 for i in used:
  key=tuple(p[i*3:i*3+3]);weld.setdefault(key,len(weld));lookup[i]=weld[key]
 edges=collections.Counter();volume=0.0
 for k in range(0,len(inds),3):
  a,b,c=[lookup[i] for i in inds[k:k+3]]
  for aa,bb in [(a,b),(b,c),(c,a)]:edges[tuple(sorted((aa,bb)))]+=1
  aa,bb,cc=[p[i*3:i*3+3] for i in inds[k:k+3]]
  volume+=(aa[0]*(bb[1]*cc[2]-bb[2]*cc[1])+aa[1]*(bb[2]*cc[0]-bb[0]*cc[2])+aa[2]*(bb[0]*cc[1]-bb[1]*cc[0]))/6
 info={'name':part['name'],'triangles':len(inds)//3,'welded_boundary_edges':sum(c==1 for c in edges.values()),'overfull_edges':sum(c>2 for c in edges.values()),'min_y':min(p[i*3+1] for i in used),'max_y':max(p[i*3+1] for i in used)}
 if part['name'].startswith('Hero'):
  stone=next(s for s in m['hero_stones'] if s['name']==part['name']);cx,cz=stone['center'];sx,sz=stone['scale']
  info['source_uv_max_error']=max(max(abs(uv[i*2]-((p[i*3]-cx)/sx+cx)/9.2),abs(uv[i*2+1]-((p[i*3+2]-cz)/sz+cz)/4.6)) for i in used)
  assert info['source_uv_max_error']<1e-6
  assert info['welded_boundary_edges']==0 and info['overfull_edges']==0,info
  info['signed_closed_volume_m3']=volume;assert volume>0,('inside-out closed stone',info)
  # Independent signed projected area of all upward-facing body triangles
  # equals its footprint; overlapping/folded cap tessellation inflates it.
  projected=0.0
  for k in range(0,len(inds),3):
   aa,bb,cc=[p[i*3:i*3+3] for i in inds[k:k+3]]
   up=((bb[2]-aa[2])*(cc[0]-aa[0])-(bb[0]-aa[0])*(cc[2]-aa[2]))*.5
   projected+=max(0.,up)
  info['projected_top_area_m2']=projected
  info['projected_top_vs_footprint_error_m2']=abs(projected-polygon_area(stone['polygon_world_xz']))
  assert info['projected_top_vs_footprint_error_m2']<1e-5,('folded body surface',info)
 else:
  info['source_uv_max_error']=max(max(abs(uv[i*2]-p[i*3]/9.2),abs(uv[i*2+1]-p[i*3+2]/4.6)) for i in used)
  assert info['source_uv_max_error']<1e-6
 qa['parts'].append(info)
qa['exposed_stone_count']=sum(part['max_y']>-.004 for part in qa['parts'][1:])
qa['fully_submerged_stone_count']=sum(part['max_y']<=-.004 for part in qa['parts'][1:])
qa['sources_preserved']=all(hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h for p,h in m['source_sha256'].items())
qa['mesh_sha256']=hashlib.sha256((OUT/'paving-v13-mesh.json').read_bytes()).hexdigest()
qa['world_bounds']=[[min(p[a::3]) for a in range(3)],[max(p[a::3]) for a in range(3)]]
old=json.loads((OUT.parent/'PavingV11/heightfield-metadata.json').read_text())
qa['xz_bound_difference_m']=max(abs(qa['world_bounds'][k][a]-old['world_bounds'][k][a]) for k in (0,1) for a in (0,2))
assert qa['triangles']<160000 and qa['positive_dot']==qa['triangles'] and not qa['negative_dot'] and not qa['degenerate']
assert qa['finite'] and qa['indices_valid'] and qa['attribute_lengths_match'] and qa['sources_preserved']
assert max(abs(l-1) for l in lens)<1e-6 and qa['xz_bound_difference_m']<1e-6
assert qa['hero_count']>300 and qa['exposed_stone_count']>0 and qa['fully_submerged_stone_count']>0
assert .60<=qa['stone_surface_coverage_ratio']<=.75
qa['passed']=True
(OUT/'export-qa.json').write_text(json.dumps(qa,indent=2))
print(json.dumps({k:v for k,v in qa.items() if k!='parts'},indent=2))
