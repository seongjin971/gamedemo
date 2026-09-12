"""Copy approved P1 derivative and pack PBR channels for URP. Meta uses Unity API."""
from pathlib import Path
from PIL import Image, ImageOps
import shutil, hashlib, json
ROOT=Path(__file__).resolve().parent
OUT=ROOT.parents[3]/'Unity/Vesper/Assets/Vesper/Expansion/P1/Art'
OUT.mkdir(parents=True,exist_ok=True)
shutil.copy2(ROOT/'prepared-v3/Adventurer.fbx',OUT/'Adventurer.fbx')
shutil.copy2(ROOT/'texture-0-base_color.png',OUT/'Albedo.png')
shutil.copy2(ROOT/'texture-0-normal.png',OUT/'Normal.png')
rough=Image.open(ROOT/'texture-0-roughness.png').convert('L')
metal=Image.open(ROOT/'texture-0-metallic.png').convert('L').resize(rough.size)
zero=Image.new('L',rough.size,0)
Image.merge('RGBA',(metal,zero,zero,ImageOps.invert(rough))).save(OUT/'MetallicSmoothness.png')
data=[{'file':p.name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size} for p in OUT.iterdir() if p.is_file() and p.suffix!='.meta']
(ROOT/'unity-art-manifest.json').write_text(json.dumps(data,indent=2),encoding='utf-8')
print(json.dumps(data))
