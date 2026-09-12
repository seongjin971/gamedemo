import json,math,hashlib
from pathlib import Path
OUT=Path(__file__).resolve().parent;ROOT=next(p for p in OUT.parents if (p/'ArtSource').is_dir())
rows=[]
def volume(data):
 p=data['positions'];ix=data['indices'];v=0.0
 for i in range(0,len(ix),3):
  a,b,c=[p[3*k:3*k+3] for k in ix[i:i+3]]
  v+=a[0]*(b[1]*c[2]-b[2]*c[1])+a[1]*(b[2]*c[0]-b[0]*c[2])+a[2]*(b[0]*c[1]-b[1]*c[0])
 return abs(v/6)
for path in [OUT/'stairs-v13-mesh.json']+sorted(OUT.glob('localized-masonry-v13-*.json')):
 d=json.loads(path.read_text());p=d['positions'];n=d['normals'];ix=d['indices'];count=len(p)//3
 assert len(p)==len(n)==count*3 and len(d['uv'])==count*2
 assert all(math.isfinite(v) for key in ['positions','normals','uv'] for v in d[key])
 assert min(ix)>=0 and max(ix)<count and len(ix)%3==0
 negative=degenerate=0;minimum=1e9
 for i in range(0,len(ix),3):
  a,b,c=[p[3*k:3*k+3] for k in ix[i:i+3]];u=[b[k]-a[k] for k in range(3)];v=[c[k]-a[k] for k in range(3)];cross=[u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]]
  avg=[sum(n[3*k+j] for k in ix[i:i+3]) for j in range(3)];dot=sum(cross[j]*avg[j] for j in range(3));negative+=dot<=0;degenerate+=sum(x*x for x in cross)<1e-20;minimum=min(minimum,dot)
 normerror=max(abs(math.sqrt(sum(x*x for x in n[i:i+3]))-1) for i in range(0,len(n),3));assert not negative and not degenerate and normerror<1e-5
 bounds=[[min(p[a::3]) for a in range(3)],[max(p[a::3]) for a in range(3)]]
 if path.name.startswith('localized'):assert all(-.500001<=x<=.500001 for b in bounds for x in b)
 rows.append({'id':d['id'],'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'triangles':len(ix)//3,'vertices':count,'negative_normal_dots':negative,'degenerate_triangles':degenerate,'minimum_cross_dot_sum_corner_normals':minimum,'max_normal_length_error':normerror,'bounds':bounds})
manifest=json.loads((OUT/'architecture-overrides.json').read_text());bridge_path=ROOT/'Unity/Vesper/Assets/Vesper/Import/unity-scene.json';assert hashlib.sha256(bridge_path.read_bytes()).hexdigest()==manifest['bridge_sha256'];nodes={n['id']:n for n in json.loads(bridge_path.read_text())['nodes']};seen=set()
for row in manifest['overrides']:
 key=(row['nodeId'],row['instanceIndex']);assert key not in seen;seen.add(key);node=nodes[key[0]];inst=node['instances'][key[1]]
 assert node['geometry']==row['geometry'] and node['materials']==[row['materialId']]
 assert all(inst[k]==row[k] for k in ['position','quaternion','scale','color'])
 replacement=json.loads((OUT/row['replacement']).read_text());original=json.loads((OUT.parent/'MasonryV12'/('masonry-v12-'+str(row['sourceVariant'])+'.json')).read_text())
 ratio=volume(replacement)/volume(original);assert .75<ratio<=1.00001,(row['replacement'],ratio)
 next(r for r in rows if r['id']==replacement['id'])['volume_fraction_of_v12']=ratio
assert len(rows)==9 and len(seen)==8
qa=json.loads((OUT/'build-validation.json').read_text());assert len(qa['stair_nose_losses'])==30 and all(0<r['depth']<=.05 and 0<r['vertical_loss']<=.05 for r in qa['stair_nose_losses']);assert all(r['nonmanifold_edges_welded']==0 for r in qa['meshes'])
assert len(qa['stair_volumes'])==90 and all(r['vertices']>0 and .90<r['ratio']<=1 and r['original_components']==r['final_components'] for r in qa['stair_volumes'])
stairs=json.loads((OUT/'stairs-v13-mesh.json').read_text());original_stairs=json.loads((ROOT/'Migration/Source/AtmosphereV2/MasonryV11/stairs-v11-mesh.json').read_text());assert set(stairs['colors'][0::4])==set(original_stairs['colors'][0::4]) and len(set(stairs['colors'][0::4]))==90
result={'status':'PASS','exact_architecture_overrides':8,'stair_nose_losses':30,'meshes':rows,'source_v11_unchanged':hashlib.sha256((ROOT/'Migration/Source/AtmosphereV2/MasonryV11/stairs-v11-mesh.json').read_bytes()).hexdigest()==qa['source_v11_mesh_sha256'],'source_v12_unchanged':hashlib.sha256((ROOT/'Migration/Source/AtmosphereV2/MasonryV12/independent-validation.json').read_bytes()).hexdigest()==qa['source_v12_validation_sha256']};assert result['source_v11_unchanged'] and result['source_v12_unchanged'];(OUT/'independent-validation.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
