"""Independent serialized geometry, exact source identity and preservation audit."""
from pathlib import Path
import json,hashlib,collections,math
import numpy as np
OUT=Path(__file__).resolve().parent;ROOT=next(p for p in OUT.parents if (p/'ArtSource').is_dir());SRC=OUT.parent
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
bridgepath=ROOT/'Unity/Vesper/Assets/Vesper/Import/unity-scene.json';bridge=load(bridgepath);bhash=hashlib.sha256(bridgepath.read_bytes()).hexdigest();nodes={n['id']:n for n in bridge['nodes']}
reports=[]
for file in sorted(OUT.glob('*-mesh.json'))+sorted(OUT.glob('hero-v16-*.json')):
 d=load(file);p=np.array(d['positions']).reshape(-1,3);n=np.array(d['normals']).reshape(-1,3);uv=np.array(d['uv']).reshape(-1,2);c=np.array(d['colors']).reshape(-1,4);idx=np.array(d['indices']).reshape(-1,3)
 assert len(p)==len(n)==len(uv)==len(c) and all(np.isfinite(a).all() for a in (p,n,uv,c))
 assert idx.min()>=0 and idx.max()<len(p)
 a,b,cc=p[idx[:,0]],p[idx[:,1]],p[idx[:,2]];cr=np.cross(b-a,cc-a);area=np.linalg.norm(cr,axis=1);dots=(cr*n[idx].sum(axis=1)).sum(axis=1)
 assert (area>1e-11).all(),(file.name,'degenerate',int((area<=1e-11).sum()))
 assert (dots>1e-11).all(),(file.name,'winding',int((dots<=1e-11).sum()))
 assert np.max(np.abs(np.linalg.norm(n,axis=1)-1))<1e-5
 pf=p.astype(np.float32).astype(float);nf=n.astype(np.float32).astype(float)
 cf=np.cross(pf[idx[:,1]]-pf[idx[:,0]],pf[idx[:,2]]-pf[idx[:,0]])
 fd=(cf*nf[idx].sum(axis=1)).sum(axis=1)
 assert (fd>0).all() and (np.linalg.norm(cf,axis=1)>1e-12).all(),(file.name,'Unity float32 rounding')
 partreports=[]
 for part in d['parts']:
  tris=idx[part['index_start']//3:(part['index_start']+part['index_count'])//3];unique={};edges=collections.Counter()
  for t in tris:
   ids=[]
   for i in t:
    key=tuple(np.round(p[i],6));unique.setdefault(key,len(unique));ids.append(unique[key])
   for i,j in zip(ids,ids[1:]+ids[:1]):edges[tuple(sorted((i,j)))]+=1
  errors=sum(v!=2 for v in edges.values());assert errors==0,(file.name,part['name'],'edge',errors)
  ps=p[tris];volume=float((ps[:,0]*np.cross(ps[:,1],ps[:,2])).sum()/6);assert volume>1e-8,(file.name,part['name'],volume)
  partreports.append({'name':part['name'],'triangles':len(tris),'closed_edge_errors':errors,'volume_m3_or_normalized':volume})
 reports.append({'file':file.name,'sha256':hashlib.sha256(file.read_bytes()).hexdigest(),'triangles':len(idx),'vertices':len(p),'bounds':[p.min(axis=0).tolist(),p.max(axis=0).tolist()],'minimum_normal_dot':float(dots.min()),'float32_minimum_normal_dot':float(fd.min()),'float32_bad_winding_or_degenerate':0,'parts':partreports})
for fname,key,count in [('hero-overrides.json','overrides',8),('facade-removal-manifest.json','instances',63)]:
 m=load(OUT/fname);assert m['bridge_sha256']==bhash and len(m[key])==count;identities=set()
 for r in m[key]:
  node=nodes[r['nodeId']];original=node['instances'][r['instanceIndex']]
  assert node['geometry']==r['geometry'] and node['materials'][0]==r['materialId']
  for f in ('position','quaternion','scale','color'):assert original[f]==r[f],(fname,r['instanceIndex'],f)
  identities.add((r['nodeId'],r['instanceIndex']))
 assert len(identities)==count
pres=load(OUT/'stair-preservation.json');old=load(SRC/'MasonryV13/stairs-v13-mesh.json');new=load(OUT/'stairs-v16-mesh.json')
assert hashlib.sha256((SRC/'MasonryV13/stairs-v13-mesh.json').read_bytes()).hexdigest()==pres['source_sha256']
assert len(pres['preserved'])==45 and len(pres['replaced'])==45
newparts=[p for p in new['parts'] if p.get('preserved')];assert len(newparts)==45
for record,part in zip(pres['preserved'],newparts):
 original_indices=[v for t in record['indices'] for v in old['indices'][t:t+3]];new_indices=new['indices'][part['index_start']:part['index_start']+part['index_count']]
 assert len(original_indices)==len(new_indices)
 for oi,ni in zip(original_indices,new_indices):
  for field,width in [('positions',3),('normals',3),('uv',2),('colors',4)]:assert old[field][oi*width:(oi+1)*width]==new[field][ni*width:(ni+1)*width],(part['name'],field)
result={'status':'PASS','exact_untouched_stair_bodies':45,'exact_hero_instances':8,'exact_facade_removals':63,'bridge_sha256':bhash,'meshes':reports}
(OUT/'independent-validation.json').write_text(json.dumps(result,indent=2));print('MASONRY_V16_QA_PASS',[(r['file'],r['triangles']) for r in reports])
