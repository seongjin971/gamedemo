"""Recover returned first job after CLI returned a list; never resubmit it."""
from pathlib import Path
import ast,json,subprocess,sys
from datetime import datetime,timezone
HERE=Path(__file__).resolve().parent;tree=ast.parse((HERE/'submit_textures.py').read_text());prompts=next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='prompts' for t in n.targets))
def cli(*args):
    p=subprocess.run(['higgsfield.cmd',*args,'--json'],capture_output=True,text=True,encoding='utf-8',timeout=60);assert p.returncode==0;return json.loads(p.stdout)
name=sys.argv[1] if len(sys.argv)>1 else 'PackedAlpineSnow';recent=cli('generate','list','--image','--size','1');rows=recent if isinstance(recent,list) else recent['items'];assert len(rows)==1;job=rows[0];job=cli('generate','get',job['id']);assert job['params']['prompt']==prompts[name]
(HERE/(name+'-job.json')).write_text(json.dumps(job,indent=2));(HERE/(name+'-prompt.txt')).write_text(prompts[name]);ledger=cli('account','transactions','--size','1');row=ledger['items'][0];assert row['action']=='spend' and row['credits']==-2
delta=abs((datetime.fromisoformat(row['created_at'].replace('Z','+00:00'))-datetime.fromisoformat(job['created_at'].replace('Z','+00:00'))).total_seconds());assert delta<2
selected={k:row.get(k) for k in ('created_at','display_name','action','credits')};balance=cli('account','status')['credits']
item={'name':name,'id':job['id'],'created_at':job['created_at'],'status':job['status'],'prompt_file':name+'-prompt.txt','job_file':name+'-job.json','matched_latest_transaction':[selected],'charge_credits':2}
if (HERE/'submission-provenance.json').exists():
    report=json.loads((HERE/'submission-provenance.json').read_text());assert all(j['id']!=job['id'] for j in report['jobs']);report['jobs'].append(item)
else:report={'created_at_utc':job['created_at'],'model':'nano_banana_pro','resolution':'2k','aspect_ratio':'1:1','balance_before':balance+2,'balance_before_basis':'Recovered current balance plus exactly matched first submission charge; prior audited balance was2440.','jobs':[item],'method':'Installed Higgsfield CLI. Create returns a list of job-ID strings; existing jobs recovered by exact full-prompt comparison, never resubmitted.'}
(HERE/'submission-provenance.json').write_text(json.dumps(report,indent=2));print('RECOVERED_EXISTING',job['id'],job['status'],'charge2','balance',balance)
