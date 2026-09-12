"""One-time additive Weather W01 source isolation. Never rewrites the L09 baseline."""
from pathlib import Path
import hashlib, json, re, shutil, uuid

ROOT = Path(__file__).resolve().parents[4]
OLD = ROOT / 'Unity/Vesper/Assets/Vesper/Expansion/LinearWorld'
NEW = ROOT / 'Unity/Vesper/Assets/Vesper/Expansion/WeatherWorld'
EVIDENCE = ROOT / 'Migration/Evidence/Expansion/WeatherWorld/W01'
TARGET = ROOT / '.dream-loop/weather-world/targets'

def digest(p):
    h = hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda: f.read(1024*1024), b''): h.update(b)
    return h.hexdigest()

def main():
    if (NEW / 'Runtime/WorldMotor.cs').exists():
        raise SystemExit('Refuse to repeat source isolation')
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    protected = list((OLD / 'Runtime').glob('*')) + list((OLD / 'Editor').glob('*')) + list(OLD.glob('*.shader*'))
    protected += list((ROOT / 'Unity/Vesper/Builds/VesperLinearWorld_L09').rglob('*'))
    protected += list((ROOT / 'Unity/Vesper/Assets/Vesper/Scenes/Expansion').glob('VesperLinearWorld_L09.unity*'))
    protected += [ROOT / p for p in ['.gitignore', 'package-lock.json', 'PLAY_VESPER_ROAD.cmd', 'RECORD_VESPER.cmd']]
    manifest = {str(p.relative_to(ROOT)): digest(p) for p in protected if p.is_file()}
    (EVIDENCE / 'protected-before.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
    (NEW / 'Runtime').mkdir(parents=True, exist_ok=True)
    remap = {}
    for name in ['WorldMotor', 'WorldCamera', 'WorldAnimation', 'WorldRunInput', 'WorldRoofCutaway', 'WorldWeather', 'WorldEnvironment']:
        src = OLD / 'Runtime' / (name + '.cs')
        dest = NEW / 'Runtime' / src.name
        # The environment implementation is authored separately after this seed.
        dest.write_text(src.read_text(encoding='utf-8').replace('Vesper.Expansion.LinearWorld', 'Vesper.Expansion.WeatherWorld'), encoding='utf-8')
        oldguid = re.search(r'^guid: (\w+)', Path(str(src)+'.meta').read_text(), re.M)[1]
        newguid = uuid.uuid4().hex
        Path(str(dest)+'.meta').write_text('fileFormatVersion: 2\nguid: '+newguid+'\n', encoding='utf-8')
        remap[oldguid] = newguid
    (EVIDENCE / 'runtime-guid-map.json').write_text(json.dumps(remap, indent=2), encoding='utf-8')
    # A scene template with remapped component scripts. Unity's builder saves the actual candidate.
    scene = (ROOT / 'Unity/Vesper/Assets/Vesper/Scenes/Expansion/VesperLinearWorld_L09.unity').read_text(encoding='utf-8')
    for a, b in remap.items(): scene = scene.replace(a, b)
    (EVIDENCE / 'scene-template.txt').write_text(scene, encoding='utf-8')
    shaders = NEW / 'Shaders'
    shaders.mkdir(exist_ok=True)
    for name, src in [('Road', OLD/'Generated/L09/RoadSurface.shader'), ('Ground', OLD/'Ground.shader'), ('WetStone', OLD/'WetStone.shader'), ('Precipitation', OLD/'Precipitation.shader')]:
        s = src.read_text(encoding='utf-8')
        s = re.sub(r'Shader "[^"]+"', 'Shader "Vesper/Weather/'+name+'"', s, count=1)
        if name == 'Road':
            s = s.replace('float d=-i.w.z;', 'float worldD=-i.w.z; float d=worldD<=48?worldD:worldD<138?48+(worldD-48)*42/90:worldD-48;')
            s = s.replace('half wet=smoothstep(48,108,d)', 'half wet=smoothstep(98,156,worldD)')
        if name == 'WetStone':
            s = s.replace('smoothstep(214,271,-i.w.z)', 'smoothstep(262,319,-i.w.z)').replace('-147.4)', '-195.4)')
        if name == 'Precipitation':
            s = s.replace('smoothstep(55,120,d),snow=smoothstep(190,255,d)', 'smoothstep(112,168,d),snow=smoothstep(238,303,d)')
            s = s.replace('_Kind==1?snow', '(_Kind==1||_Kind==3)?snow')
            s = s.replace('else if(_Kind==1)alpha=1-smoothstep(.1,1,radius);', 'else if(_Kind==1)alpha=1-smoothstep(.1,1,radius);\n else if(_Kind==3)alpha=pow(saturate(1-radius),2)*.55;')
        (shaders/(name+'.shader')).write_text(s, encoding='utf-8')
    TARGET.mkdir(parents=True, exist_ok=True)
    for srcname, name in [('Concepts-v01/01-prestorm-forest.png','01-prestorm-forest.png'),('Concepts-v03/02-abbey-distant-flash.png','02-default-distant-flash.png'),('Concepts-v02/02-abbey-flash-only.png','02-rare-strong-flash.png'),('Concepts-v01/03-night-blizzard.png','03-night-blizzard.png')]:
        shutil.copy2(Path(__file__).parent/srcname, TARGET/name)
    (TARGET/'LOCK.json').write_text(json.dumps({'default':'distant, no bolt', 'rare':'broad strong flash, no bolt', 'brightness':'existing L09 rain baseline', 'audio':False, 'targets':{p.name:digest(p) for p in TARGET.glob('*.png')}}, indent=2), encoding='utf-8')
    print(json.dumps({'protected_files':len(manifest), 'runtime_scripts':len(remap), 'target_images':4}))

if __name__ == '__main__': main()
