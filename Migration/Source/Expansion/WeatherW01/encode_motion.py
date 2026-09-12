"""Timestamped Unity screenshot preview. Never presented as an OBS recording or FPS benchmark."""
from pathlib import Path
import csv,json,subprocess,sys
ROOT=Path(__file__).resolve().parents[4]
revision=sys.argv[1] if len(sys.argv)>1 else 'W04'
folder=ROOT/'Migration/Evidence/Expansion/WeatherWorld'/revision/'motion'
rows=list(csv.DictReader((folder/'frames.csv').open()))
parts=[];durations=[]
for i,r in enumerate(rows):
    dt=float(rows[i+1]['time'])-float(r['time']) if i+1<len(rows) and rows[i+1]['progress']==r['progress'] else .067
    durations.append(dt);parts += ["file '"+r['file']+"'",f'duration {dt:.5f}']
parts += ["file '"+rows[-1]['file']+"'"]
(folder/'preview.ffconcat').write_text('\n'.join(parts)+'\n',encoding='utf-8')
output=folder.parent/'WEATHER_PREVIEW.mp4'
if output.exists():raise SystemExit('Refuse to overwrite preview')
subprocess.run(['ffmpeg','-hide_banner','-loglevel','warning','-f','concat','-safe','0','-i',str(folder/'preview.ffconcat'),'-c:v','libx264','-crf','19','-preset','fast','-pix_fmt','yuv420p','-fps_mode','vfr','-movflags','+faststart','-an',str(output)],check=True)
stats={'revision':revision,'frames':len(rows),'duration':sum(durations),'averageSampleFps':len(rows)/sum(durations),'source':'Unmodified actual Unity screenshot sequence; durations retained from runtime timestamps, fixture wait gaps cut. Forced standard pulse previews at identified points. This is an effects preview, not a gameplay or recording performance measurement.','audio':False,'stages':sorted(set(float(r['progress']) for r in rows))}
(folder.parent/'motion-summary.json').write_text(json.dumps(stats,indent=2),encoding='utf-8')
print(json.dumps(stats,indent=2))
