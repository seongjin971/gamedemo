from pathlib import Path
from PIL import Image
import json,hashlib
SOURCE=Path(__file__).resolve().parent;ROOT=SOURCE.parents[5];results={}
for path in SOURCE.glob('*coverage-mask.png'):
    im=Image.open(path).convert('RGBA');white=green=0
    for r,g,b,a in im.getdata():
        if a<128:continue
        if min(r,g,b)>127:white+=1
        elif g>127 and r<128 and b<128:green+=1
    results[path.name]={'visible_snow_pixels':white,'visible_tree_pixels':green,'projected_snow_fraction':white/(white+green),'image_size':list(im.size),'camera':'Unity default angle .46 radians / elevation .72 radians, root yaw 0' if 'actual-angle' in path.name else 'Inspection camera source (12,-16,17.6) looking at (0,0,4.3)','method':'Opaque-enough foreground pixels (alpha>=128), white emission snow vs green emission tree. Antialiased boundary pixels use a 127 channel threshold. Controlled single view; no claim of all-angle coverage.'}
for path in SOURCE.glob('*-manifest.json'):
    m=json.loads(path.read_text());pair=ROOT/'Unity/Vesper/Assets/Vesper/Expansion/ContinuousWorld/Art/EnvironmentKit/FoliageFir'/(m['paired_model']+'.fbx');assert hashlib.sha256(pair.read_bytes()).hexdigest()==m['paired_fbx_sha256']
result={'coverage':results,'paired_original_fbx_hashes_unchanged':True,'camera':{'position_source_xyz':[12,-16,17.6],'look_at_source_xyz':[0,0,4.3],'orthographic_scale':11},'original_v1_coverage':'Not measured by this script; V1 geometric selection was 33 sprays.'}
(SOURCE/'coverage-audit.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
