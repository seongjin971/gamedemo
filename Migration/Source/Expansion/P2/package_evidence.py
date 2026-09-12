"""Run after all isolated player performance measurements have exited."""
from pathlib import Path
import hashlib
import json
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[4]
EVIDENCE = ROOT / 'Migration/Evidence/Expansion/P2'

def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(4 * 1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()

def audit():
    before = json.loads((EVIDENCE / 'protection-before.json').read_text())
    allowed = {'CHECKPOINT.md', 'EXPANSION_PLAN.md', 'PLAY_EXPANSION.md',
               'Unity/Vesper/Packages/manifest.json', 'Unity/Vesper/Packages/packages-lock.json'}
    changed = [name for name, old in before.items()
               if not (ROOT / name).is_file() or digest(ROOT / name) != old]
    violations = [name for name in changed if name not in allowed]
    result = {'checked': len(before), 'unchanged': len(before)-len(changed),
              'authorizedChanges': [name for name in changed if name in allowed],
              'violations': violations}
    (EVIDENCE / 'protection-audit.json').write_text(json.dumps(result, indent=2))
    build = ROOT / 'Unity/Vesper/Builds/VesperP2'
    manifest = {p.relative_to(build).as_posix(): digest(p) for p in build.rglob('*') if p.is_file()}
    (EVIDENCE / 'build-hashes.json').write_text(json.dumps(manifest, indent=2))
    print(result)
    if violations:
        raise SystemExit(1)

def video(folder):
    sys.path.insert(0, str(ROOT / '.dream-loop/p2-tools'))
    import imageio_ffmpeg
    folder = EVIDENCE / folder
    report = json.loads((folder / 'motion-report.json').read_text())
    frames = report['frames']
    lines = ['ffconcat version 1.0']
    for i, frame in enumerate(frames):
        duration = frames[i+1]['time'] - frame['time'] if i+1 < len(frames) else .15
        lines.extend([f"file '{frame['file']}'", f'duration {duration:.6f}'])
    lines.append(f"file '{frames[-1]['file']}'")
    (folder / 'frames.ffconcat').write_text('\n'.join(lines)+'\n')
    subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), '-hide_banner', '-loglevel', 'error', '-y',
                    '-safe', '0', '-i', str(folder / 'frames.ffconcat'),
                    '-fps_mode', 'vfr', '-c:v', 'libx264', '-threads', '4', '-crf', '21',
                    '-pix_fmt', 'yuv420p', str(folder / 'motion.mp4')], check=True)
    print('Timestamp-preserving video:', folder / 'motion.mp4')

if __name__ == '__main__':
    if sys.argv[1] == 'audit':
        audit()
    elif sys.argv[1] == 'video':
        video(sys.argv[2])
