import json,math,hashlib
from pathlib import Path
OUT=Path(__file__).resolve().parent;ROOT=next(p for p in OUT.parents if (p/'ArtSource').is_dir())
build=json.loads((OUT/'build-validation.json').read_text());manifest=json.loads((OUT/'rubble-removal-manifest.json').read_text());evidence=json.loads((OUT/'world-contact-evidence.json').read_text());bridge_file=ROOT/'Unity/Vesper/Assets/Vesper/Import/unity-scene.json';bridge=json.loads(bridge_file.read_text());nodes={n['id']:n for n in bridge['nodes']}
assert hashlib.sha256(bridge_file.read_bytes()).hexdigest()==manifest['bridge_sha256']
seen=set()
for row in manifest['instances']+manifest['retained_instances']:
 key=(row['nodeId'],row['instanceIndex']);assert key not in seen;seen.add(key);node=nodes[row['nodeId']];actual=node['instances'][row['instanceIndex']]
 assert node['geometry']==row['geometry'] and node['materials']==[row['materialId']]
 assert all(actual[k]==row[k] for k in ['position','quaternion','scale','color'])
 assert row['materialId']=='08b6ee59-7da1-4fb0-bd5d-a752d5b8fa60' and max(row['scale'])<.8
assert len(manifest['instances'])==50 and len(manifest['retained_instances'])==49 and len(seen)==99
support=evidence['root4_wall_contact']['support'];assert (support['nodeId'],support['instanceIndex']) not in {(r['nodeId'],r['instanceIndex']) for r in manifest['instances']}
assert build['new_offcuts']==26 and len(build['pockets'])==4 and len(build['clusters'])==4
reports=[]
for item in build['exports']:
 path=OUT/item['file'];d=json.loads(path.read_text());p=d['positions'];n=d['normals'];ix=d['indices'];count=len(p)//3
 assert len(n)==len(p) and len(d['uv'])==2*count and len(d['colors'])==4*count and all(math.isfinite(v) for key in ['positions','normals','uv','colors'] for v in d[key])
 assert min(ix)>=0 and max(ix)<count and len(ix)%3==0
 bad=degenerate=0;minimum=1e20
 edges={};signed_volume=0
 for k in range(0,len(ix),3):
  ids=ix[k:k+3];a,b,c=[p[3*i:3*i+3] for i in ids];u=[b[j]-a[j] for j in range(3)];v=[c[j]-a[j] for j in range(3)];cross=[u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]];normal=[sum(n[3*i+j] for i in ids) for j in range(3)];dot=sum(cross[j]*normal[j] for j in range(3));bad+=dot<=0;degenerate+=sum(t*t for t in cross)<1e-18;minimum=min(minimum,dot);signed_volume+=sum(a[j]*cross[j] for j in range(3))/6
  coords=[tuple(round(v,6) for v in point) for point in [a,b,c]]
  for j in range(3):edge=tuple(sorted((coords[j],coords[(j+1)%3])));edges[edge]=edges.get(edge,0)+1
 boundary=sum(v!=2 for v in edges.values());error=max(abs(math.sqrt(sum(t*t for t in n[k:k+3]))-1) for k in range(0,len(n),3));assert bad==0 and degenerate==0 and boundary==0 and error<1e-5 and signed_volume>0,(path.name,bad,degenerate,boundary,error,signed_volume)
 bounds=[[min(p[a::3]) for a in range(3)],[max(p[a::3]) for a in range(3)]]
 assert all(3.8<=p[k]<=9.041 and -.14<=p[k+1]<=.45 and -7.8<=p[k+2]<=7 for k in range(0,len(p),3))
 assert all(r['nonmanifold_edges_welded']==0 and r['signed_volume_m3']>0 for r in item['objects'])
 detail={'file':path.name,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'vertices':count,'triangles':len(ix)//3,'nonpositive_normal_dot':bad,'degenerate_triangles':degenerate,'welded_edge_errors':boundary,'minimum_cross_dot_sum_normals':minimum,'max_normal_length_error':error,'signed_volume_m3':signed_volume,'bounds':bounds}
 if 'rubble' in path.name:
  cursor=0;diameters={}
  for body in item['objects']:
   end=cursor+body['triangles']*9;coords=list(set((p[k],p[k+2]) for k in range(cursor,end,3)));diameter=max(math.hypot(a[0]-b[0],a[1]-b[1]) for a in coords for b in coords);diameters.setdefault(int(body['name'].split()[1]),[]).append(diameter);cursor=end
  detail['cluster_fragment_diameter_ranges']=[{'cluster':k,'min_m':min(v),'max_m':max(v),'ratio':max(v)/min(v)} for k,v in sorted(diameters.items())];assert all(2<r['ratio']<4 for r in detail['cluster_fragment_diameter_ranges'])
 reports.append(detail)
assert hashlib.sha256((OUT.parent/'TreeV12/derivative/tree-v12-mesh.json').read_bytes()).hexdigest()==evidence['tree_sha256']
assert hashlib.sha256((ROOT/evidence['paving_source']).read_bytes()).hexdigest()==evidence['paving_sha256']
result={'status':'PASS','exact_removed_instances':50,'retained_instances':49,'rubble_clusters':4,'new_closed_fragments':26,'closed_contact_pockets':4,'tree_and_paving_sources_preserved':True,'meshes':reports}
(OUT/'independent-validation.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
