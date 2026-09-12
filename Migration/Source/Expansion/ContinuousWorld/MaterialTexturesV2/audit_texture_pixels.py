"""Read-only original PNG pixel statistics. No image edits or derived images."""
from pathlib import Path
from PIL import Image,ImageStat
import math,json,hashlib
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[4];ART=ROOT/'Unity/Vesper/Assets/Vesper/Expansion/ContinuousWorld/Art/Textures'
files={'PackedAlpineSnow':HERE/'staged/PackedAlpineSnow.png','WetAbbeyLimestone':HERE/'staged/WetAbbeyLimestone.png','OriginalSnowSurface':ART/'SnowSurface.png','OriginalLimestoneSurface':ART/'LimestoneSurface.png'}
results={}
def lum(p):return .2126*p[0]+.7152*p[1]+.0722*p[2]
def mae(a,b):return sum(abs(a[i]-b[i]) for i in range(3))/3
for name,path in files.items():
    before=hashlib.sha256(path.read_bytes()).hexdigest();im=Image.open(path).convert('RGBA');px=im.load();w,h=im.size;mean=ImageStat.Stat(im).mean;stdev=ImageStat.Stat(im).stddev;adj=[];hdiff=[]
    for y in range(0,h,8):
        for x in range(0,w-1,8):adj.append(lum(px[x+1,y])-lum(px[x,y]))
        for x in range(0,w//2,8):hdiff.append(mae(px[x,y],px[x+w//2,y]))
    seams_x=[mae(px[0,y],px[w-1,y]) for y in range(h)];seams_y=[mae(px[x,0],px[x,h-1]) for x in range(w)]
    assert before==hashlib.sha256(path.read_bytes()).hexdigest()
    results[name]={'size':[w,h],'mean_rgba':mean,'stdev_rgba':stdev,'alpha_extrema':im.getchannel('A').getextrema(),'one_pixel_luminance_difference_rms':math.sqrt(sum(v*v for v in adj)/len(adj)),'horizontal_opposing_edge_rgb_mae':sum(seams_x)/len(seams_x),'vertical_opposing_edge_rgb_mae':sum(seams_y)/len(seams_y),'horizontal_half_frame_rgb_mae':sum(hdiff)/len(hdiff),'sha256':before,'file_unchanged':True}
report={'results':results,'snow_microcontrast_rms_ratio_new_over_old':results['PackedAlpineSnow']['one_pixel_luminance_difference_rms']/results['OriginalSnowSurface']['one_pixel_luminance_difference_rms'],'scope':'Pixel statistics on original downloaded PNGs and read-only old references; no filtering, recoloring, resampling, normal-map generation or image edits. Metrics do not guarantee seamless visual tiling.','inspection':{'PackedAlpineSnow':'Clearly coarser crushed granular snow with pale blue-gray compacted patches; no recognizable footprints, track paths, grid, rocks or perspective. Some larger angular snow clods are present; visible fine self-contrast is inherent in this generated albedo.','WetAbbeyLimestone':'Cool blue-gray fine limestone with tiny pits and short fractures; no tile borders, puddles, gloss reflections or directional cast shadow. A repeated half-frame motif is perceptible in the generated original; use per-slab rotation/UV offsets already available if repetition becomes visible.','tiling':'Requested seamless repeat in both prompts. Edge statistics are evidence, not a claim of mathematically identical edge pixels or Unity repeat-mode visual acceptance.'}}
(HERE/'texture-pixel-audit.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
