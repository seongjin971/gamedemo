"""Read-only diagnostics and build preservation audit; run outside FPS benchmark."""
from pathlib import Path
import json, hashlib, statistics, math
ROOT=Path(__file__).resolve().parents[4]
OUT=ROOT/'Migration/Evidence/Expansion/P1-Mixamo'
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest().upper()
audit={}
for label,rel in [('candidate58','Migration/Evidence/Expansion/P1/baseline/protected-hashes.json'),('deliveredP1','Migration/Evidence/Expansion/P1/player-03/build-hashes.json')]:
    rows=read(ROOT/rel)
    mismatches=[r['path'] for r in rows if not (ROOT/r['path']).exists() or sha(ROOT/r['path'])!=r['sha256'].upper()]
    audit[label]={'checked':len(rows),'mismatches':mismatches}
(OUT/'protection-audit.json').write_text(json.dumps(audit,indent=2))
build=ROOT/'Unity/Vesper/Builds/VesperMixamo'
manifest=[{'path':str(p.relative_to(ROOT)),'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(build.rglob('*')) if p.is_file()]
(OUT/'player-01/build-hashes.json').write_text(json.dumps(manifest,indent=2))
comparison={'note':'Adjacent isolated 1536x1024 natural player frame loops, automatic commands, not hardware present or direct input.'}
new=read(OUT/'player-01/performance/player-report.json')
old=read(OUT/'baseline-p1/performance/player-report.json')
comparison['stages']=[{'stage':n['name'],'originalP1Fps':o['fps'],'mixamoFps':n['fps'],'changePercent':(n['fps']/o['fps']-1)*100} for o,n in zip(old['stages'],new['stages'])]
(OUT/'performance-comparison.json').write_text(json.dumps(comparison,indent=2))
proxy={'note':'Approximate low-toe contact proxy at constant cruise speed. Joint positions are not sole contacts and turns may inflate values. Same method applied to both runs; not visual acceptance.'}
for label,folder in [('originalP1',ROOT/'Migration/Evidence/Expansion/P1/player-03/motion'),('mixamo',OUT/'player-01/motion')]:
    fs=read(folder/'motion-report.json')['frames']; result={}
    for foot in ['leftToe','rightToe']:
        lo=min(f[foot]['y'] for f in fs); samples=[]
        for a,b in zip(fs,fs[1:]):
            dt=b['time']-a['time']
            if a['stage']!=b['stage'] or min(a['speed'],b['speed'])<2.2 or max(a[foot]['y'],b[foot]['y'])>lo+.035 or dt<=0: continue
            samples.append(math.hypot(b[foot]['x']-a[foot]['x'],b[foot]['z']-a[foot]['z'])/dt)
        result[foot]={'minHeight':lo,'samples':len(samples),'medianUnitsPerSecond':statistics.median(samples) if samples else None,'maxUnitsPerSecond':max(samples) if samples else None}
    proxy[label]=result
(OUT/'contact-comparison.json').write_text(json.dumps(proxy,indent=2))
print(json.dumps({'protection':audit,'performance':comparison,'contact':proxy},indent=2))
