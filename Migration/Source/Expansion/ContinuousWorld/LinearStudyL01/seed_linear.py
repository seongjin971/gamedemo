"""Add an isolated linear-world implementation. Never overwrite the original world."""
from pathlib import Path
import re, json, hashlib, shutil
ROOT = Path(__file__).resolve().parents[5]
OLD = ROOT/'Unity/Vesper/Assets/Vesper/Expansion/ContinuousWorld'
NEW = ROOT/'Unity/Vesper/Assets/Vesper/Expansion/LinearWorld'
if NEW.exists(): raise RuntimeError('LinearWorld already exists; seed is one-shot')
def put(relative, content):
    p=NEW/relative;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(content,encoding='utf-8')
def adapt(s):
    return s.replace('namespace Vesper.Expansion.ContinuousWorld','namespace Vesper.Expansion.LinearWorld').replace('WorldBuild','LinearBuild').replace('"-world','"-linear')
for name in ['WorldMotor','WorldAnimation','WorldRunInput','WorldCamera','WorldEnvironment','WorldWeather','WorldRoofCutaway']:
    s=adapt((OLD/'Runtime'/f'{name}.cs').read_text(encoding='utf-8'))
    if name=='WorldCamera': s=s.replace('= .46f','= .59f').replace('= .72f','= .88f').replace('14.1f / 1.27f','8.8f')
    if name=='WorldEnvironment':
        s=s.replace('Progress<103','Progress<65').replace('Progress>135&&Progress<225','Progress>110&&Progress<185')
        s=s.replace('1.65f*a+.85f*b+1.05f*c','1.65f*a+.72f*b+1.1f*c')
    put('Runtime/'+name+'.cs',s)
# Clone the existing authored model/material loader, but all existing assets are read-only.
s=adapt((OLD/'Editor/WorldVisuals.cs').read_text(encoding='utf-8'))
s=s[:s.index(' static void Grounded')]+ '\n}\n}\n'
s=s.replace('const string Art=LinearBuild.Root+"/Art"','const string Art="Assets/Vesper/Expansion/ContinuousWorld/Art"')
a=s.index(' public static Texture2D Texture(');b=s.index(' static Material Mat(',a)
s=s[:a]+''' public static Texture2D Texture(string path,bool normal=false,bool linear=false,TextureWrapMode wrap=TextureWrapMode.Repeat){return AssetDatabase.LoadAssetAtPath<Texture2D>(path);}
'''+s[b:]
s=s.replace('var importer=AssetImporter.GetAtPath(path) as TextureImporter;if(importer&&!importer.alphaIsTransparency){importer.alphaIsTransparency=true;importer.SaveAndReimport();}','')
s=s.replace('var asset=AssetDatabase.LoadAssetAtPath<GameObject>(path);','if(file.StartsWith("VisualF/"))path=LinearBuild.Root+"/Art/EnvironmentKit/"+file+".fbx";var asset=AssetDatabase.LoadAssetAtPath<GameObject>(path);')
s=s.replace('Debug.LogWarning("Missing optional model "+path);return null;','throw new Exception("Missing required model "+path);')
put('Editor/WorldVisuals.cs',s)
# Reuse weather creation and torch helpers; no previous ruin arrangement or puddle placement.
s=adapt((OLD/'Editor/WorldRuins.cs').read_text(encoding='utf-8'))
s='using System.Collections.Generic;\nusing UnityEngine;\nusing UnityEngine.Rendering;\nusing UnityEditor;\nnamespace Vesper.Expansion.LinearWorld.Editor {\npublic static partial class WorldVisuals {\n'+s[s.index(' static ParticleSystem Precipitation'):]
s=s.replace('"Vesper/WorldPrecipitation"','"Vesper/Linear/Precipitation"').replace('Center(48.5f),0,-48.5f','Center(25),0,-25')
put('Editor/WorldWeatherSetup.cs',s)
for name,shader in [('VisualFGround','Ground'),('VisualFRiver','River'),('VisualFWetStone','WetStone'),('WorldPrecipitation','Precipitation')]:
    s=(OLD/f'{name}.shader').read_text(encoding='utf-8')
    s=re.sub(r'Shader "[^"]+"',f'Shader "Vesper/Linear/{shader}"',s,count=1)
    if shader=='Precipitation':s=s.replace('smoothstep(95,145,d)','smoothstep(55,120,d)').replace('smoothstep(242,292,d)','smoothstep(190,255,d)')
    put(shader+'.shader',s)
