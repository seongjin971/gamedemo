"""Source-only masonry construction. No Unity writes or Blender launch."""
from pathlib import Path
import json,math,random,hashlib,collections
OUT=Path(__file__).resolve().parent
ROOT=next(p for p in OUT.parents if (p/'ArtSource').is_dir())
SRC=ROOT/'Migration/Source/AtmosphereV2'
BRIDGE=ROOT/'Unity/Vesper/Assets/Vesper/Import/unity-scene.json'
STONE='08b6ee59-7da1-4fb0-bd5d-a752d5b8fa60'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(name,data):
 p=OUT/name;p.write_text(json.dumps(data,separators=(',',':')));return hashlib.sha256(p.read_bytes()).hexdigest()
def dot(a,b):return sum(x*y for x,y in zip(a,b))
def sub(a,b):return tuple(x-y for x,y in zip(a,b))
def cross(a,b):return (a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])
def unit(a):
 d=math.sqrt(dot(a,a));return tuple(x/d for x in a)
def box(w,h,d):
 x=w/2;y=h/2;z=d/2
 return [[(-x,-y,-z),(-x,y,-z),(x,y,-z),(x,-y,-z)],
 [(x,-y,z),(x,y,z),(-x,y,z),(-x,-y,z)],
 [(-x,-y,z),(-x,y,z),(-x,y,-z),(-x,-y,-z)],
 [(x,-y,-z),(x,y,-z),(x,y,z),(x,-y,z)],
 [(-x,y,-z),(-x,y,z),(x,y,z),(x,y,-z)],
 [(-x,-y,z),(-x,-y,-z),(x,-y,-z),(x,-y,z)]]
def clip(faces,n,d):
 """Intersect a closed convex body with n.p<=d, retaining planar polygons."""
 result=[];boundary=[]
 for face in faces:
  out=[]
  for a,b in zip(face,face[1:]+face[:1]):
   da=dot(n,a)-d;db=dot(n,b)-d
   if da<=1e-10:out.append(a)
   if (da< -1e-10 and db>1e-10) or (da>1e-10 and db< -1e-10):
    t=da/(da-db);p=tuple(a[j]+(b[j]-a[j])*t for j in range(3));out.append(p);boundary.append(p)
   elif abs(da)<=1e-10:boundary.append(a)
  unique=[]
  for p in out:
   if not unique or sum((p[j]-unique[-1][j])**2 for j in range(3))>1e-18:unique.append(p)
  if len(unique)>2 and sum((unique[0][j]-unique[-1][j])**2 for j in range(3))<1e-18:unique.pop()
  if len(unique)>=3:result.append(unique)
 uniq={tuple(round(v,10) for v in p):p for p in boundary};ring=list(uniq.values())
 if len(ring)>=3:
  center=tuple(sum(p[j] for p in ring)/len(ring) for j in range(3));nn=unit(n);u=unit(cross(nn,(0,1,0) if abs(nn[1])<.9 else (1,0,0)));v=cross(nn,u)
  ring.sort(key=lambda p:math.atan2(dot(sub(p,center),v),dot(sub(p,center),u)));result.append(ring)
 return result
def lithic(w,h,d,seed,stair=False):
 """Large open cleavage planes, rather than all-over noise or a box bevel."""
 rng=random.Random(seed);f=box(w,h,d);front=d/2
 # A coherent oblique break occupies roughly half the front face. The
 # angle/width varies with block size, with a second unequal edge fracture.
 depth=(.002 if stair else min(.022,d*.08,h*.08))*rng.uniform(.88,1.04)
 side=1 if seed%2 else -1
 ax=side*depth/(w*.62);ay=depth/(h*.52)*(1 if seed%3 else -1)
 threshold=front+abs(ax)*w*.08+abs(ay)*h*.04
 f=clip(f,(ax,ay,1),threshold)
 # Broad broken bedding plane opens at the opposite side, never forms an
 # inset island/rim repeated on every face. Keep full stair support coverage.
 ax2=-side*depth/(w*.54);ay2=-ay*.62
 f=clip(f,(ax2,ay2,1),front+abs(ax2)*w*.24+abs(ay2)*h*.13)
 # Walking tops have a coherent tiny unequal plane, not per-triangle noise.
 tilt=.0035 if stair else min(.032,h*.05)
 f=clip(f,(side*tilt/(w*.8),1,tilt/(d*.85)),h/2+tilt*.05)
 # Local exposed nose/corner losses; no bevel around the whole body.
 if not stair or seed%3==1:
  dx=min(w*.22,.21 if stair else .32);dy=.032 if stair else min(h*.24,.15);dz=.039 if stair else min(d*.20,.16)
  n=(side/dx,1/dy,1/dz);limit=w/(2*dx)+h/(2*dy)+d/(2*dz)-1
  f=clip(f,n,limit)
 if not stair:
  # The visible left side also has a substantial lithic plane.
  dep=min(w*.14,.085);n=(-1,dep/h,dep/d);f=clip(f,n,w/2+dep*.08)
 return f
