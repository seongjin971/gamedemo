from pathlib import Path
import hashlib,json,sys,shutil

ROOT=Path(__file__).resolve().parents[4]
E=ROOT/'Migration/Evidence/Expansion/WeatherWorld/W06'
ASSETS=ROOT/'Unity/Vesper/Assets/Vesper/Expansion/WeatherWorld'
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()
if sys.argv[1]=='before':
    E.mkdir(parents=True,exist_ok=True)
    out=E/'protected-before.json'
    if out.exists():raise SystemExit('Refuse to overwrite W06 audit')
    paths=set()
    for base in [ROOT/'Unity/Vesper/Builds/VesperWeatherWorld_W05',ASSETS/'Generated',ROOT/'Migration/Evidence/Expansion/WeatherWorld/W05']:
        paths.update(p for p in base.rglob('*') if p.is_file())
    paths.update((ROOT/'Unity/Vesper/Assets/Vesper/Scenes/Expansion').glob('VesperWeatherWorld_W*'))
    paths.update(ROOT/p for p in ['.gitignore','package-lock.json','RECORD_VESPER_WEATHER.cmd'])
    old=json.loads((ROOT/'Migration/Evidence/Expansion/WeatherWorld/W01/protected-before.json').read_text())
    paths.update(ROOT/p for p in old)
    out.write_text(json.dumps({str(p.relative_to(ROOT)).replace('\\','/'):sha(p) for p in sorted(paths)},indent=2))
    shutil.copytree(ASSETS/'Runtime',E/'before-source/Runtime')
    shutil.copytree(ASSETS/'Editor',E/'before-source/Editor')
    shutil.copytree(ASSETS/'Shaders',E/'before-source/Shaders')
    shutil.copy2(ROOT/'PLAY_VESPER_WEATHER.cmd',E/'PLAY_VESPER_WEATHER_W05.cmd')
    print('Preserved',len(paths),'files and before-source')
else:
    before=json.loads((E/'protected-before.json').read_text())
    changed=[p for p,h in before.items() if not (ROOT/p).is_file() or sha(ROOT/p)!=h]
    report={'protectedFiles':len(before),'changed':changed,'passed':not changed}
    out=E/'protected-after.json'
    if out.exists():raise SystemExit('Refuse to overwrite audit result')
    out.write_text(json.dumps(report,indent=2));print(json.dumps(report));raise SystemExit(bool(changed))
