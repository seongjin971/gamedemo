"""CPU-only nominal guide/clip budget check; not final AO/mesh validation."""
import ast,json,math
from pathlib import Path
import numpy as np
OUT=Path(__file__).resolve().parent
tree=ast.parse((OUT/'build_hybrid_v14.py').read_text())
for node in tree.body:
 if isinstance(node,ast.FunctionDef) and node.name in ['inside','area','clip','clean','triangulate']:
  exec(compile(ast.Module(body=[node],type_ignores=[]),str(OUT/'build_hybrid_v14.py'),'exec'))
m=json.loads((OUT.parent/'PavingV11/heightfield-metadata.json').read_text());bounds=m['world_bounds'];rect=m['coverage_rectangles_xz'][0]
guides=json.loads((OUT/'source_seeds.json').read_text())['slabs'];templates=[]
for g in guides:
 raw=np.array(g['polygon'],float)/[2048,1024];raw[:,1]=1-raw[:,1];raw*=[12.4,6.2];points=[]
 for a,b in zip(raw,np.roll(raw,-1,axis=0)):
  steps=max(2,math.ceil(np.linalg.norm(b-a)/.19));points.extend(a+(b-a)*k/steps for k in range(steps))
 poly=np.array(points);poly=.7*poly+.15*np.roll(poly,1,axis=0)+.15*np.roll(poly,-1,axis=0)
 if sum(np.cross(a,b) for a,b in zip(poly,np.roll(poly,-1,axis=0)))<0:poly=poly[::-1]
 templates.append(poly)
selected=[]
for tx in (-1,0):
 for tz in range(-1,5):
  for poly in templates:
   poly=poly+[tx*12.4,tz*6.2]
   for axis,value,sign in [(0,bounds[0][0],1),(0,bounds[1][0],-1),(1,rect[2],1),(1,bounds[1][2],-1)]:
    if len(poly)<3:break
    poly=clip(poly,axis,value,sign)
   poly=clean(poly)
   if area(poly)<.035:continue
   selected.append(poly)
report={'nominal_body_count':len(selected),'estimated_triangles_including_36032_bed':sum(len(p)*8-8 for p in selected)+36032,'stone_surface_coverage_ratio':sum(area(p) for p in selected)/((rect[1]-rect[0])*(rect[3]-rect[2])),'period':[12.4,6.2],'note':'Nominal manually traced guides only. Final bounded AO refinement, normals and export QA remain required.'}
assert 450<=len(selected)<=550
(OUT/'layout-preflight.json').write_text(json.dumps(report,indent=2));print(report)
