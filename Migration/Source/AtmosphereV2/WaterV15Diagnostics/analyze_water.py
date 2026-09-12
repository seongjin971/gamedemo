"""Read-only source diagnostics. Python 3 + Pillow; no Unity/Blender launch.

Writes only this directory. Geometry uses exact PavingV14 source triangles.
Mask bilinear is base mip, linear R, Clamp addressing from Unity importer.
"""
import hashlib, json, math, re
from pathlib import Path
from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
SCENE = ROOT / 'Unity/Vesper/Assets/Vesper/Scenes/VesperAtmosphereV2.unity'
MESH = HERE.parent / 'PavingV14/paving-v14-mesh.json'
MASK = ROOT / 'Unity/Vesper/Assets/Vesper/AtmosphereV2/Textures/courtyard-wet-mask.png'
WATER_Y = -.004
REFLECTION_Y = -.005

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def transform(scene, ident):
    block = re.search(r'^--- !u!4 &' + str(ident) + r'\n(.*?)(?=^---|\Z)', scene, re.M | re.S).group(1)
    assert 'm_Father: {fileID: 0}' in block
    return [float(v) for v in re.search(r'm_LocalPosition: \{x: ([^,]+), y: ([^,]+), z: ([^}]+)', block).groups()]

image = Image.open(MASK).convert('RGB')
pixels = image.load()
def mask_bilinear(u, v):
    # Unity UV origin bottom-left; texel centers are (i+.5)/dimension.
    px = u * image.width - .5
    py = (1-v) * image.height - .5
    x, y = math.floor(px), math.floor(py)
    tx, ty = px-x, py-y
    value = 0.
    for ox, wx in [(0,1-tx),(1,tx)]:
        for oy, wy in [(0,1-ty),(1,ty)]:
            value += pixels[max(0,min(image.width-1,x+ox)),max(0,min(image.height-1,y+oy))][0] / 255. * wx * wy
    return value

def mask_sample(x, z):
    u,v = (-x+7.8)/18, 1-(z+8)/26
    samples = [mask_bilinear(u+d,v) for d in [0,.018,-.018]]
    t=max(0,min(1,(max(samples)-.36)/(.63-.36)))
    return dict(uv=[u,v], red_samples=samples, coverage=t*t*(3-2*t), inside_water_quad=0<=u<=1 and 0<=v<=1)

# Index projected triangles into one-meter cells. Ignore vertical walls only
# when their XZ determinant is zero; all actual overlapping cap/bed faces stay.
geo=json.loads(MESH.read_text())
coords=geo['positions']; ids=geo['indices']; triangles=[]; cells={}
for k in range(0,len(ids),3):
    a,b,c=[coords[3*ids[k+j]:3*ids[k+j]+3] for j in range(3)]
    denominator=(b[2]-c[2])*(a[0]-c[0])+(c[0]-b[0])*(a[2]-c[2])
    if abs(denominator)<1e-12: continue
    n=len(triangles); triangles.append((a,b,c,denominator,k//3))
    for ix in range(math.floor(min(a[0],b[0],c[0])),math.floor(max(a[0],b[0],c[0]))+1):
        for iz in range(math.floor(min(a[2],b[2],c[2])),math.floor(max(a[2],b[2],c[2]))+1):
            cells.setdefault((ix,iz),[]).append(n)

def top_y(x,z):
    hits=[]
    for n in cells.get((math.floor(x),math.floor(z)),[]):
        a,b,c,d,index=triangles[n]
        u=((b[2]-c[2])*(x-c[0])+(c[0]-b[0])*(z-c[2]))/d
        v=((c[2]-a[2])*(x-c[0])+(a[0]-c[0])*(z-c[2]))/d
        w=1-u-v
        if min(u,v,w)>=-1e-8:
            hits.append((u*a[1]+v*b[1]+w*c[1],index))
    if not hits: return None
    y,index=max(hits)
    return dict(y=y, triangle=index, water_minus_floor_m=WATER_Y-y, floor_above_water=y>WATER_Y)

scene=SCENE.read_text(encoding='utf-8')
emitters={'left':transform(scene,337797818),'right':transform(scene,1599689651)}
views=[]
for name,a,e,size in [('full',.46,.72,14.1/1.27),('orbit',.70,.85,14.1/1.27),('zoom',.46,.72,8.8)]:
    forward=[math.sin(a)*math.cos(e),-math.sin(e),-math.cos(a)*math.cos(e)]
    result=dict(name=name,angle_radians=a,elevation_radians=e,orthographic_size=size,
                camera_forward=forward,fresnel=.025+.975*(1-math.sin(e))**5,emitters=[])
    for label,p in emitters.items():
        virtual=[p[0],2*REFLECTION_Y-p[1],p[2]]
        distance=(WATER_Y-virtual[1])/forward[1]
        hit=[virtual[j]+distance*forward[j] for j in range(3)]
        samples=[]
        # Three small probes around center; these are NOT the whole flame sprite.
        for probe,dx,dz in [('center',0,0),('near_east',.15,0),('near_northwest',-.075,.129903810568),('near_southwest',-.075,-.129903810568)]:
            x,z=hit[0]+dx,hit[2]+dz
            samples.append(dict(name=probe,world=[x,WATER_Y,z],mask=mask_sample(x,z),floor=top_y(x,z)))
        result['emitters'].append(dict(name=label,world_center=p,virtual_center=virtual,water_hit=hit,samples=samples))
    views.append(result)

report=dict(schema_version=1,inputs={str(p.relative_to(ROOT)):sha(p) for p in [SCENE,MESH,MASK]},
            water_y=WATER_Y,reflection_plane_y=REFLECTION_Y,mask_size=list(image.size),
            formula='Pvirtual=(Px,2*hReflection-Py,Pz); t=(hWater-Pvirtual.y)/cameraForward.y; W=Pvirtual+t*cameraForward',
            views=views,limitations=[
                'Serialized flame transform centers, not brightest texels or runtime sprite displacement.',
                'Base-mip linear red bilinear samples; actual GPU derivative/mips/filter precision may differ.',
                'Vertical source-mesh top Y does not prove camera-ray visibility or account for other scene geometry.',
                'Full and zoom have identical orthographic view direction so their world intersections match.',
                'Sky radiance and actual reflected HDR values require matched native captures; PNG clips HDR values.',
                'The .001m reflection-plane/water-plane difference is retained, not silently corrected.'
            ])
(HERE/'water-hit-report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
for view in views:
    for emitter in view['emitters']:
        print(view['name'],emitter['name'],'hit',emitter['water_hit'])
        for sample in emitter['samples']:
            print(' ',sample['name'],'coverage',round(sample['mask']['coverage'],5),'floor',sample['floor'])
