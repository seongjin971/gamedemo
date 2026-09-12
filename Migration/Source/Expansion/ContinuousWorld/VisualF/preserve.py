from pathlib import Path
import hashlib, json, subprocess, sys
ROOT = Path(__file__).resolve().parents[5]
OUT = ROOT / 'Migration/Evidence/Expansion/ContinuousWorld/VisualF'
def sha(p):
    h = hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda: f.read(4*1024*1024), b''): h.update(b)
    return h.hexdigest()
OUT.mkdir(parents=True, exist_ok=True)
baseline = OUT / 'preservation-baseline-20260910.json'
if sys.argv[1] == 'before':
    if baseline.exists(): raise SystemExit('Refusing to overwrite baseline')
    names = subprocess.check_output(['git','ls-files','--cached','--others','--exclude-standard','-z'], cwd=ROOT).decode().split('\0')
    paths = {ROOT/n for n in names if n and (ROOT/n).is_file()}
    for folder in ['Unity/Vesper/Builds','.dream-loop/continuous-world']:
        paths.update(p for p in (ROOT/folder).rglob('*') if p.is_file())
    manifest = {p.relative_to(ROOT).as_posix():sha(p) for p in sorted(paths) if 'ContinuousWorld/VisualF/' not in p.as_posix()}
    with baseline.open('x', encoding='utf-8') as f: json.dump(manifest,f,indent=2)
    (OUT/'git-status-before.txt').write_bytes(subprocess.check_output(['git','status','--short'],cwd=ROOT))
    print(json.dumps({'files':len(manifest),'baseline':str(baseline)}))
else:
    manifest=json.loads(baseline.read_text())
    changed=[n for n,h in manifest.items() if not (ROOT/n).is_file() or sha(ROOT/n)!=h]
    print(json.dumps({'files':len(manifest),'changed':changed},indent=2))
