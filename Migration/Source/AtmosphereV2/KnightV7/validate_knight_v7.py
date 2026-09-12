"""Independent V7 JSON audit, using the established native Unity cross/dot rule."""
import json,math,hashlib
from pathlib import Path
W=Path(__file__).resolve().parent;S=W.parent/'KnightV6';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
a=json.loads((S/'knight-v6-unity-meshes.json').read_text());b=json.loads((W/'knight-v7-unity-meshes.json').read_text());h=json.loads((W/'helmet-v6-unity-mesh.json').read_text());KEY='Heavy_folded_crimson_cape'
assert a['coordinateBasis']==b['coordinateBasis']==h['coordinateBasis'];assert [x['gameObjectName'] for x in a['objects']]==[x['gameObjectName'] for x in b['objects']]
assert all(x==y for x,y in zip(a['objects'],b['objects']) if x['gameObjectName']!=KEY)
assert sha(S/'helmet-v6-unity-mesh.json')==sha(W/'helmet-v6-unity-mesh.json')
old=next(x for x in a['objects'] if x['gameObjectName']==KEY);new=next(x for x in b['objects'] if x['gameObjectName']==KEY);assert old['uv']==new['uv'] and old['indices']==new['indices'];assert old['vertexCount']==new['vertexCount'] and old['triangleCount']==new['triangleCount']
cross=lambda a,b:[a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]]
dot=lambda a,b:sum(x*y for x,y in zip(a,b))
results=[]
for e in b['objects']+h['objects']:
 p=e['positions'];n=e['normals'];uv=e['uv'];ids=e['indices'];count=e['vertexCount'];assert len(p)==len(n)==count*3 and len(uv)==count*2;assert len(ids)==e['triangleCount']*3
 assert all(math.isfinite(v) for array in (p,n,uv) for v in array);assert all(type(i)==int and 0<=i<count for i in ids)
 errors=[abs(math.sqrt(dot(n[i:i+3],n[i:i+3]))-1) for i in range(0,len(n),3)];assert max(errors)<1e-5
 minarea=math.inf;minalign=1;nonpositive=0
 for i in range(0,len(ids),3):
  ix=ids[i:i+3];aa,bb,cc=[p[k*3:k*3+3] for k in ix];f=cross([bb[k]-aa[k] for k in range(3)],[cc[k]-aa[k] for k in range(3)]);avg=[sum(n[k*3+j] for k in ix) for j in range(3)];fl=math.sqrt(dot(f,f));area=fl*.5;align=dot(f,avg)/(fl*math.sqrt(dot(avg,avg)));minarea=min(minarea,area);minalign=min(minalign,align);nonpositive+=int(dot(f,avg)<=0)
 assert minarea>1e-12 and minalign>0 and nonpositive==0
 results.append(dict(name=e['gameObjectName'],vertices=count,triangles=e['triangleCount'],minTriangleArea=minarea,minFaceMeanNormalAlignment=minalign,strictNonpositiveDotTriangles=nonpositive,maxNormalLengthError=max(errors),bounds=[[min(p[k::3]),max(p[k::3])] for k in range(3)]))
assert abs((max(new['positions'][::3])-min(new['positions'][::3]))-(max(old['positions'][::3])-min(old['positions'][::3])))<1e-6
pin=[i for i in range(new['vertexCount']) if new['uv'][i*2+1]<=.14];assert all(new['positions'][i*3:i*3+3]==old['positions'][i*3:i*3+3] for i in pin)
hem={side:[] for side in ['left','right']}
for i in range(new['vertexCount']):
 u,t=new['uv'][i*2:i*2+2]
 if t>.9999 and (u<1e-6 or u>1-1e-6):hem['left' if u<.5 else 'right'].append(new['positions'][i*3+1]-old['positions'][i*3+1])
hemdiff=sum(hem['right'])/len(hem['right'])-sum(hem['left'])/len(hem['left']);assert abs(hemdiff-.0714)<1e-5
preserved={name:sha(S/name)==value for name,value in json.loads((W/'protected-v6-hashes.json').read_text()).items()};assert all(preserved.values())
r=dict(passed=True,exactSixOtherRecords=True,helmetSupplementByteExact=True,capeUVAndIndexBuffersExact=True,collarPositionVerticesExact=len(pin),measuredHemAuthoredLeftRightDifferenceMeters=hemdiff,checks=results,sourceFilesPreserved=preserved,sha256={p.name:sha(p) for p in [W/'knight-v7-unity-meshes.json',W/'knight-v7.blend',W/'helmet-v6-unity-mesh.json',W/'build_knight_v7.py']})
(W/'export-qa.json').write_text(json.dumps(r,indent=2),encoding='utf-8');print(json.dumps({k:v for k,v in r.items() if k!='sourceFilesPreserved'},indent=2))
