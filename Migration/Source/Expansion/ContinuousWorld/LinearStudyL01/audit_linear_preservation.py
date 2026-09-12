"""Read existing manifests; never regenerate or mutate prior preservation evidence."""
from pathlib import Path
import datetime, hashlib, json, sys

ROOT = Path(__file__).resolve().parents[5]
OLD = ROOT / 'Migration/Evidence/Expansion/ContinuousWorld/VisualF'
baseline = json.loads((OLD / 'preservation-baseline-20260910.json').read_text(encoding='utf-8-sig'))
f02 = json.loads((OLD / 'F02-uncompiled-source-manifest.json').read_text(encoding='utf-8-sig'))
fixed = {
    '.gitignore', 'package-lock.json', 'PLAY_VESPER_WORLD.cmd',
    'Migration/Evidence/Expansion/ContinuousWorld/protection-before.json',
    'Migration/Evidence/Expansion/ContinuousWorld/E02/delivery-audit.json',
    'Unity/Vesper/Assets/UniversalRenderPipelineGlobalSettings.asset',
    'Unity/Vesper/Assets/Vesper/AtmosphereV2/Settings/AtmosphereURP.asset',
    'Unity/Vesper/ProjectSettings/GraphicsSettings.asset',
    'Unity/Vesper/ProjectSettings/ProjectAuditorSettings.asset',
    'Unity/Vesper/ProjectSettings/ProjectSettings.asset',
}
prefixes = (
    'Unity/Vesper/Builds/VesperContinuousWorld_E02/',
    'Unity/Vesper/Assets/Vesper/Expansion/ContinuousWorld/',
    'Unity/Vesper/Assets/Vesper/Scenes/Expansion/VesperContinuousWorld',
)
expected = {n: h for n, h in baseline.items() if n in fixed or n.startswith(prefixes)}
expected.update(f02)  # The later safe-stop source manifest is authoritative for F02 drafts.
sha = lambda b: hashlib.sha256(b).hexdigest()
changes, newline_only = [], []
for name, wanted in expected.items():
    p = ROOT / name
    if not p.is_file():
        changes.append({'path': name, 'missing': True})
        continue
    raw = p.read_bytes()
    if sha(raw) == wanted:
        continue
    candidate = raw.replace(b'\r\n', b'\n').replace(b'\n', b'\r\n')
    record = {'path': name, 'expected': wanted, 'actual': sha(raw)}
    if name in fixed and sha(candidate) == wanted:
        newline_only.append(record)
    else:
        changes.append(record)
report = {
    'timeUtc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'scope': 'Bounded read-only comparison: E02 complete build, ContinuousWorld assets/source/scenes available in prior baseline, later F02 source manifest, five Unity-reserialized shared settings, original preservation evidence, launcher and IDE files. Not a full 24061-file rehash. No prior script executed or baseline rewritten.',
    'checked': len(expected), 'f02SourceFiles': len(f02),
    'changes': changes, 'exactCrLfOnlyChanges': newline_only,
}
out = ROOT / 'Migration/Evidence/Expansion/LinearWorld' / sys.argv[1]
with out.open('x', encoding='utf-8') as f:
    json.dump(report, f, indent=2)
print(json.dumps(report, indent=2))
