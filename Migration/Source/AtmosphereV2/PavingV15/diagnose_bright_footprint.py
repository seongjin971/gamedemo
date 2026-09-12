"""Actual flame-shader footprint versus source floor. System Python + Pillow.
No Unity, Blender, or original-source modifications. Base mip at t=2.3.
"""
import json, math, re, hashlib, bisect, struct
from pathlib import Path
from PIL import Image
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[3]
MESH=OUT.parent/'PavingV14/paving-v14-mesh.json'
META=OUT.parent/'PavingV14/hybrid-metadata.json'
SCENE=ROOT/'Unity/Vesper/Assets/Vesper/Scenes/VesperAtmosphereV2.unity'
FLAME=ROOT/'Unity/Vesper/Assets/Vesper/Textures/flame-v1.png'
MASK=ROOT/'Unity/Vesper/Assets/Vesper/AtmosphereV2/Textures/courtyard-wet-mask.png'
MATERIAL=ROOT/'Unity/Vesper/Assets/Vesper/AtmosphereV2/Materials/31e82bcf-916c-434c-ba3e-39d42111d21e.mat'
QUAD=ROOT/'Unity/Vesper/Assets/Vesper/Generated/Meshes/358ec67e-4682-424f-b50b-39b570140d99.asset'
SHADER=ROOT/'Unity/Vesper/Assets/Vesper/Shaders/AtmosphereFlame.shader'
H=-.004; HR=-.005

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def smooth(a,b,x):
 t=max(0,min(1,(x-a)/(b-a)));return t*t*(3-2*t)
def linear(x):return x/12.92 if x<=.04045 else ((x+.055)/1.055)**2.4
class Sampler:
 def __init__(self,path,srgb=False):
  self.image=Image.open(path).convert('RGBA');self.w,self.h=self.image.size;self.p=self.image.load();self.srgb=srgb
 def sample(self,u,v):
  x=u*self.w-.5;y=(1-v)*self.h-.5;ix=math.floor(x);iy=math.floor(y);tx=x-ix;ty=y-iy;r=[0.]*4
  for dx,wx in [(0,1-tx),(1,tx)]:
   for dy,wy in [(0,1-ty),(1,ty)]:
    p=self.p[max(0,min(self.w-1,ix+dx)),max(0,min(self.h-1,iy+dy))]
    for k in range(4):r[k]+=(linear(p[k]/255) if self.srgb and k<3 else p[k]/255)*wx*wy
  return r

