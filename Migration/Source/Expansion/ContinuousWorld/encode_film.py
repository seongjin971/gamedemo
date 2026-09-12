"""Encode internal Unity render captures at their recorded realtime cadence.

The nine fixture cuts are explicitly retained; this is not a seamless traversal
recording or a performance benchmark. Original PNGs and timing CSV stay intact.
"""
import argparse
import csv
import json
import subprocess
from pathlib import Path

p = argparse.ArgumentParser()
p.add_argument('folder', type=Path)
p.add_argument('--ffmpeg', type=Path, required=True)
a = p.parse_args()
folder = a.folder.resolve()
rows = list(csv.DictReader((folder / 'frames.csv').open(encoding='utf-8')))
if not rows:
    raise SystemExit('No recorded frames')
groups = {}
for row in rows:
    path = (folder / row['file']).resolve()
    if not path.is_relative_to(folder) or not path.is_file():
        raise SystemExit(f'Invalid/missing recorded frame: {path}')
    groups.setdefault(row['fixture'], []).append(row)
manifest = []
for fixture, frames in groups.items():
    concat = folder / f'fixture-{fixture}.ffconcat'
    lines = ['ffconcat version 1.0']
    total = 0.0
    for i, row in enumerate(frames):
        duration = (float(frames[i+1]['realtime']) - float(row['realtime'])) if i+1 < len(frames) else 1/12
        if duration <= 0:
            raise SystemExit('Nonmonotonic capture timing')
        total += duration
        name = row['file'].replace("'", "'\\''")
        lines.extend([f"file '{name}'", f'duration {duration:.6f}'])
    lines.append(f"file '{frames[-1]['file']}'")
    concat.write_text('\n'.join(lines)+'\n', encoding='utf-8')
    dest = folder / f'fixture-{fixture}.mp4'
    subprocess.run([str(a.ffmpeg), '-hide_banner', '-loglevel', 'error', '-n', '-f', 'concat', '-safe', '0', '-i', str(concat), '-fps_mode', 'vfr', '-c:v', 'libx264', '-preset', 'fast', '-crf', '19', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', str(dest)], check=True)
    manifest.append(dict(fixture=fixture, frames=len(frames), recordedSeconds=total, video=dest.name))
(folder / 'video-manifest.json').write_text(json.dumps(dict(note='Internal live render captures. Nine separately placed fixture clips, recorded realtime cadence. Silent video; not seamless traversal or FPS evidence.', clips=manifest), indent=2), encoding='utf-8')
print(json.dumps(manifest, indent=2))
