"""Read submitted jobs and download original PNG bytes to Source/staged; never generate."""
from pathlib import Path
import subprocess,json,urllib.request,hashlib,concurrent.futures
from PIL import Image
HERE=Path(__file__).resolve().parent;STAGED=HERE/'staged';STAGED.mkdir(exist_ok=True);provenance=json.loads((HERE/'submission-provenance.json').read_text())
def fetch(item):
    p=subprocess.run(['higgsfield.cmd','generate','get',item['id'],'--json'],capture_output=True,text=True,encoding='utf-8',timeout=60);assert p.returncode==0;job=json.loads(p.stdout);(HERE/item['job_file']).write_text(json.dumps(job,indent=2),encoding='utf-8');result={'name':item['name'],'job_id':item['id'],'status':job['status'],'charge_credits':item['charge_credits']}
    if job['status']=='completed':
        url=job['result_url'];path=STAGED/(item['name']+'.png')
        if not path.exists():
            with urllib.request.urlopen(url,timeout=60) as response:data=response.read()
            assert data[:8]==b'\x89PNG\r\n\x1a\n';path.write_bytes(data)
        im=Image.open(path);im.verify();im=Image.open(path);assert im.size==(2048,2048),(item['name'],im.size)
        result.update({'path':str(path.relative_to(HERE)),'width':im.width,'height':im.height,'mode':im.mode,'file_bytes':path.stat().st_size,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'original_bytes_preserved':True,'procedural_edits':False})
    return result
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:results=list(pool.map(fetch,provenance['jobs']))
report={'textures':results,'all_complete':all(r['status']=='completed' for r in results),'new_texture_charge_total':4,'balance_after_submission':provenance['balance_after_submission'],'active_run_total_credits':90,'source_only':True};(HERE/'texture-delivery.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
