from pathlib import Path
import json,subprocess,urllib.request,hashlib
source=Path(__file__).resolve().parent
data=json.loads(subprocess.check_output(['higgsfield.cmd','generate','get','3e65cfe6-9a44-4e95-aa7e-2b9929ebc732','--json'],encoding='utf-8'))
(source/'limestone-job-current.json').write_text(json.dumps(data,indent=2),encoding='utf-8')
url=data.get('result_url')
print(json.dumps({'id':data.get('id'),'status':data.get('status'),'hasResult':bool(url)}))
if url and not (source/'LimestoneFineF.png').exists():
    urllib.request.urlretrieve(url,source/'LimestoneFineF.png')
    p=source/'LimestoneFineF.png'
    (source/'limestone-download.json').write_text(json.dumps({'url':url,'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'imagePixelsEdited':False,'adopted':False},indent=2))
    print('Downloaded original texture')
