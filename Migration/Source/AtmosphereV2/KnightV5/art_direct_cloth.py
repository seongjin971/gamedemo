"""Restore silhouette while retaining corresponding simulated cloth displacement.
This is explicitly art-directed baked cloth, not an untouched settled simulation.
"""
import json,math
from pathlib import Path
W=Path(__file__).resolve().parent
d=json.loads((W/'attempt-03-flared/settled-cage.json').read_text());C=d['C'];R=d['R'];raw=d['vertices']
def filtered(j,i,k):
 total=weight=0.0
 for dj in range(-2,3):
  for di in range(-3,4):
   w=math.exp(-.5*((di/1.2)**2+(dj/1.0)**2));jj=max(0,min(R-1,j+dj));ii=max(0,min(C-1,i+di))
   total+=raw[jj*C+ii][k]*w;weight+=w
 return total/weight
smoothed=[tuple(filtered(j,i,k) for k in range(3)) for j in range(R) for i in range(C)]
out=[]
for j in range(R):
 t=j/(R-1);width=.17+.18*math.sin(t*math.pi*.6)
 row=smoothed[j*C:(j+1)*C];mean_z=sum(p[2] for p in row)/C
 for i in range(C):
  u=i/(C-1);s=2*u-1;v=row[i]
  # Restore broad v3 envelope, retain a small physically generated sideways drift.
  line_x=row[0][0]*(1-u)+row[-1][0]*u
  x=s*width+.05*t*t+.12*(v[0]-line_x)*math.sin(math.pi*t*.5)
  # Remove the global contraction/translation, keeping the simulation's curved,
  # nonperiodic cloth relief. Fine collar crumples were spatially low-pass filtered.
  line_y=row[0][1]*(1-u)+row[-1][1]*u
  relief=v[1]-line_y
  y=.023+.270*t+.070*t*t+.85*relief*min(1,t*8)
  sag=-.014*math.exp(-((s+.62)/.23)**2)-.025*math.exp(-((s-.02)/.29)**2)-.010*math.exp(-((s-.69)/.18)**2)
  z=-.956*t+.50*(v[2]-mean_z)*min(1,t*8)+t**5*sag
  if j==0:x=s*.17;y=.023;z=0
  out.append((x,y,z))
d['vertices']=out
(W/'settled-cage.json').write_text(json.dumps(d))
report=dict(status='ART_DIRECTED_CANDIDATE_REQUIRES_VISUAL_REVIEW',rawSimulation='attempt-03-flared/settled-cage.json',method='restore v3 broad envelope per grid row, retain low-pass filtered simulated relief and side drift, sculpt unequal shallow hem sags',untouchedSimulation=False,rawBounds=[[min(p[k] for p in raw),max(p[k] for p in raw)] for k in range(3)],artDirectedBounds=[[min(p[k] for p in out),max(p[k] for p in out)] for k in range(3)])
(W/'art-direction-report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
