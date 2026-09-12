"""Summarize recorded frames and build a timestamp-preserving review video.

This never treats video output FPS as the application's performance.
"""
import json, sys, subprocess, math, statistics
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
folder=Path(sys.argv[1]).resolve()
data=json.loads((folder/'motion-report.json').read_text(encoding='utf-8-sig'))
frames=data['frames']
groups={}
for f in frames:groups.setdefault(f['stage'],[]).append(f)
summary={'frames':len(frames),'distance':data['distance'],'errors':data['errors'],'skipped':data['skipped'],
         'unfocused':sum(not f['focused'] for f in frames),'stages':{}}
for name,rows in groups.items():
    elapsed=rows[-1]['time']-rows[0]['time']
    summary['stages'][name]={'frames':len(rows),'seconds':elapsed,
        'captureHz':(len(rows)-1)/elapsed if elapsed else 0,'minSpeed':min(r['speed'] for r in rows),'maxSpeed':max(r['speed'] for r in rows),
        'first':rows[0]['file'],'middle':rows[len(rows)//2]['file'],'last':rows[-1]['file']}
summary['arrivals']=data['arrivals']
(folder/'motion-summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
entries=[]
for i,f in enumerate(frames):
    entries.append("file '"+f['file']+"'")
    duration=(frames[i+1]['time']-f['time']) if i+1<len(frames) else 1/12
    entries.append('duration '+str(max(.001,duration)))
entries.append("file '"+frames[-1]['file']+"'")
(folder/'frames.ffconcat').write_text('\n'.join(entries),encoding='utf-8')
ffmpeg=ROOT/'.dream-loop/qa-video-tools/imageio_ffmpeg/binaries/ffmpeg-win-x86_64-v7.1.exe'
if '--video' in sys.argv:
    subprocess.run([str(ffmpeg),'-hide_banner','-loglevel','warning','-y','-f','concat','-safe','0','-i',str(folder/'frames.ffconcat'),
        '-fps_mode','vfr','-c:v','libx264','-crf','20','-pix_fmt','yuv420p',str(folder/'motion.mp4')],check=True)
print(json.dumps(summary,indent=2))
