"""Download only the five completed L01 Higgsfield originals, without pixel edits."""
import hashlib
import json
from pathlib import Path
import urllib.request
from PIL import Image

root = Path(__file__).resolve().parent
request = json.loads((root / 'request.json').read_text(encoding='utf-8'))
result = json.loads((root / 'completed-jobs.json').read_text(encoding='utf-8'))
jobs = result['structuredContent']['jobs']
names = {item['index']: item for item in request['stages']}
records = []
for job in jobs:
    if job['status'] != 'completed':
        raise RuntimeError(f"Job {job['index']} not completed: {job['status']}")
    stage = names[job['index']]
    target = root / (stage['name'] + '.png')
    if target.exists():
        raise FileExistsError(target)
    with urllib.request.urlopen(job['result_url'], timeout=120) as response:
        data = response.read()
    with target.open('xb') as output:
        output.write(data)
    with Image.open(target) as img:
        dimensions = list(img.size)
        img.verify()
    records.append({**stage, 'job_id': job['job_id'], 'url': job['result_url'],
                    'file': target.name, 'bytes': len(data), 'dimensions': dimensions,
                    'sha256': hashlib.sha256(data).hexdigest(), 'pixelEdits': False})
manifest = {'status': 'GENERATED_REVIEW_CANDIDATES', 'unityImported': False,
            'layoutAdopted': False, 'images': records}
with (root / 'delivery.json').open('x', encoding='utf-8') as output:
    json.dump(manifest, output, ensure_ascii=False, indent=2)
print(json.dumps(manifest, ensure_ascii=False, indent=2))
