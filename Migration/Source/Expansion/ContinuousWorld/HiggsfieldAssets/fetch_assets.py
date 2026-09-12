"""Poll the three authorized CLI jobs and download their original GLB outputs."""
import json,subprocess,time,urllib.request
from pathlib import Path
SOURCE=Path(__file__).resolve().parent
JOBS={'rock':'dda3a429-d355-404d-81e1-39eba93618df','fir':'d545ebc1-f197-47c4-abe8-d2f2f9f55295','alder':'156e139b-457a-4556-9d54-ffd8872859f5',
      'fir_hunyuan':'d8c1cc6c-26f3-4bcc-a0ce-2ee7b7793abe','buttress':'c4658017-eef3-4be9-b602-a6c79a79738c'}
remaining={k:v for k,v in JOBS.items() if not (SOURCE/(k+'.glb')).exists()}
deadline=time.monotonic()+1200
while remaining and time.monotonic()<deadline:
    for key,jobid in list(remaining.items()):
        reply=subprocess.run(['higgsfield.cmd','generate','get',jobid,'--json'],capture_output=True,text=True,encoding='utf8',check=True)
        data=json.loads(reply.stdout); (SOURCE/(key+'-job.json')).write_text(json.dumps(data,indent=2),encoding='utf8')
        print(key,data['status'],flush=True)
        url=data.get('result_url')
        if url:
            if not isinstance(url,str): raise RuntimeError('Unexpected result URL structure '+repr(url))
            urllib.request.urlretrieve(url,SOURCE/(key+'.glb'))
            print('DOWNLOADED',key,(SOURCE/(key+'.glb')).stat().st_size,flush=True)
            del remaining[key]
        elif data['status'] in ('failed','cancelled'):
            raise RuntimeError(key+' job '+data['status'])
    if remaining:time.sleep(30)
print('PENDING',list(remaining),flush=True)