class Floor:
 def __init__(self,path):
  g=json.loads(path.read_text());p=g['positions'];ids=g['indices'];self.g=g;self.triangles=[];self.cells={}
  for k in range(0,len(ids),3):
   a,b,c=[p[3*ids[k+j]:3*ids[k+j]+3] for j in range(3)]
   d=(b[2]-c[2])*(a[0]-c[0])+(c[0]-b[0])*(a[2]-c[2])
   n=len(self.triangles);self.triangles.append((a,b,c,d,k//3))
   for x in range(math.floor(min(a[0],b[0],c[0])*2),math.floor(max(a[0],b[0],c[0])*2)+1):
    for z in range(math.floor(min(a[2],b[2],c[2])*2),math.floor(max(a[2],b[2],c[2])*2)+1):self.cells.setdefault((x,z),[]).append(n)
 def top(self,x,z):
  top=-1e9;index=None
  for n in self.cells.get((math.floor(x*2),math.floor(z*2)),[]):
   a,b,c,d,k=self.triangles[n]
   if abs(d)<1e-12:continue
   u=((b[2]-c[2])*(x-c[0])+(c[0]-b[0])*(z-c[2]))/d;v=((c[2]-a[2])*(x-c[0])+(a[0]-c[0])*(z-c[2]))/d;w=1-u-v
   if min(u,v,w)>=-1e-8:
    y=u*a[1]+v*b[1]+w*c[1]
    if y>top:top,index=y,k
  return top,index
 def ray_occluded(self,w,to_camera):
  # Floor max Y=.01042; scan from water toward camera for up to .05m height.
  # Exact double-sided Moller-Trumbore intersection, including vertical walls.
  origin=[w[k]+to_camera[k]*.08 for k in range(3)];direction=[-x for x in to_camera]
  end=[w[k]+to_camera[k]*.000001 for k in range(3)]
  candidates=set()
  for x in range(math.floor(min(origin[0],end[0])*2),math.floor(max(origin[0],end[0])*2)+1):
   for z in range(math.floor(min(origin[2],end[2])*2),math.floor(max(origin[2],end[2])*2)+1):candidates.update(self.cells.get((x,z),[]))
  best=.08;hit=None
  for n in candidates:
   a,b,c,d,k=self.triangles[n]
   e1=[b[j]-a[j] for j in range(3)];e2=[c[j]-a[j] for j in range(3)]
   pv=cross(direction,e2);det=dot(e1,pv)
   if abs(det)<1e-12:continue
   tv=[origin[j]-a[j] for j in range(3)];u=dot(tv,pv)/det
   if u<0 or u>1:continue
   q=cross(tv,e1);v=dot(direction,q)/det
   if v<0 or u+v>1:continue
   t=dot(e2,q)/det
   if 0<=t<best:best=t;hit=k
  return hit

def dot(a,b):return sum(x*y for x,y in zip(a,b))
def cross(a,b):return [a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]]

def main(mesh=MESH,suffix='before-v14',resolution=128):
 flame=Sampler(FLAME,True);mask=Sampler(MASK);floor=Floor(mesh);meta=json.loads(META.read_text());parts=meta['parts'];starts=[p['index_start']//3 for p in parts]
 base_color=[float(x) for x in re.search(r'_BaseColor: \{r: ([^,]+), g: ([^,]+), b: ([^,]+), a: ([^}]+)',MATERIAL.read_text()).groups()]
 quad_bytes=bytes.fromhex(re.search(r'_typelessdata: (\w+)',QUAD.read_text()).group(1));assert len(quad_bytes)==192
 quad=[struct.unpack('<12f',quad_bytes[i*48:(i+1)*48]) for i in range(4)]
 assert all(abs(q[0]-(.5-q[10]))<1e-7 and abs(q[1]-(q[11]-.5))<1e-7 for q in quad)
 scene=SCENE.read_text();emitters=[]
 for name,ident in [('left',337797818),('right',1599689651)]:
  block=re.search(r'^--- !u!4 &'+str(ident)+r'\n(.*?)(?=^---)',scene,re.M|re.S).group(1);assert 'm_Father: {fileID: 0}' in block
  values=lambda key:[float(v) for v in re.search(key+r': \{x: ([^,]+), y: ([^,]+), z: ([^}]+)',block).groups()]
  emitters.append((name,values('m_LocalPosition'),values('m_LocalScale')))
 texels=[]
 for j in range(resolution):
  for i in range(resolution):
   u,v=(i+.5)/resolution,(j+.5)/resolution
   wu=u+math.sin(v*11-2.3*4)*.012*v;wv=v+math.sin(2.3*3+wu*9)*.012*v
   rgba=flame.sample(max(0,min(1,wu)),max(0,min(1,wv)));density=max(rgba[:3]);core=smooth(.18,.65,rgba[1])*smooth(.5,.95,rgba[0])
   color=[1,.32+core*.5,.075+core*.445];radiance=[color[k]*density**1.6*base_color[k]*rgba[3]*base_color[3]*(.25+core*.75)*(1+core*4) for k in range(3)]
   lum=dot(radiance,[.2126,.7152,.0722])
   if lum>.02:texels.append((i,j,u,v,lum,core))
 reports=[];samples_out=[]
 for view,a,e in [('full',.46,.72),('orbit',.70,.85)]:
  d=[math.sin(a)*math.cos(e),-math.sin(e),-math.cos(a)*math.cos(e)];to_camera=[-q for q in d]
  # Reflection camera inverse view = mirrorY * source camera inverse view.
  # Shader billboard right/up are from that matrix, not transform.rotation.
  # Unity transform right = cross(worldUp, forward), not the OpenGL
  # cross(forward, worldUp). The imported quad's X reversal is independent.
  right=[-math.cos(a),0,-math.sin(a)];up=[math.sin(a)*math.sin(e),-math.cos(e),-math.cos(a)*math.sin(e)]
  for label,center,scale in emitters:
   stats={'view':view,'emitter':label,'luminance_sum':0.,'core_luminance_sum':0.,'core_occluded_luminance':0.,'occluded_luminance':0.,'mask_lost_luminance':0.,'visible_luminance':0.,'core_visible_luminance':0.,'occluding_bodies':{},'water_bounds_xz':[[1e9,1e9],[-1e9,-1e9]]}
   preview=Image.new('RGB',(resolution,resolution));pix=preview.load()
   for i,j,u,v,lum,core in texels:
    # Actual imported quad X=.5-u, Y=v-.5, parsed from its serialized mesh.
    physical=[center[k]+right[k]*(.5-u)*scale[0]+up[k]*(v-.5)*scale[1] for k in range(3)]
    virtual=[physical[0],2*HR-physical[1],physical[2]];t=(H-virtual[1])/d[1];w=[virtual[k]+d[k]*t for k in range(3)]
    mu,mv=(-w[0]+7.8)/18,1-(w[2]+8)/26;coverage=smooth(.36,.63,max(mask.sample(mu+du,mv)[0] for du in [0,.018,-.018]))
    fy,tri=floor.top(w[0],w[2]);hit=floor.ray_occluded(w,to_camera);occluded=hit is not None
    stats['luminance_sum']+=lum;stats['core_luminance_sum']+=lum if core>=.5 else 0
    stats['occluded_luminance']+=lum*occluded;stats['core_occluded_luminance']+=lum*(core>=.5)*occluded
    stats['mask_lost_luminance']+=lum*(1-coverage);stats['visible_luminance']+=lum*coverage*(not occluded);stats['core_visible_luminance']+=lum*(core>=.5)*coverage*(not occluded)
    if occluded:
     body=parts[bisect.bisect_right(starts,hit)-1]['name'];stats['occluding_bodies'][body]=stats['occluding_bodies'].get(body,0)+lum
    for k,axis in enumerate([0,2]):stats['water_bounds_xz'][0][k]=min(stats['water_bounds_xz'][0][k],w[axis]);stats['water_bounds_xz'][1][k]=max(stats['water_bounds_xz'][1][k],w[axis])
    intensity=min(255,round(40+lum*45));pix[i,resolution-1-j]=(intensity,20,20) if occluded else ((20,20,intensity) if coverage<.5 else (20,intensity,20))
    samples_out.append(dict(view=view,emitter=label,uv=[u,v],world=w,luminance=lum,core=core,coverage=coverage,floor_y=fy,ray_occluded=occluded,triangle=hit))
   total=stats['luminance_sum'];ct=stats['core_luminance_sum']
   for key in ['occluded_luminance','mask_lost_luminance','visible_luminance']:stats[key+'_fraction']=stats[key]/total
   stats['core_occluded_fraction']=stats['core_occluded_luminance']/ct;stats['core_visible_fraction']=stats['core_visible_luminance']/ct
   stats['occluding_bodies']=dict(sorted(stats['occluding_bodies'].items(),key=lambda pair:-pair[1]))
   preview.resize((512,512),Image.Resampling.NEAREST).save(OUT/f'{suffix}-{view}-{label}-occlusion.png');reports.append(stats)
 report=dict(mesh_sha256=sha(mesh),source_hashes={str(p.relative_to(ROOT)):sha(p) for p in [FLAME,MASK,SCENE,META,MATERIAL,QUAD,SHADER]},material_base_color=base_color,quad_position_uv_verified=True,resolution=resolution,sample_count=len(texels),time_seconds=2.3,core_definition='shader core >= .5',radiance_threshold=.02,views=reports,
 limitations=['Actual source RGBA, sRGB-before-bilinear, sequential t=2.3 warp and shader radiance formula; base mip only.', 'Exact camera-ray triangle intersection with source paving within 8cm toward camera; excludes other scene geometry.', 'View matrix billboard model mirrors source camera right/up, including actual quad X=.5-u.', 'Weights are emitted luminance, not tone-mapped screen pixels; no reflection RT bilinear/mips or bloom.'])
 (OUT/f'{suffix}-footprint-report.json').write_text(json.dumps(report,indent=2));(OUT/f'{suffix}-footprint-samples.json').write_text(json.dumps(samples_out,separators=(',',':')))
 print(json.dumps(reports,indent=2))

if __name__=='__main__':main()
