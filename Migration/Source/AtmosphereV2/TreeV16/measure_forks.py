"""Read-only actual V12/V16 corresponding triangle-corner cross-section audit."""
import ast,json
from pathlib import Path
import numpy as np
W=Path(__file__).resolve().parent
code=ast.parse((W/'build_tree_v16.py').read_text(encoding='utf-8-sig'))
items=[n for n in code.body if (isinstance(n,ast.FunctionDef) and n.name in ('smooth','closest','forks')) or (isinstance(n,ast.Assign) and any(isinstance(x,ast.Name) and x.id=='paths' for x in n.targets))]
exec(compile(ast.Module(body=items,type_ignores=[]),'section_functions','exec'))
def corners(path):
 d=json.loads(path.read_text());p=np.array(d['positions']).reshape(-1,3);idx=np.array(d['indices']);p=p[idx];return np.c_[-p[:,0],-p[:,2],p[:,1]]
old=corners(W.parent/'TreeV12/derivative/tree-v12-mesh.json');new=corners(W/'tree-v16-mesh.json');rows=[]
for name,points,radius in paths:
 dist,near,prog=closest(old,np.array(points));ro=np.linalg.norm(old-near,axis=1);rn=np.linalg.norm(new-near,axis=1);mask=(prog>.20)&(prog<.78)&(ro<radius)&(ro>.10)
 ratios=rn[mask]/ro[mask];bins=[]
 for a in [.22,.32,.42,.52,.62]:
  sel=mask&(prog>=a)&(prog<a+.10)
  if sel.sum()<20:continue
  before=np.percentile(ro[sel],95);after=np.percentile(rn[sel],95);bins.append(dict(progress=[a,a+.10],samples=int(sel.sum()),beforeRadius95=float(before),afterRadius95=float(after),outer95ReductionPercent=float((1-after/before)*100)))
 rows.append(dict(region=name,selection='Entire radial core including outer bark up to documented radius; axial .20-.78. No deformation-weight filtering.',coreRadiusLocal=radius,triangleCornerSamples=int(mask.sum()),medianRadiusReductionPercent=float(100*(1-np.median(ratios))),radiusRatio10to90=np.percentile(ratios,[10,90]).tolist(),sections=bins))
(W/'fork-section-measurements.json').write_text(json.dumps(rows,indent=2));print(json.dumps(rows,indent=2))
