"""One explicit Meshy job; credentials are read only, never persisted or printed."""
import argparse, base64, hashlib, importlib.util, json, sys
from pathlib import Path
from datetime import datetime, timezone
from urllib.request import Request, build_opener, urlopen
from urllib.error import HTTPError

ROOT = Path(__file__).resolve().parent
API = 'https://api.meshy.ai/openapi/v1/image-to-3d'

def write(name, value):
    (ROOT / name).write_text(json.dumps(value, indent=2), encoding='utf-8')

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=['create', 'status', 'download'])
    parser.add_argument('--credential-reader', required=True)
    args = parser.parse_args()
    sys.dont_write_bytecode = True
    spec = importlib.util.spec_from_file_location('credential_reader', args.credential_reader)
    reader = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(reader)
    headers = {'Authorization': 'Bearer ' + reader.read_key(), 'Content-Type': 'application/json'}
    if args.action == 'create':
        if (ROOT / 'task-created.json').exists() or (ROOT / 'creation-started.json').exists():
            raise RuntimeError('Creation already attempted; inspect status instead of duplicating.')
        source = (ROOT / 'reference-tree.png').read_bytes()
        params = dict(model_type='standard', ai_model='meshy-7', ultra_mode=True,
                      should_texture=True, enable_pbr=True, texture_resolution='4k',
                      should_remesh=False, image_enhancement=False,
                      target_formats=['glb'], multi_view_thumbnails=True)
        write('request-metadata.json', dict(parameters=params, image='reference-tree.png',
              image_sha256=hashlib.sha256(source).hexdigest(), expected_credits=35,
              api_docs='https://docs.meshy.ai/en/api/image-to-3d',
              pricing_docs='https://docs.meshy.ai/en/api/pricing'))
        write('creation-started.json', {'utc': datetime.now(timezone.utc).isoformat()})
        params['image_url'] = 'data:image/png;base64,' + base64.b64encode(source).decode('ascii')
        request = Request(API, data=json.dumps(params).encode(), headers=headers, method='POST')
        with build_opener(reader.NoRedirect).open(request, timeout=60) as response:
            result = json.load(response)
        write('task-created.json', result)
        print(json.dumps(result))
        return
    task = json.loads((ROOT / 'task-created.json').read_text())['result']
    request = Request(API + '/' + task, headers=headers)
    with build_opener(reader.NoRedirect).open(request, timeout=30) as response:
        result = json.load(response)
    # Keep expiring signed URLs only in ignored scratch, not tracked provenance.
    scratch = ROOT.parents[3] / '.dream-loop/unity-atmosphere-v2/external-asset-strategy'
    scratch.mkdir(parents=True, exist_ok=True)
    (scratch / 'tree-v11-task-private.json').write_text(json.dumps(result), encoding='utf-8')
    summary = {k: result.get(k) for k in ['id','status','progress','created_at','finished_at','consumed_credits']}
    write('task-status.json', summary)
    print(json.dumps(summary))
    if args.action != 'download' or result['status'] != 'SUCCEEDED':
        return
    downloads = {'tree-v11-original.glb': result['model_urls']['glb']}
    for name, url in result.get('thumbnail_urls', {}).items():
        downloads['preview-' + name + '.png'] = url
    for index, textures in enumerate(result.get('texture_urls', [])):
        for name, url in textures.items():
            if url: downloads['texture-' + str(index) + '-' + name + '.png'] = url
    manifest = []
    for name, url in downloads.items():
        path = ROOT / name
        if not path.exists():
            with urlopen(url, timeout=120) as response:
                payload = response.read()
            path.write_bytes(payload)
        payload = path.read_bytes()
        manifest.append(dict(file=name, bytes=len(payload), sha256=hashlib.sha256(payload).hexdigest()))
    write('download-manifest.json', dict(task_id=task, source='Meshy generated from local imagegen reference', files=manifest))
    print(json.dumps({'downloaded': len(manifest)}))

if __name__ == '__main__':
    try: main()
    except HTTPError as error:
        print(json.dumps({'error': 'HTTP_ERROR', 'status': error.code})); sys.exit(1)
    except Exception as error:
        print(json.dumps({'error': type(error).__name__})); sys.exit(1)
