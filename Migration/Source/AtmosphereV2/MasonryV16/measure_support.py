"""First-hit front support clearance and actual geometric normal angles."""
import json,math
from pathlib import Path
import numpy as np
root=Path(__file__).resolve().parent;d=json.loads((root/'stairs-v16-mesh.json').read_text());p=np.array(d['positions']).reshape(-1,3);idx=np.array(d['indices']).reshape(-1,3);bad=[];worst=1;angles=[];records=[]
for part in d['parts']:
 if part.get('preserved'):continue
 row=int(part['name'].split()[-1].split('-')[0]);top=(row+1)*.29+.042;front=-1.75-row*.49+.291
 tris=p[idx[part['index_start']//3:(part['index_start']+part['index_count'])//3]];a,b,c=tris[:,0],tris[:,1],tris[:,2]
 cr=np.cross(b-a,c-a);normal=cr/np.linalg.norm(cr,axis=1)[:,None]
 den=(b[:,1]-c[:,1])*(a[:,0]-c[:,0])+(c[:,0]-b[:,0])*(a[:,1]-c[:,1]);ok=np.abs(den)>1e-14;den=np.where(ok,den,1)
 local=[];localmargin=1
 for x in np.linspace(tris[:,:,0].min()+.015,tris[:,:,0].max()-.015,17):
  for y in np.linspace(top-.29,top-.057,16):
   u=((b[:,1]-c[:,1])*(x-c[:,0])+(c[:,0]-b[:,0])*(y-c[:,1]))/den;v=((c[:,1]-a[:,1])*(x-c[:,0])+(a[:,0]-c[:,0])*(y-c[:,1]))/den;w=1-u-v;hit=ok&(u>=-1e-8)&(v>=-1e-8)&(w>=-1e-8)
   if not hit.any():bad.append((part['name'],'no ray hit'));continue
   z=u*a[:,2]+v*b[:,2]+w*c[:,2];ti=np.argmax(np.where(hit,z,-np.inf));margin=float(z[ti]-(front-.041));worst=min(worst,margin);localmargin=min(localmargin,margin)
   angle=math.degrees(math.acos(float(np.clip(normal[ti,2],-1,1))));angles.append(angle);local.append(angle)
   if margin<0:bad.append((part['name'],float(x),float(y),margin))
 records.append({'name':part['name'],'minimum_nominal_margin':localmargin,'normal_angle_median':float(np.median(local)),'normal_angle_p90':float(np.percentile(local,90)),'fraction_angles_14_to_25':sum(14<=a<=25 for a in local)/len(local)})
r={'samples':45*17*16,'minimum_nominal_support_front_margin_m':worst,'violations':bad,'normal_angle_median':float(np.median(angles)),'normal_angle_p90':float(np.percentile(angles,90)),'fraction_angles_14_to_25':sum(14<=a<=25 for a in angles)/len(angles),'parts':records,'interpretation':'First +Z surface ray sampled beneath original support top; nominal source support box, not a native shadow or all-points proof.'}
(root/'support-ray-validation.json').write_text(json.dumps(r,indent=2));print('Support rays',len(bad),worst,'angles median/p90',r['normal_angle_median'],r['normal_angle_p90']);assert not bad
