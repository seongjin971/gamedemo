from pathlib import Path
import hashlib,json,subprocess,sys
ROOT=Path(__file__).resolve().parents[4]
OUT=ROOT/'Migration/Evidence/Expansion/ContinuousWorld'
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for block in iter(lambda:f.read(4*1024*1024),b''): h.update(block)
    return h.hexdigest()
if sys.argv[1]=='before':
    names=subprocess.check_output(['git','ls-files','-z'],cwd=ROOT).decode().split('\0')
    paths={ROOT/n for n in names if n and (ROOT/n).is_file()}
    paths.update(p for p in (ROOT/'Unity/Vesper/Builds').rglob('*') if p.is_file())
    paths.add(ROOT/'CONTINUOUS_MAP_PLAN.md')
    before={p.relative_to(ROOT).as_posix():sha(p) for p in sorted(paths)}
    (OUT/'protection-before.json').write_text(json.dumps(before,indent=2))
    for name in ['CHECKPOINT.md','EXPANSION_PLAN.md','CONTINUOUS_MAP_PLAN.md']:
        (OUT/('original-'+name)).write_bytes((ROOT/name).read_bytes())
    print('Protected',len(before),'files')
else:
    before=json.loads((OUT/'protection-before.json').read_text())
    allowed={'CHECKPOINT.md','EXPANSION_PLAN.md','CONTINUOUS_MAP_PLAN.md'}
    changed=[n for n,h in before.items() if not (ROOT/n).is_file() or sha(ROOT/n)!=h]
    result={'checked':len(before),'unchanged':len(before)-len(changed),'authorizedDocs':[n for n in changed if n in allowed],'violations':[n for n in changed if n not in allowed]}
    (OUT/'protection-final.json').write_text(json.dumps(result,indent=2))
    print(result)
    sys.exit(bool(result['violations']))
