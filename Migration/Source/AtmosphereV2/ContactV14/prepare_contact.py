"""Freeze exact rubble identities and measure world-space root contact evidence."""
import json,math,hashlib,argparse
from pathlib import Path
OUT=Path(__file__).resolve().parent;ROOT=next(p for p in OUT.parents if (p/'ArtSource').is_dir())
BRIDGE=ROOT/'Unity/Vesper/Assets/Vesper/Import/unity-scene.json';bridge=json.loads(BRIDGE.read_text());nodes={n['id']:n for n in bridge['nodes']}
parser=argparse.ArgumentParser();parser.add_argument('--paving-version',type=int,choices=(13,14),default=14);args=parser.parse_args()
TREE=ROOT/'Migration/Source/AtmosphereV2/TreeV12/derivative/tree-v12-mesh.json';CONTACTS=TREE.with_name('root-footprint-and-contacts.json');PAVING=ROOT/('Migration/Source/AtmosphereV2/PavingV'+str(args.paving_version)+'/paving-v'+str(args.paving_version)+'-mesh.json')
tree=json.loads(TREE.read_text());contacts=json.loads(CONTACTS.read_text());paving=json.loads(PAVING.read_text());pp=paving['positions'];pi=paving['indices']
parent=nodes['1a37e0e4-35a6-42e2-8273-6a870b9c1c98'];yaw=-math.radians(20)-2*math.atan2(parent['quaternion'][1],parent['quaternion'][3]);cs,sn=math.cos(yaw),math.sin(yaw);scale=parent['scale'][0];origin=[-parent['position'][0],parent['position'][1],parent['position'][2]]
def world(p):return [origin[0]+scale*(cs*p[0]+sn*p[2]),origin[1]+scale*p[1],origin[2]+scale*(-sn*p[0]+cs*p[2])]
def top_at(x,z):
 heights=[]
 for k in range(0,len(pi),3):
  a,b,c=[pp[3*i:3*i+3] for i in pi[k:k+3]]
  if not min(a[0],b[0],c[0])-1e-7<=x<=max(a[0],b[0],c[0])+1e-7 or not min(a[2],b[2],c[2])-1e-7<=z<=max(a[2],b[2],c[2])+1e-7:continue
  det=(b[2]-c[2])*(a[0]-c[0])+(c[0]-b[0])*(a[2]-c[2])
  if abs(det)<1e-10:continue
  u=((b[2]-c[2])*(x-c[0])+(c[0]-b[0])*(z-c[2]))/det;v=((c[2]-a[2])*(x-c[0])+(a[0]-c[0])*(z-c[2]))/det;w=1-u-v
  if min(u,v,w)>=-1e-6:heights.append(u*a[1]+v*b[1]+w*c[1])
 return max(heights) if heights else None