def mesh(name):return {'id':name,'name':name,'positions':[],'normals':[],'uv':[],'colors':[],'indices':[],'parts':[]}
def add_body(dst,faces,center=(0,0,0),tone=1,transform=None,name='',normalized=None):
 start=len(dst['indices']);vstart=len(dst['positions'])//3
 size=max(max(p[j] for f in faces for p in f)-min(p[j] for f in faces for p in f) for j in range(3))
 bounds=[(min(p[j] for f in faces for p in f),max(p[j] for f in faces for p in f)) for j in range(3)]
 width=bounds[0][1]-bounds[0][0];height=bounds[1][1]-bounds[1][0];depth=bounds[2][1]-bounds[2][0]
 is_stair=name.startswith('Lithic stair');is_hero=name.startswith('Lower visible')
 body_seed=int.from_bytes(hashlib.sha256(name.encode()).digest()[:8],'little')
 layer_rng=random.Random(body_seed)
 band=layer_rng.uniform(.076,.106) if is_stair else min(height*.48,layer_rng.uniform(.092,.115))
 amplitude=min(.029 if is_stair else .043,band*.43)
 line_center=layer_rng.uniform(-.17,.18)*height
 line_slope=layer_rng.uniform(-.24,.24)*height/width
 inner=(.19 if is_hero else .27)*width;outer=(.29 if is_hero else .49)*width
 def layer_line(x):return line_center+line_slope*x
 def warped(p):
  # A continuous positive-Jacobian depth compression creates an exposed
  # central bedding fracture. The rear stays fixed; no support box is exposed.
  window=max(0,min(1,(outer-abs(p[0]))/(outer-inner)))
  ramp=max(0,min(1,(p[1]-layer_line(p[0]))/band+.5))
  loss=amplitude*window*ramp
  return (p[0],p[1],bounds[2][0]+(p[2]-bounds[2][0])*(1-loss/depth))
 divisions=4
 for fi,poly in enumerate(faces):
  fn=unit(cross(sub(poly[1],poly[0]),sub(poly[2],poly[0])))
  tangent=unit(sub(poly[1],poly[0]));bitangent=cross(fn,tangent)
  ctr=tuple(sum(p[j] for p in poly)/len(poly) for j in range(3));radius=math.sqrt(max(dot(sub(p,ctr),sub(p,ctr)) for p in poly))
  rng=random.Random(body_seed+fi*179)
  pits=[(rng.uniform(-.35,.35)*radius,rng.uniform(-.28,.28)*radius,rng.uniform(.04,.09),rng.uniform(.006,.013)) for _ in range(3)]
  # Sparse coherent mineral losses are geometric depressions. They fade at
  # original polygon boundaries and share a continuous field across every
  # tessellation triangle; normals are averaged within that same fracture plane.
  def sculpt(p):
   if fn[1]>.85:return warped(p)
   edge=min(abs(dot(cross(sub(b,a),sub(p,a)),fn))/math.sqrt(dot(sub(b,a),sub(b,a))) for a,b in zip(poly,poly[1:]+poly[:1]))
   fade=min(1,edge/.025);u=dot(sub(p,ctr),tangent);v=dot(sub(p,ctr),bitangent);loss=0
   for pu,pv,r,depth in pits:
    rr=((u-pu)/r)**2+((v-pv)/(r*.65))**2
    if rr<1:loss+=depth*(1-rr)**2*(.22 if is_stair else .65)
   return warped(tuple(p[j]-fn[j]*loss*fade*fade*(3-2*fade) for j in range(3)))
  pieces=[];normal_sum=collections.defaultdict(lambda:[0.,0.,0.])
  boundary=[tuple(a[k]+(b[k]-a[k])*i/divisions for k in range(3)) for a,b in zip(poly,poly[1:]+poly[:1]) for i in range(divisions)]
  triangles=[[ctr,a,b] for a,b in zip(boundary,boundary[1:]+boundary[:1])]
  samples=[]
  if fn[2]>.65:
   for fraction in (-.47,-.29,-.19,0,.19,.29,.47):
    x=fraction*width
    for offset in (-.65,-.50,0,.50,.65):
     y=layer_line(x)+band*offset;z=(dot(fn,poly[0])-fn[0]*x-fn[1]*y)/fn[2]
     samples.append((x,y,z))
  for pu,pv,r,dep in pits:
   for scale in (0,.55,1.15):
    for k in range(1 if scale==0 else 7):
     angle=k*2*math.pi/7+.17;u=pu+r*scale*math.cos(angle);v=pv+r*.65*scale*math.sin(angle)
     samples.append(tuple(ctr[k]+tangent[k]*u+bitangent[k]*v for k in range(3)))
  for point in samples:
   for ti,(a,b,c) in enumerate(triangles):
    ab=sub(b,a);ac=sub(c,a);ap=sub(point,a);den=dot(cross(ab,ac),fn)
    if abs(den)<1e-12:continue
    v=dot(cross(ap,ac),fn)/den;w=dot(cross(ab,ap),fn)/den;u=1-v-w
    if min(u,v,w)>1e-6:
     triangles[ti:ti+1]=[[a,b,point],[b,c,point],[c,a,point]];break
  for rawtri in triangles:
   tri=[sculpt(p) for p in rawtri]
   pts=[tuple(p[k]+center[k] for k in range(3)) for p in tri]
   if transform:pts=[transform(p) for p in pts]
   cr=cross(sub(pts[1],pts[0]),sub(pts[2],pts[0]))
   if dot(cr,cr)<1e-18:continue
   pieces.append(pts)
   for p in pts:
    key=tuple(round(x,9) for x in p)
    for k in range(3):normal_sum[key][k]+=cr[k]
  for tri in pieces:
   cr=cross(sub(tri[1],tri[0]),sub(tri[2],tri[0]))
   if dot(cr,cr)<1e-18:continue
   normal=unit(cr);axis=max(range(3),key=lambda j:abs(normal[j]))
   for p in tri:
    smooth=unit(normal_sum[tuple(round(x,9) for x in p)])
    if dot(smooth,normal)<.25:smooth=normal
    q=p
    if normalized:q=tuple(p[j]/normalized[j] for j in range(3))
    nn=unit(tuple(smooth[j]*normalized[j] for j in range(3))) if normalized else smooth
    if normalized:
     flat=unit(tuple(normal[j]*normalized[j] for j in range(3)))
     if dot(nn,flat)<.25:nn=flat
    idx=len(dst['positions'])//3;dst['positions'].extend(q);dst['normals'].extend(nn)
    dst['uv'].extend([(p[2],p[1]),(p[0],p[2]),(p[0],p[1])][axis]);dst['colors'].extend((tone,tone,tone,1));dst['indices'].append(idx)
 dst['parts'].append({'name':name,'index_start':start,'index_count':len(dst['indices'])-start,'vertex_start':vstart,'vertex_count':len(dst['positions'])//3-vstart})
def copy_triangles(dst,src,triangles,name):
 start=len(dst['indices']);vstart=len(dst['positions'])//3;remap={}
 for t in triangles:
  for old in src['indices'][t:t+3]:
   if old not in remap:
    remap[old]=len(dst['positions'])//3
    for field,width in [('positions',3),('normals',3),('uv',2),('colors',4)]:dst[field].extend(src[field][old*width:(old+1)*width])
   dst['indices'].append(remap[old])
 dst['parts'].append({'name':name,'index_start':start,'index_count':len(dst['indices'])-start,'vertex_start':vstart,'vertex_count':len(dst['positions'])//3-vstart,'preserved':True})
def record(n,ix,i,kind):return {'nodeId':n['id'],'geometry':n['geometry'],'materialId':n['materials'][0],'instanceIndex':ix,'kind':kind,**i}

def main():
 bridge=read(BRIDGE);old=read(SRC/'MasonryV13/stairs-v13-mesh.json');groups=collections.defaultdict(list)
 for t in range(0,len(old['indices']),3):groups[old['colors'][old['indices'][t]*4]].append(t)
 assert len(groups)==90
 out=mesh('stairs-v16-mesh');preserved=[];replaced=[]
 for tone,triangles in groups.items():
  ids={v for t in triangles for v in old['indices'][t:t+3]};top=max(old['positions'][v*3+1] for v in ids);row=round((top-.042)/.29)-1
  assert row in range(10),(row,top)
  if row%2:
   copy_triangles(out,old,triangles,f'Preserved V13 row {row} tone {tone}');preserved.append({'row':row,'tone':tone,'indices':triangles})
  else:replaced.append({'row':row,'tone':tone})
 bounds=read(SRC/'MasonryV11/export-validation.json')['rows'];rows=[]
 for row in (0,2,4,6,8):
  low,high=bounds[row]['boundaries_x'][0],bounds[row]['boundaries_x'][-1];rng=random.Random(16100+row)
  # Existing adjacent-row centers guide purposeful running-bond joints.
  near=bounds[row+1]['boundaries_x'];count=9;nom=(high-low)/count
  cuts=[low]+[near[j]+nom*(.20 if row%4==0 else -.22)+rng.uniform(-.025,.025) for j in range(1,count)]+[high]
  # Two unequal header/stretcher substitutions alter one bay per course.
  if row in (0,4,8):del cuts[3];cuts.insert(5,(cuts[4]+cuts[5])*.5)
  assert all(b>a for a,b in zip(cuts,cuts[1:])),cuts
  rowinfo={'row':row,'boundaries':cuts,'stones':[]}
  for j,(a,b) in enumerate(zip(cuts,cuts[1:])):
   gap=.025+.014*((j*3+row)%4)/3;lo=a+(gap/2 if j else 0);hi=b-(gap/2 if j<8 else 0)
   h=.322;top=(row+1)*.29+.042;front=-1.75-row*.49+.291;depth=.525
   # Face recession cannot reveal the preserved support at z=front-.041.
   f=lithic(hi-lo,h,depth,16000+row*19+j,True)
   center=((lo+hi)/2,top-h/2,front-depth/2)
   add_body(out,f,center,.92+rng.random()*.09,name=f'Lithic stair {row:02}-{j:02}')
   rowinfo['stones'].append({'lo':lo,'hi':hi,'nominal_top':top,'front':front,'support_front':front-.041,'gap':gap})
  rows.append(rowinfo)
 hashes={'stairs':save('stairs-v16-mesh.json',out)}
 save('stair-preservation.json',{'source_sha256':hashlib.sha256((SRC/'MasonryV13/stairs-v13-mesh.json').read_bytes()).hexdigest(),'preserved':preserved,'replaced':replaced,'rows':rows})
 # Four lower flame-pier blocks, two low portal blocks, and two cheek caps.
 chosen={('592370d4',473),('b8fdddbd',473),('b8fdddbd',479),('b8fdddbd',480),('592370d4',411),('592370d4',450)}
 heroes=[];candidates=[]
 for n in bridge['nodes']:
  if n.get('distant') or not n.get('instances'):continue
  selected=[i for i in n['instances'] if -10<=i['position'][0]<=10 and -13<=i['position'][2]<=22 and -3<=i['position'][1]<=15]
  for ix,i in enumerate(n['instances']):
   p,s=i['position'],i['scale']
   if (n['id'][:8],ix) in chosen:heroes.append((n,ix,i))
   if n['materials'][0]=='f07c4b31-f38a-44bb-bd4f-1a92d5329f38' and abs(s[0]-.86)<.01 and abs(s[1]-.18)<.01 and -4.6<p[2]<-2.0:candidates.append((n,ix,i))
 for side in [-1,1]:
  pool=[r for r in candidates if (r[2]['position'][0]-2.8)*side>0]
  heroes.append(min(pool,key=lambda r:abs(r[2]['position'][2]+3.22)))
 overrides=[]
 for k,(n,ix,i) in enumerate(heroes):
  s=i['scale'];new=mesh(f'hero-v16-{k}');f=lithic(*s,161600+k)
  add_body(new,f,normalized=s,name=f'Lower visible hero {k}')
  filename=f'hero-v16-{k}.json';hashes[filename]=save(filename,new);r=record(n,ix,i,'hero');r['replacement']=filename
  selected=[a for a in n['instances'] if -10<=a['position'][0]<=10 and -13<=a['position'][2]<=22 and -3<=a['position'][1]<=15]
  j=next(j for j,a in enumerate(selected) if a is i);r['sourceVariant']=(j+(j//100)*7)%6;overrides.append(r)
 assert len(overrides)==8 and len({(r['nodeId'],r['instanceIndex']) for r in overrides})==8
 save('hero-overrides.json',{'bridge_sha256':hashlib.sha256(BRIDGE.read_bytes()).hexdigest(),'overrides':overrides})
 removed=[]
 for n in bridge['nodes']:
  if n.get('distant') or not n.get('instances'):continue
  for ix,i in enumerate(n['instances']):
   p,s=i['position'],i['scale']
   if abs(p[0]-9.47)<.005 and -3.36<p[2]<4.26 and -3.3<p[1]<0 and abs(s[0]-.5)<.01 and abs(s[1]-.43)<.01 and abs(s[2]-.91)<.01:removed.append(record(n,ix,i,'facade_skin'))
 assert len(removed)==63,len(removed)
 zlo=min(r['position'][2]-r['scale'][2]/2 for r in removed);zhi=max(r['position'][2]+r['scale'][2]/2 for r in removed)
 ymin=min(r['position'][1]-r['scale'][1]/2 for r in removed);ymax=max(r['position'][1]+r['scale'][1]/2 for r in removed)
 face=mesh('facade-v16-mesh');rng=random.Random(16163);bays=7;width=(zhi-zlo)/bays
 # Seven nonaligned masonry bands, with selected true double-height headers.
 ycuts=[ymin]+[ymin+(ymax-ymin)*v for v in (.141,.286,.429,.574,.712,.858)]+[ymax]
 headers=[{'rows':(1,2),'lo':zlo+2.25*width,'hi':zlo+3.08*width},{'rows':(4,5),'lo':zlo+4.72*width,'hi':zlo+5.56*width}]
 for row in range(7):
  cuts=[zlo]+[zlo+j*width+(.22 if row%2 else -.19)*width+rng.uniform(-.075,.075) for j in range(1,bays)]+[zhi]
  header=next((r for r in headers if row in r['rows']),None)
  if header:
   cuts=[v for v in cuts if v in (zlo,zhi) or (v<header['lo']-.20 or v>header['hi']+.20)]+[header['lo'],header['hi']];cuts.sort()
  for j,(za,zb) in enumerate(zip(cuts,cuts[1:])):
   ya,yb=ycuts[row],ycuts[row+1];gap=.019+rng.random()*.019
   if header and abs(za-header['lo'])<1e-8 and abs(zb-header['hi'])<1e-8:
    if row==header['rows'][1]:continue
    yb=ycuts[row+2]
   w=zb-za-gap;h=yb-ya-.018;d=.56
   # Native -X face: local front +Z rotated -90 degrees about Y.
   f=lithic(w,h,d,16300+row*19+j);cx=-9.48-rng.uniform(.025,.040)
   def tf(p,cx=cx,cy=(ya+yb)/2,cz=(za+zb)/2):return (cx-p[2],cy+p[1],cz+p[0])
   add_body(face,f,transform=tf,tone=.91+rng.random()*.12,name=f'Running bond {row}-{j}')
 hashes['facade']=save('facade-v16-mesh.json',face)
 save('facade-removal-manifest.json',{'bridge_sha256':hashlib.sha256(BRIDGE.read_bytes()).hexdigest(),'instances':removed,'retained':'All structural foundation cores and all original skins outside these 63 exact instances','old_bounds':[[-9.72,ymin,zlo],[-9.22,ymax,zhi]],'new_outward_allowance_m':.08})
 save('source-build.json',{'hashes':hashes,'preserved_stair_bodies':len(preserved),'replaced_stair_bodies':len(replaced),'new_stair_bodies':45,'hero_count':8,'facade_removed':len(removed),'facade_new_bodies':len(face['parts']),'double_height_headers':headers,'notes':['Source-only; final visual QA pending.','Global composition, untouched stairs and internal foundation remain.']})
 print('MASONRY_V16_SOURCE_COMPLETE',hashes)
if __name__=='__main__':main()
