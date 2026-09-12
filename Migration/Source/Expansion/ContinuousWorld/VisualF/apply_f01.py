from pathlib import Path
import shutil, hashlib, json
ROOT=Path(__file__).resolve().parents[5]
CW=ROOT/'Unity/Vesper/Assets/Vesper/Expansion/ContinuousWorld'
SNAP=Path(__file__).resolve().parent/'pre-F01-source'
SNAP.mkdir(exist_ok=True)
evidence=ROOT/'Migration/Evidence/Expansion/ContinuousWorld/VisualF'
editable=[CW/'Editor/WorldBuild.cs', CW/'Runtime/WorldLayout.cs']
with (evidence/'editable-source-before.json').open('x',encoding='utf-8') as f:
    json.dump({p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in editable},f,indent=2)
def edit(rel,replacements):
    p=CW/rel
    original=p.read_text(encoding='utf-8-sig')
    out=SNAP/rel;out.parent.mkdir(parents=True,exist_ok=True)
    if out.exists():raise RuntimeError('Source backup already exists '+str(out))
    shutil.copy2(p,out)
    for old,new in replacements:
        if original.count(old)!=1:raise RuntimeError('Expected one source anchor '+old[:100])
        original=original.replace(old,new)
    p.write_text(original,encoding='utf-8')
edit('Editor/WorldBuild.cs',[
('public const string ScenePath="Assets/Vesper/Scenes/Expansion/VesperContinuousWorld.unity";', 'public static string ScenePath=>"Assets/Vesper/Scenes/Expansion/VesperContinuousWorld"+(revision!=null&&revision.StartsWith("F")?"_"+revision:"")+".unity";'),
('WorldVisuals.SnowPass(terrain,world);Bake(terrain);','WorldVisuals.SnowPass(terrain,world);if(revision.StartsWith("F"))WorldVisuals.RecomposeVisualF(terrain,world);Bake(terrain);'),
('int cells=z0>=-96','int cells=z0<=-352?64:z0>=-96'),
('MeshObject(parent,"Continuous terrain "+x0+" "+z0,verts,tris,earth,28,true,colors.ToArray());','var chunk=MeshObject(parent,"Continuous terrain "+x0+" "+z0,verts,tris,earth,28,true,colors.ToArray());\n   var normals=verts.Select(p=>{float dx=(WorldLayout.Height(p.x+.15f,-p.z)-WorldLayout.Height(p.x-.15f,-p.z))/.3f;float dz=(WorldLayout.Height(p.x,-p.z-.15f)-WorldLayout.Height(p.x,-p.z+.15f))/.3f;return new Vector3(-dx,1,-dz).normalized;}).ToArray();chunk.GetComponent<MeshFilter>().sharedMesh.normals=normals;')])
edit('Runtime/WorldLayout.cs',[
('public static float Center(float d){for', 'public static float Center(float d){if(d>=166&&d<=198)return 18;if(d>145&&d<166)return Mathf.Lerp(0,18,Mathf.SmoothStep(0,1,Mathf.InverseLerp(145,166,d)));if(d>198&&d<210)return Mathf.Lerp(18,10,Mathf.SmoothStep(0,1,Mathf.InverseLerp(198,210,d)));for'),
('float natural=level-', 'float overlookEdge=8.7f+1.2f*Mathf.Sin(d*.18f)+.6f*Mathf.Sin(d*.47f);\n  float natural=level-'),
('Mathf.InverseLerp(383,396,d)', 'Mathf.InverseLerp(385+1.8f*Mathf.Sin(x*.28f),405+2.2f*Mathf.Sin(x*.2f),d)'),
('Mathf.InverseLerp(8,16,Center(d)-x)', 'Mathf.InverseLerp(overlookEdge,overlookEdge+12,Center(d)-x)')])
print('F01 structural source changes applied; old sources copied before editing')

# Separate shader keeps every old material reference and shader asset intact.
p=CW/'WorldGround.shader'
s=p.read_text(encoding='utf-8-sig').replace('Shader "Vesper/WorldGround"','Shader "Vesper/VisualF/Ground"')
old='half3 stone=SAMPLE_TEXTURE2D(_StoneMap,sampler_StoneMap,uv*.67).rgb;'
new='half3 weights=pow(abs(normalize(i.n)),4);weights/=max(.001,weights.x+weights.y+weights.z);half3 stone=SAMPLE_TEXTURE2D(_StoneMap,sampler_StoneMap,i.w.zy*_DetailScale*.67).rgb*weights.x+SAMPLE_TEXTURE2D(_StoneMap,sampler_StoneMap,i.w.xz*_DetailScale*.67).rgb*weights.y+SAMPLE_TEXTURE2D(_StoneMap,sampler_StoneMap,i.w.xy*_DetailScale*.67).rgb*weights.z;'
assert s.count(old)==1
s=s.replace(old,new)
(CW/'VisualFGround.shader').write_text(s,encoding='utf-8')
