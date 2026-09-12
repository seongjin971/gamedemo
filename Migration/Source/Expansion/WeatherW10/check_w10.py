from pathlib import Path
import hashlib,json,re,shutil
from PIL import Image
ROOT=Path(__file__).resolve().parents[4]
E=ROOT/'Migration/Evidence/Expansion/WeatherWorld/W10'
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
out=E/'verification.json'
assert not out.exists(),'Preserve previous evidence'
before=json.loads((E/'protected-before.json').read_text())
changed=[p for p,h in before.items() if not (ROOT/p).is_file() or sha(ROOT/p)!=h]
skills=json.loads((E/'skill-before.json').read_text())
skill_changes=[p for p,h in skills.items() if sha(Path(p))!=h]
mapping=json.loads((E/'script-map.json').read_text())
old=(ROOT/'Unity/Vesper/Assets/Vesper/Scenes/Expansion/VesperWeatherWorld_W09.unity').read_text()
new=(ROOT/'Unity/Vesper/Assets/Vesper/Scenes/Expansion/VesperWeatherWorld_W10.unity').read_text()
def guid(p):return re.search(r'^guid: (.+)$',p.read_text(),re.M)[1]
for row in mapping:
 oldguid=guid(ROOT/'Unity/Vesper'/(row['old']+'.meta'))
 newguid=guid(ROOT/'Unity/Vesper'/(row['new']+'.meta'))
 new=new.replace('guid: '+newguid,'guid: '+oldguid)
def normalize(s):
 for ns in ['WeatherWorld','WeatherW07','WeatherW08']:s=s.replace('Vesper.Expansion.'+ns,'Vesper.Expansion.WeatherW10')
 lines=[];seen=set()
 for line in s.splitlines():
  if line.startswith('using '):
   if line in seen:continue
   seen.add(line)
  lines.append(line)
 return '\n'.join(lines)+'\n'
runtime=[]
for row in mapping:
 a=normalize((ROOT/'Unity/Vesper'/row['old']).read_text(encoding='utf-8-sig'))
 b=(ROOT/'Unity/Vesper'/row['new']).read_text()
 if Path(row['old']).name=='WorldEnvironment.cs':a=a.replace('Drag to orbit','Q / E to orbit')
 runtime.append({'file':Path(row['new']).name,'sameAsideFromNamespaceAndHelp':a==b,'intendedCameraChange':Path(row['new']).name=='WorldCamera.cs'})
images={p.relative_to(E).as_posix():list(Image.open(p).size) for p in (E/'input-qa-visible').glob('*.png')}
qa=json.loads((E/'input-qa-visible/report.json').read_text())
build=json.loads((E/'build.json').read_text())
r={'protectedFiles':len(before),'protectedChanges':changed,'sharedSkillChanges':skill_changes,
   'sceneIdenticalExceptVersionedScriptGuids':old==new,'runtimeComparison':runtime,
   'rawImageSizes':images,'inputQAFailures':qa['failures'],'runtimeErrors':qa['errors'],
   'buildErrors':build['errors'],'buildWarnings':build['warnings']}
r['passed']=not(changed or skill_changes or qa['failures'] or qa['errors']) and old==new and all(x['sameAsideFromNamespaceAndHelp'] or x['intendedCameraChange'] for x in runtime) and len(images)==len(qa['captures']) and len(images)>0 and all(s==[1920,1080] for s in images.values()) and build['result']=='Succeeded' and build['errors']==0 and build['warnings']==0
out.write_text(json.dumps(r,indent=2))
shutil.copytree(ROOT/'Unity/Vesper/Assets/Vesper/Expansion/WeatherW10',E/'source/WeatherW10')
shutil.copy2(ROOT/'Unity/Vesper/Assets/Vesper/Scenes/Expansion/VesperWeatherWorld_W10.unity',E/'source/VesperWeatherWorld_W10.unity')
print(json.dumps(r,indent=2));raise SystemExit(not r['passed'])
