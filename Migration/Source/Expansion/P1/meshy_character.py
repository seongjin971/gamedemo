"""Bounded P1 generation. Credentials are imported read-only and never logged.

Usage: python -B meshy_character.py balance|create|status|download model|rig|idle
Each stage has an exclusive submission marker to prevent accidental duplicate spend.
"""
import base64, hashlib, importlib.util, json, sys
from pathlib import Path
from urllib.request import Request, build_opener, urlopen
from urllib.error import HTTPError
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parent
WORKSPACE = ROOT.parents[3]
SCRATCH = WORKSPACE / '.dream-loop/expansion-p1'
READER = Path('C:/Users/brian/Dev/active/2ndKoreawar/Tools/Meshy/check_connection.py')
ENDPOINTS = {'model': 'image-to-3d', 'rig': 'rigging', 'idle': 'animations'}

def write(name, data):
    (ROOT / name).write_text(json.dumps(data, indent=2), encoding='utf-8')

def main():
    action = sys.argv[1]
    stage = sys.argv[2] if len(sys.argv)>2 else 'model'
    spec = importlib.util.spec_from_file_location('credential_reader', READER)
    reader = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(reader)
    headers = {'Authorization': 'Bearer '+reader.read_key(), 'Content-Type': 'application/json'}
    def request(endpoint, data=None):
        req = Request('https://api.meshy.ai/openapi/v1/'+endpoint,
                      data=json.dumps(data).encode() if data is not None else None,
                      headers=headers, method='POST' if data is not None else 'GET')
        with build_opener(reader.NoRedirect).open(req, timeout=60) as response:
            return json.load(response)
    if action=='balance':
        data=request('balance')
        safe={'utc': datetime.now(timezone.utc).isoformat(), 'authenticated': True,
              'balance':data.get('balance')}
        write('connection.json',safe); print(json.dumps(safe)); return
    endpoint=ENDPOINTS[stage]
    if action=='create':
        if len(list(ROOT.glob('*-submission.json'))) >= 3:
            raise RuntimeError('Three-job user limit reached; additional approval required')
        marker=ROOT/(stage+'-submission.json')
        if marker.exists(): raise RuntimeError('Stage already submitted; inspect status')
        if stage=='model':
            source=(ROOT/'reference-adventurer.png').read_bytes()
            data=dict(model_type='standard',ai_model='meshy-7',ultra_mode=True,
                      should_texture=True,enable_pbr=True,texture_resolution='2k',
                      should_remesh=True,topology='triangle',target_polycount=30000,
                      pose_mode='a-pose',image_enhancement=False,target_formats=['glb'],
                      multi_view_thumbnails=True)
            write('model-request.json',dict(parameters=data,image_sha256=hashlib.sha256(source).hexdigest(),
                  source='OpenAI built-in imagegen, original P1 character design',
                  docs='https://docs.meshy.ai/en/api/image-to-3d'))
            data['image_url']='data:image/png;base64,'+base64.b64encode(source).decode()
        elif stage=='rig':
            data=dict(input_task_id=json.loads((ROOT/'model-created.json').read_text())['result'],height_meters=1.78)
            write('rig-request.json', data)
        else:
            data=dict(rig_task_id=json.loads((ROOT/'rig-created.json').read_text())['result'],action_id=0)
            write('idle-request.json',data)
        with marker.open('x') as f: json.dump({'utc':datetime.now(timezone.utc).isoformat()},f)
        result=request(endpoint,data)
        write(stage+'-created.json',result);print(json.dumps(result));return
    task=json.loads((ROOT/(stage+'-created.json')).read_text())['result']
    data=request(endpoint+'/'+task)
    SCRATCH.mkdir(parents=True,exist_ok=True)
    (SCRATCH/(stage+'-private.json')).write_text(json.dumps(data),encoding='utf-8')
    safe={k:data.get(k) for k in ('id','status','progress','created_at','finished_at','consumed_credits','task_error')}
    write(stage+'-status.json',safe);print(json.dumps(safe))
    if action!='download' or data['status']!='SUCCEEDED': return
    downloads={}
    if stage=='model':
        downloads['original.glb']=data['model_urls']['glb']
        for key,url in data.get('thumbnail_urls',{}).items():
            if url: downloads['preview-'+key+'.png']=url
        for index,maps in enumerate(data.get('texture_urls',[])):
            for key,url in maps.items():
                if url: downloads['texture-'+str(index)+'-'+key+'.png']=url
    elif stage=='rig':
        result=data['result'];downloads['rigged.glb']=result['rigged_character_glb_url']
        for key,url in result.get('basic_animations',{}).items():
            if key in ('walking_glb_url','walking_fbx_url'):downloads[key.replace('_url','').replace('_glb','.glb').replace('_fbx','.fbx')]=url
    else:
        for key,url in data.get('result',{}).items():
            if isinstance(url,str) and url.startswith('https:') and 'glb' in key:downloads['idle-'+key+'.glb']=url
    manifest=[]
    for name,url in downloads.items():
        path=ROOT/name
        if not path.exists():
            with urlopen(url,timeout=120) as response:path.write_bytes(response.read())
        manifest.append(dict(file=name,bytes=path.stat().st_size,sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
    write(stage+'-manifest.json',{'task_id':task,'files':manifest});print(json.dumps({'downloaded':len(manifest)}))

if __name__=='__main__':
    try:main()
    except HTTPError as e:print(json.dumps({'error':'HTTP_ERROR','status':e.code}));sys.exit(1)
    except Exception as e:print(json.dumps({'error':type(e).__name__}));sys.exit(1)
