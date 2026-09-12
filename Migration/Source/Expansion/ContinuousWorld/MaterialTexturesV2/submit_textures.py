"""Submit exactly two authorized new 2K Higgsfield material albedos; no Art writes."""
from pathlib import Path
import subprocess,json
from datetime import datetime,timezone
HERE=Path(__file__).resolve().parent
def cli(*args):
    p=subprocess.run(['higgsfield.cmd',*args,'--json'],capture_output=True,text=True,encoding='utf-8',timeout=60)
    if p.returncode:raise RuntimeError('CLI error '+str(p.returncode))
    return json.loads(p.stdout)
prompts={
'PackedAlpineSnow': 'Production game material: one seamless tileable 2048 square PBR base-color ALBEDO of densely packed alpine snow, a continuous snow surface viewed flat orthographically from directly above, covering about 2 metres square. The snow has been broadly compressed and churned by use but has NO recognizable footprints, boot tread, tracks or grooves. Clearly resolved fine irregular hard snow granules and crushed crystals, small compacted clods, a few denser icy granular patches, irregular subtly compressed areas. Materially coarser and more granular than smooth fresh powder, while still unmistakably near-white snow. Restrained pale icy gray-blue compression among neutral off-white grains; very subtle low-frequency variation. Sharp physically plausible millimetre grain and crushed crystalline texture at every part of the image, not blurred cloud noise or cotton. Perfectly even diffuse unlit albedo capture: NO cast shadows, directional illumination, highlights, sparkles, reflections, ambient occlusion, vignette or lighting gradient. No scene, perspective, horizon, rocks, dirt, plants, liquid puddles, snow dunes, text or borders. All four edges repeat seamlessly with uniform exposure; no grid or visible seams. Output the material texture itself, edge-to-edge, not a render of a material sample.',
'WetAbbeyLimestone': 'Production game material: one seamless tileable 2048 square PBR base-color ALBEDO of rain-wet weathered blue-gray limestone from a ruined Gothic abbey floor. One continuous stone surface fills the frame, a flat orthographic top-down material scan covering about 1 metre square, WITHOUT any slab perimeter, tile grid, mortar joint or paving layout. Cool medium-light slate-blue gray mineral body, tiny irregular pores and pinprick pits, occasional very narrow short hairline fractures, finely worn pale limestone grains and subtle old abrasion. Saturated by rain so the mineral color is slightly deeper and cooler than dry limestone, but this image is ALBEDO ONLY: no glossy reflections, specular highlights, water glints, puddles, rivulets, drops, wet shine, directional light, shadows, ambient occlusion, black crevices, bright bevels or baked depth lighting. Detailed and convincing fine-grained weathered stone, restrained broad mottling, no large dark veins, no dramatic cracks, no moss, no grass, no sediment streaks, no dirt blobs. Uniform neutral diffuse illumination and edge-to-edge material density; all four edges repeat seamlessly. No perspective, scene, text, borders, tiles, grid or sample sphere. Return only the physically plausible color texture.'
}
before=cli('account','status').get('credits');report=json.loads((HERE/'submission-provenance.json').read_text()) if (HERE/'submission-provenance.json').exists() else {'created_at_utc':datetime.now(timezone.utc).isoformat(),'model':'nano_banana_pro','resolution':'2k','aspect_ratio':'1:1','balance_before':before,'jobs':[],'method':'Installed Higgsfield CLI explicitly requested; two new original albedos, no input upload, no image editing.'}
for name,prompt in prompts.items():
    # Avoid accidental rerun spending. Existing job files must be continued with poll_textures.py.
    jobfile=HERE/(name+'-job.json')
    if jobfile.exists():
        print('REUSE_EXISTING_JOB',name,json.loads(jobfile.read_text())['id']);continue
    created=cli('generate','create','nano_banana_pro','--prompt',prompt,'--aspect-ratio','1:1','--resolution','2k')
    if isinstance(created,list):created=created[0]
    if isinstance(created,str):created=cli('generate','get',created)
    jid=created.get('id')
    if not jid:raise RuntimeError('Creation returned no job id')
    jobfile.write_text(json.dumps(created,indent=2),encoding='utf-8');(HERE/(name+'-prompt.txt')).write_text(prompt,encoding='utf-8')
    fresh=cli('generate','get',jid);jobfile.write_text(json.dumps(fresh,indent=2),encoding='utf-8');ledger=cli('account','transactions','--size','1');rows=[]
    for row in ledger.get('items',[]):
        delta=abs((datetime.fromisoformat(row['created_at'].replace('Z','+00:00'))-datetime.fromisoformat(fresh['created_at'].replace('Z','+00:00'))).total_seconds())
        if delta<2 and row.get('action')=='spend':rows.append({k:row.get(k) for k in ('created_at','display_name','action','credits')})
    item={'name':name,'id':jid,'created_at':fresh.get('created_at'),'status':fresh.get('status'),'prompt_file':name+'-prompt.txt','job_file':name+'-job.json','matched_latest_transaction':rows,'charge_credits':-rows[0]['credits'] if len(rows)==1 else None}
    report['jobs'].append(item);(HERE/'submission-provenance.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(name,jid,fresh.get('status'),'cost',item['charge_credits'])
report['balance_after_submission']=cli('account','status').get('credits');report['known_charge_total']=sum(j['charge_credits'] for j in report['jobs'] if j['charge_credits'] is not None);report['attribution_limit']='Exact ledger charges; job linkage uses the latest transaction queried after each separate submission and before the next submission, plus matching timestamps. Ledger has no explicit job ID.'
(HERE/'submission-provenance.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print('BALANCE',report['balance_before'],report['balance_after_submission'])
