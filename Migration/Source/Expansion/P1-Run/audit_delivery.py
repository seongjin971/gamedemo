"""Read-only preservation and isolated performance summary; run after measurements."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];OUT=ROOT/'Migration/Evidence/Expansion/P1-Run'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest().upper()
audit={}
for label,path in [('candidate58','P1/baseline/protected-hashes.json'),('originalP1','P1/player-03/build-hashes.json'),('mixamoWalk','P1-Mixamo/player-01/build-hashes.json')]:
 rows=read(OUT.parent/path);audit[label]={'checked':len(rows),'mismatches':[r['path'] for r in rows if not (ROOT/r['path']).exists() or sha(ROOT/r['path'])!=r['sha256'].upper()]}
(OUT/'protection-audit.json').write_text(json.dumps(audit,indent=2))
build=ROOT/'Unity/Vesper/Builds/VesperRun'
manifest=[{'path':str(p.relative_to(ROOT)),'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(build.rglob('*')) if p.is_file()]
(OUT/'player-02/build-hashes.json').write_text(json.dumps(manifest,indent=2))
old=read(OUT/'baseline-walk/performance/player-report.json');new=read(OUT/'player-02/performance/player-report.json')
comparison={'note':'Adjacent standalone natural frame cadence, same1536x1024, no other rendering/encoding. Not hardware presentation or direct input.',
 'stages':[{'name':n['name'],'walkBuildFps':o['fps'],'runBuildFps':n['fps'],'changePercent':(n['fps']/o['fps']-1)*100} for o,n in zip(old['stages'],new['stages'])],
 'continuous':read(OUT/'player-02/run-performance/run-performance.json')}
(OUT/'performance-comparison.json').write_text(json.dumps(comparison,indent=2))
print(json.dumps({'preservation':audit,'performance':comparison},indent=2))
