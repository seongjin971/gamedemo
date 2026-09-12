"""Read final opt-in runtime evidence; fail closed on missing/incomplete records."""
from pathlib import Path
import hashlib, json, sys

root = Path(__file__).resolve().parents[4]
revision = sys.argv[1]
folder = root / 'Migration/Evidence/Expansion/ContinuousWorld' / revision
issues, checks, summaries = [], [], {}

def require(condition, description):
    (checks if condition else issues).append(description)

def read(path):
    if not path.is_file():
        issues.append('Missing ' + str(path.relative_to(root)))
        return {}
    return json.loads(path.read_text(encoding='utf-8-sig'))

build = read(folder / 'build.json')
require(build.get('result') == 'Succeeded' and build.get('errors') == 0, 'Build succeeded without errors')
prepare = read(folder / 'prepare.json')
require(len(prepare.get('routes', [])) == 12 and all(x.startswith('PASS') for x in prepare.get('routes', [])), '12 complete prepared route legs')
require(prepare.get('missingScripts') == 0, 'No missing scripts')
for mode in ['qa', 'edges', 'weather', 'performance', 'film']:
    r = read(folder / mode / 'report.json')
    require(r.get('failures') == 0 and r.get('errors') == [], mode + ': no failures/runtime errors')
    require(r.get('resets') == 0 and r.get('safetyStops') == 0, mode + ': no resets/safety stops')
    summaries[mode] = {k: r.get(k) for k in ['clicks', 'blocked', 'samples', 'distance', 'width', 'height']}
    if mode == 'qa':
        require(r.get('clicks') == 450 and r.get('blocked') == 0, '450 accepted whole-route screen clicks')
        require('PASS Full continuous round trip 3 without reset' in r.get('checks', []), 'Three completed continuous round trips')
        require(len(list((folder / mode).glob('*.png'))) == 16, '16 native captures during continuous traversal')
    elif mode == 'edges':
        require(r.get('clicks') == 44 and r.get('blocked') == 5, '44 edge clicks / five intended rejections')
    elif mode == 'weather':
        require(len(r.get('checks', [])) == 42 and all(c.startswith('PASS') for c in r.get('checks', [])), '42 weather/shelter checks')
        require(all(c in r.get('checks', []) for c in ['PASS Real roof blocks falling precipitation above shelter', 'PASS Player reaches covered space without reset', 'PASS Outdoor rain continues while player is sheltered', 'PASS Shelter round trip exits normally']), 'Required roof, entry, outside rain and exit checks present')
    elif mode == 'performance':
        p = r.get('performance', [])
        require(len(p) == 20 and all(x['unfocused'] == 0 for x in p), '20 focused performance intervals')
        if p:
            summaries[mode].update(minFPS=min(x['fps'] for x in p), maxFPS=max(x['fps'] for x in p), worstP95Ms=max(x['p95Ms'] for x in p))
    elif mode == 'capture':
        require(len(list((folder / mode).glob('*.png'))) == 18, '18 native still captures')
    elif mode == 'film':
        require(r.get('clicks') == 9 and len(r.get('checks', [])) == 9, 'Nine local moving fixture recordings')
        videos = read(folder / mode / 'video-manifest.json').get('clips', [])
        require(len(videos) == 9 and all((folder / mode / x['video']).is_file() for x in videos), 'Nine encoded local videos')

source = root / 'Unity/Vesper/Assets/Vesper/Expansion/ContinuousWorld'
prepared = read(folder / 'prepare-source/manifest.json')
built = read(folder / 'build-source/manifest.json')
require(prepared == built, 'Prepare and build source manifests identical')
if isinstance(built, list):
    require(all(hashlib.sha256((source / x['Path']).read_bytes()).hexdigest().upper() == x['SHA256'] for x in built), 'Current runtime/editor/shader source matches build snapshot')
exe = root / 'Unity/Vesper/Builds' / ('VesperContinuousWorld_' + revision) / 'VesperWorld.exe'
require(exe.is_file(), 'Standalone executable exists')
result = dict(revision=revision, passed=not issues, checks=checks, issues=issues, summaries=summaries,
              note='Technical evidence only. Film contains separate local fixtures; timing is natural frame cadence. Independent visual score, physical device/user acceptance and preservation audit are separate.')
(folder / 'delivery-audit.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
print(json.dumps(result, indent=2))
sys.exit(bool(issues))
