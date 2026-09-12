"""CPU-only source guide preflight; final AO-refined export QA is separate."""
import ast,json,math
from pathlib import Path
import numpy as np
OUT=Path(__file__).resolve().parent
tree=ast.parse((OUT/'build_hybrid_v13.py').read_text())
for node in tree.body:
 if isinstance(node,ast.FunctionDef) and node.name in ['inside','area','clip','clean','triangulate']:
  exec(compile(ast.Module(body=[node],type_ignores=[]),str(OUT/'build_hybrid_v13.py'),'exec'))
guides=json.loads((OUT/'source_seeds.json').read_text())['slabs'];results=[]
for g in guides:
 raw=np.array(g['polygon'],float)/[2048,1024];raw[:,1]=1-raw[:,1];raw*=np.array([9.2,4.6])
 points=[]
 for a,b in zip(raw,np.roll(raw,-1,axis=0)):
  steps=max(2,math.ceil(np.linalg.norm(b-a)/.19))
  points.extend(a+(b-a)*k/steps for k in range(steps))
 poly=np.array(points);poly=.7*poly+.15*np.roll(poly,1,axis=0)+.15*np.roll(poly,-1,axis=0)
 if sum(np.cross(a,b) for a,b in zip(poly,np.roll(poly,-1,axis=0)))<0:poly=poly[::-1]
 poly=clean(poly);n=len(poly);inset=[]
 for j,p in enumerate(poly):
  prev=p-poly[(j-1)%n];nxt=poly[(j+1)%n]-p;prev/=np.linalg.norm(prev);nxt/=np.linalg.norm(nxt)
  npv=np.array([-prev[1],prev[0]]);nnx=np.array([-nxt[1],nxt[0]]);direction=npv+nnx;direction/=np.linalg.norm(direction)
  width=((.018+.012*(.5+.5*math.sin(j/n*math.tau*2))) if g.get('subordinate') else (.032+.020*(.5+.5*math.sin(j/n*math.tau*2))))/max(.6,float(np.dot(direction,npv)))
  inset.append(direction*width)
 inset=np.array(inset);scale=1.;error=None
 for attempt in range(5):
  top=poly+inset*scale
  try:
   assert np.all(inside(top[:,0],top[:,1],poly))
   tris=triangulate(top);assert abs(sum(area(t) for t in tris)-area(top))<1e-7
   triangulate(poly);break
  except AssertionError as exc:error=str(exc);scale*=.5
 else:raise AssertionError((g['id'],error))
 results.append({'id':g['id'],'n':n,'inset_scale':scale,'body_area':area(poly),'cap_area':area(top)})
report={'source_contours':len(results),'body_ratio':sum(s['body_area'] for s in results)/(9.2*4.6),'cap_ratio':sum(s['cap_area'] for s in results)/(9.2*4.6),'inset_reduced':[s for s in results if s['inset_scale']<1],'estimated_body_triangles_per_tile':sum(s['n']*8-8 for s in results),'results':results}
(OUT/'contour-preflight.json').write_text(json.dumps(report,indent=2));print({k:v for k,v in report.items() if k not in ['results','inset_reduced']});print('REDUCED',len(report['inset_reduced']))
