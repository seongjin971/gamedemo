"""Encode original opt-in player frames with their actual capture timestamps.

Usage: python encode_motion.py SOURCE_FOLDER OUTPUT_MP4 FFMPEG_EXE
This does not interpolate frames or certify display FPS/direct input.
"""
import json
from pathlib import Path
import subprocess
import sys

source, output, ffmpeg = Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve(), sys.argv[3]
report = json.loads((source / 'motion-report.json').read_text(encoding='utf-8'))
frames = report['frames']
assert len(frames) > 1 and not report['errors'] and report['skipped'] == 0
lines = ['ffconcat version 1.0']
for index, frame in enumerate(frames):
    path = (source / frame['file']).resolve()
    assert path.is_file() and path.parent == source
    lines.append("file '" + str(path).replace('\\', '/').replace("'", "'\\''") + "'")
    duration = frames[index + 1]['time'] - frame['time'] if index + 1 < len(frames) else frame['time'] - frames[index - 1]['time']
    assert duration > 0
    lines.append(f'duration {duration:.9f}')
lines.append(lines[-2])
concat = source / 'motion.ffconcat'
concat.write_text('\n'.join(lines) + '\n', encoding='utf-8')
output.parent.mkdir(parents=True, exist_ok=True)
subprocess.run([ffmpeg, '-hide_banner', '-loglevel', 'warning', '-n', '-f', 'concat', '-safe', '0', '-i', str(concat), '-fps_mode', 'vfr', '-c:v', 'libx264', '-threads', '2', '-crf', '18', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', str(output)], check=True)
summary = {'note': 'Original JPEG95 frames, variable frame rate from actual capture timestamps; no interpolation. Not clean FPS or direct input evidence.', 'frames': len(frames), 'distance': report['distance'], 'skipped': report['skipped'], 'errors': report['errors'], 'unfocused': sum(not f['focused'] for f in frames), 'stages': []}
for stage in dict.fromkeys(f['stage'] for f in frames):
    group = [f for f in frames if f['stage'] == stage]
    summary['stages'].append({'stage': stage, 'frames': len(group), 'hz': (len(group)-1)/(group[-1]['time']-group[0]['time']), 'maximumGapSeconds': max(b['time']-a['time'] for a,b in zip(group,group[1:]))})
output.with_name('motion-summary.json').write_text(json.dumps(summary, indent=2) + '\n', encoding='utf-8')
print(json.dumps(summary))