# F02's unpublished Blender files are copied into a new asset directory; its source stays untouched.
src=ROOT/'Migration/Source/Expansion/ContinuousWorld/VisualF'
dst=NEW/'Art/EnvironmentKit/VisualF';dst.mkdir(parents=True)
for folder in ['FirVolume','DetailAssets']:
    for p in (src/folder).glob('*.fbx'):shutil.copyfile(p,dst/p.name)
shutil.copyfile(src/'LimestoneFineF.png',dst/'LimestoneFineF.png')
# Build utilities and player conversion are reused in the isolated namespace only.
s=adapt((OLD/'Editor/WorldBuild.cs').read_text(encoding='utf-8'))
s=s.replace('Assets/Vesper/Expansion/ContinuousWorld','Assets/Vesper/Expansion/LinearWorld')
s=s.replace('public static class LinearBuild','public static partial class LinearBuild')
a=s.index(' public static string ScenePath');b=s.index(' static string generated',a)
s=s[:a]+' public static string ScenePath=>"Assets/Vesper/Scenes/Expansion/VesperLinearWorld_"+revision+".unity";\n'+s[b:]
s=s.replace('../../Migration/Evidence/Expansion/ContinuousWorld/','../../Migration/Evidence/Expansion/LinearWorld/')
s=s.replace('Builds/VesperContinuousWorld_','Builds/VesperLinearWorld_').replace('/VesperWorld.exe','/VesperLinear.exe')
a=s.index(' static void Terrain(');b=s.index(' static WorldEnvironment Lighting',a)
s=s[:a]+s[b:]
s=s.replace('revision=Arg("-linearRevision","A01");generated=Root+"/Generated/"+revision;Directory.CreateDirectory(generated);','revision=Arg("-linearRevision","L01");generated=Root+"/Generated/"+revision;if(Directory.Exists(generated)||File.Exists(ScenePath))throw new Exception("Refuse to overwrite existing candidate "+revision);Directory.CreateDirectory(generated);')
s=s.replace('control.homeSize=11.1f','control.homeSize=8.8f').replace('camera.orthographicSize=11.1f','camera.orthographicSize=8.8f')
a=s.index('  earth=Material(');b=s.index('  var edgeDiagnostics=',a)
s=s[:a]+'''  earth=Material("Earth",Color.white);stone=Material("PathStone",new Color(.55f,.55f,.50f));
  var terrain=new GameObject("Linear terrain and collision");Terrain(terrain.transform);Bridge(terrain.transform);
  var world=Lighting(player,camera);WorldVisuals.Compose(terrain,world,generated);Bake(terrain);Physics.SyncTransforms();
'''+s[b:]
a=s.index('  var edgeDiagnostics=');b=s.index('  var results=',a)
s=s[:a]+s[b:]
s=s.replace('revision=Arg("-linearRevision","A01")','revision=Arg("-linearRevision","L01")')
s=s.replace('options=BuildOptions.StrictMode','options=BuildOptions.StrictMode')
put('Editor/LinearBuild.cs',s)
# Lock new references without replacing any older target image.
targets=ROOT/'.dream-loop/linear-world/targets';targets.mkdir(parents=True,exist_ok=False)
delivery=json.loads((Path(__file__).parent/'final-delivery.json').read_text(encoding='utf-8'))
locked=[]
for item in delivery['images']:
    source=Path(__file__).parent/item['file'];dest=targets/item['file'];shutil.copyfile(source,dest)
    locked.append({'file':item['file'],'sha256':hashlib.sha256(dest.read_bytes()).hexdigest()})
(targets.parent/'targets.json').write_text(json.dumps({'status':'USER_ACCEPTED_BUILD_TARGETS','images':locked},indent=2),encoding='utf-8')
print('Created isolated LinearWorld sources and locked five approved targets.')