measured=[];tp=tree['positions']
for item in contacts['rootContacts']:
 w=world(item['measuredVisibleContactVertex']);row={'root':item['root'],'original_local_vertex':item['measuredVisibleContactVertex'],'original_world_vertex':w,'original_source_vertex_index':item['sourceVertexIndex'],'original_paving_top_y':top_at(w[0],w[2])}
 if row['original_paving_top_y'] is None or w[0]>8.7:
  candidates=[];angle=item['designDirectionRadiansBlender'];width=[.35,.30,.32,.40][item['root']-1]
  for ix in range(0,len(tp),3):
   p=tp[ix:ix+3]
   if not -.005<=p[1]<=.13:continue
   theta=math.atan2(-p[2],-p[0]);diff=math.atan2(math.sin(theta-angle),math.cos(theta-angle));v=world(p)
   if abs(diff)<width*.75 and v[0]<8.7 and math.hypot(p[0],p[2])>.55:candidates.append((math.hypot(p[0],p[2]),ix//3,p,v))
  candidates.sort(reverse=True)
  for radius,ix,p,v in candidates:
   h=top_at(v[0],v[2])
   if h is not None:
    row['alternative_inner_contact']={'local_vertex':p,'world_vertex':v,'source_vertex_index':ix,'paving_top_y':h,'height_above_paving':v[1]-h,'candidate_count':len(candidates)};break
 measured.append(row)
clusters=[{'id':0,'center_xz':[6.0,-6.35],'radius':.87,'pieces':7,'lengths':[.92,.65,.48,.34,.28,.23,.25]},
 {'id':1,'center_xz':[7.95,-4.0],'radius':.78,'pieces':5,'lengths':[.84,.60,.37,.26,.22]},
 {'id':2,'center_xz':[5.65,-2.5],'radius':.72,'pieces':6,'lengths':[.78,.52,.42,.30,.21,.25]},
 {'id':3,'center_xz':[7.9,.48],'radius':.87,'pieces':8,'lengths':[.96,.66,.56,.41,.32,.27,.25,.24]}]
for cluster in clusters:cluster['lengths']=[max(.28,length) for length in cluster['lengths']]
rubble=[]
for n in bridge['nodes']:
 if n.get('materials')!=['08b6ee59-7da1-4fb0-bd5d-a752d5b8fa60']:continue
 for ix,i in enumerate(n.get('instances',[])):
  p=i['position'];s=i['scale'];x=-p[0];z=p[2]
  side=7.3-1e-5<=x<=8.75+1e-5 and -5.9-1e-5<=z<=12+1e-5 and abs(p[1]-s[0]*.35)<1e-6 and .099<=s[0]<=.461
  rear=4.7-1e-5<=x<=7.3+1e-5 and -7.8-1e-5<=z<=-1.8+1e-5 and abs(p[1]-s[0]*.4)<1e-6 and abs(s[1]-s[0]*.75)<1e-6 and .129<=s[0]<=.491
  if (side or rear) and z<1.8:
   row={'nodeId':n['id'],'instanceIndex':ix,'geometry':n['geometry'],'materialId':n['materials'][0],'kind':'rear_offcut' if rear else 'parapet_offcut',**i};row['world_position']=[x,p[1],z];row['cluster_distance']=min(math.hypot(x-c['center_xz'][0],z-c['center_xz'][1])/c['radius'] for c in clusters);rubble.append(row)
# Remove the most isolated old offcuts first, leaving existing stones near
# clusters. Exact IDs are frozen; runtime must never rerun a broad region delete.
rubble.sort(key=lambda r:(-r['cluster_distance'],r['nodeId'],r['instanceIndex']));remove=rubble[:(len(rubble)+1)//2];keep=rubble[len(remove):]
manifest={'bridge_sha256':hashlib.sha256(BRIDGE.read_bytes()).hexdigest(),'selection_basis':'src/world.js explicit two rubble loops; exact placement/scale equations and material identify loose offcuts. Then only native left/rear region z<1.8. Half removed by isolation from four authored cluster centers.','candidate_count':len(rubble),'removed_count':len(remove),'retained_count':len(keep),'instances':remove,'retained_instances':keep}
(OUT/'rubble-removal-manifest.json').write_text(json.dumps(manifest,indent=2));(OUT/'cluster-plan.json').write_text(json.dumps(clusters,indent=2))
evidence={'tree_sha256':hashlib.sha256(TREE.read_bytes()).hexdigest(),'contact_source_sha256':hashlib.sha256(CONTACTS.read_bytes()).hexdigest(),'paving_sha256':hashlib.sha256(PAVING.read_bytes()).hexdigest(),'paving_source':str(PAVING.relative_to(ROOT)),'native_tree_parent':{'position':origin,'scale':parent['scale'],'quaternion':[0,-parent['quaternion'][1],0,parent['quaternion'][3]]},'mesh_local_yaw_degrees':-20,'combined_yaw_degrees':math.degrees(yaw),'contacts':measured,'paving_bounds':[[min(pp[a::3]) for a in range(3)],[max(pp[a::3]) for a in range(3)]]}
wallnode=nodes['592370d4-d68c-4fe8-b91d-41e1eaa41394'];wallix=682;wall=wallnode['instances'][wallix];selected=[ix for ix,i in enumerate(wallnode['instances']) if -10<=i['position'][0]<=10 and -13<=i['position'][2]<=22 and -3<=i['position'][1]<=15];j=selected.index(wallix)
evidence['root4_wall_contact']={'sourceVertexIndex':61633,'nativeLocalVertex':tp[61633*3:61633*3+3],'worldVertex':world(tp[61633*3:61633*3+3]),'support':{'nodeId':wallnode['id'],'instanceIndex':wallix,'geometry':wallnode['geometry'],'materialId':wallnode['materials'][0],'sourceVariant':(j+(j//100)*7)%6,**wall},'reason':'Fourth terminal sample is outside paving. An actual root vertex lies within 1.6mm of the nominal inward parapet plane; use a small vertical moss contact pocket projected to actual V12 stone geometry instead of a floating horizontal soil mound.'}
(OUT/'world-contact-evidence.json').write_text(json.dumps(evidence,indent=2));print(json.dumps({'rubble_candidates':len(rubble),'removed':len(remove),'retained':len(keep),'contacts':measured},indent=2))
