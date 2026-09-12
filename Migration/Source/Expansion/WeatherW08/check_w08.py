from pathlib import Path
import hashlib,json,re,sys
from PIL import Image,ImageStat
ROOT=Path(__file__).resolve().parents[4]
E=ROOT/'Migration/Evidence/Expansion/WeatherWorld/W08'
P=ROOT/'Migration/Evidence/Expansion/WeatherWorld/W07'
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()
if sys.argv[1]=='preserve':
    before=json.loads((P/'protected-before.json').read_text());candidate=[p for p in before if p.startswith('Unity/Vesper/Assets/Vesper/Expansion/WeatherW07/')]
    changes=[p for p,h in before.items() if p not in candidate and (not (ROOT/p).is_file() or sha(ROOT/p)!=h)]
    skills=json.loads((P/'skill-before.json').read_text());skill_changes=[p for p,h in skills.items() if sha(Path(p))!=h]
    r={'baseline':'W07/protected-before.json, taken at start of this task','protectedFiles':len(before)-len(candidate),'newTaskDiagnosticFilesExcluded':candidate,'changed':changes,'sharedSkillChanges':skill_changes,'passed':not(changes or skill_changes)}
    out=E/'protected-after.json'
elif sys.argv[1]=='movement':
    code=(ROOT/'Migration/Source/Expansion/WeatherW07/compare_w07.py').read_text()
    code=code.replace("E=ROOT/'Migration/Evidence/Expansion/WeatherWorld/W07'","E=ROOT/'Migration/Evidence/Expansion/WeatherWorld/W08'").replace("signature('W07')","signature('W08')").replace("'candidate':'W07'","'candidate':'W08'").replace("E/'before-source/Runtime'","ROOT/'Migration/Evidence/Expansion/WeatherWorld/W07/before-source/Runtime'")
    exec(compile(code,__file__,'exec'));raise SystemExit()
else:
    def regions(name):
        im=Image.open(E/'capture'/(name+'.png')).convert('L');w,h=im.size
        return [ImageStat.Stat(im.crop(box)).mean[0] for box in [(0,0,w//2,h//2),(w//2,0,w,h//2),(0,h//2,w//2,h),(w//2,h//2,w,h)]]
    r={'note':'8-bit grayscale image averages, not physical illumination; raw FHD player samples. Atmospheric particles vary between frames.','comparisons':{}}
    for kind in ['flash','strong']:
        old=regions('abbey-W06-'+kind);new=regions('abbey-W08-'+kind);normal=regions('abbey-W08-normal')
        r['comparisons'][kind]={'W06Quadrants':old,'W08Quadrants':new,'W08OverW06':[b/a for a,b in zip(old,new)],'W08OverNormal':[b/a for a,b in zip(normal,new)]}
    normal=regions('abbey-W08-normal');after=regions('abbey-after-flash');r['normalReturnRatios']=[b/a for a,b in zip(normal,after)]
    r['allQuadrantsNoticeablyBrighter']=all(v>1.25 for c in r['comparisons'].values() for v in c['W08OverW06'])
    r['darknessReturn']=all(abs(v-1)<.08 for v in r['normalReturnRatios']);r['passed']=r['allQuadrantsNoticeablyBrighter'] and r['darknessReturn'];out=E/'flash-coverage.json'
if out.exists():raise SystemExit('Refuse existing evidence '+str(out))
out.write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2));sys.exit(not r['passed'])
