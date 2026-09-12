"""Summarize real captured motion and encode variable-timestamp video after FPS QA."""
import json,sys,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];folder=Path(sys.argv[1]).resolve()
d=json.loads((folder/'motion-report.json').read_text(encoding='utf-8-sig'));fs=d['frames'];groups={}
for f in fs:groups.setdefault(f['stage'],[]).append(f)
summary={k:d[k] for k in ['width','height','distance','peakSpeed','skipped','errors','passed']}
summary.update(frames=len(fs),unfocused=sum(not f['focused'] for f in fs),stages={})
for name,rows in groups.items():
 summary['stages'][name]={'frames':len(rows),'captureHz':(len(rows)-1)/(rows[-1]['time']-rows[0]['time']),'peakSpeed':max(r['speed'] for r in rows),'peakRunBlend':max(r['runBlend'] for r in rows),'first':rows[0]['file'],'middle':rows[len(rows)//2]['file'],'last':rows[-1]['file']}
(folder/'motion-summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
entries=[]
for i,f in enumerate(fs):
 entries.append("file '"+f['file']+"'");entries.append('duration '+str(max(.001,fs[i+1]['time']-f['time']) if i+1<len(fs) else 1/12))
entries.append("file '"+fs[-1]['file']+"'");(folder/'frames.ffconcat').write_text('\n'.join(entries))
if '--video' in sys.argv:
 ffmpeg=ROOT/'.dream-loop/qa-video-tools/imageio_ffmpeg/binaries/ffmpeg-win-x86_64-v7.1.exe'
 subprocess.run([str(ffmpeg),'-hide_banner','-loglevel','error','-y','-f','concat','-safe','0','-i',str(folder/'frames.ffconcat'),'-fps_mode','vfr','-c:v','libx264','-crf','20','-pix_fmt','yuv420p',str(folder/'motion.mp4')],check=True)
print(json.dumps(summary,indent=2))
