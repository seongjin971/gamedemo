"""Copy reviewed originals and provenance into the explicitly opened new Art folder."""
from pathlib import Path
import json,hashlib,shutil
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[4];STAGED=HERE/'staged';ART=ROOT/'Unity/Vesper/Assets/Vesper/Expansion/ContinuousWorld/Art/Textures/MaterialTexturesV2'
manifest=json.loads((HERE/'texture-delivery.json').read_text());assert manifest['all_complete'];manifest['usage']='sRGB albedo, repeat wrap, full0..1 UV (not atlas quadrant). Parent binds selective packed route / abbey flooring.';manifest['quality_notes']={'PackedAlpineSnow':'Strong crushed granular contrast; some larger snow clods. No recognizable footprints or tracks.','WetAbbeyLimestone':'Cool blue-gray pits/fractures; no tile border or baked puddles. Repeated half-frame motif exists in the original.','tiling':'Prompted seamless repeat; edge statistics documented separately, not mathematically exact edge matching.'};manifest['source_only']=False;manifest['review']='Root visually reviewed both original PNGs and explicitly opened import window before copying.'
provenance=json.loads((HERE/'submission-provenance.json').read_text());provenance['active_run_credits_after_this_batch']=90
for j in provenance['jobs']:
    j['prompt']=(HERE/j['prompt_file']).read_text();j['status']=json.loads((HERE/j['job_file']).read_text())['status'];j['source_original_job_metadata']=str((HERE/j['job_file']).relative_to(ROOT)).replace('\\','/')
(STAGED/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8');(STAGED/'provenance.json').write_text(json.dumps(provenance,indent=2),encoding='utf-8');ART.mkdir(parents=True,exist_ok=True)
checks=[]
for name in ('PackedAlpineSnow.png','WetAbbeyLimestone.png','manifest.json','provenance.json'):
    source=STAGED/name;target=ART/name;expected=hashlib.sha256(source.read_bytes()).hexdigest()
    if target.exists():assert hashlib.sha256(target.read_bytes()).hexdigest()==expected,'Existing differing new-target file cannot be overwritten'
    else:shutil.copyfile(source,target)
    got=hashlib.sha256(target.read_bytes()).hexdigest();assert got==expected;checks.append({'file':name,'destination':str(target),'sha256':got,'stage_matches_art':True})
(HERE/'art-copy-audit.json').write_text(json.dumps(checks,indent=2));print(json.dumps(checks,indent=2))
