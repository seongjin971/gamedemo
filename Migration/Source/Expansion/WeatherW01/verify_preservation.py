from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[4]
before=json.loads((ROOT/'Migration/Evidence/Expansion/WeatherWorld/W01/protected-before.json').read_text())
def digest(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()
changed=[p for p,h in before.items() if not (ROOT/p).is_file() or digest(ROOT/p)!=h]
result={'protected_files':len(before),'changed':changed,'passed':not changed,'scope':'Exact initial hashes for L09 build, scene, LinearWorld runtime/editor/root shaders and protected launchers/user files. This is not a new baseline.'}
path=ROOT/'Migration/Evidence/Expansion/WeatherWorld/protected-after.json'
path.write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(result,indent=2))
raise SystemExit(bool(changed))
