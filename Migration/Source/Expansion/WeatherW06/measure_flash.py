from pathlib import Path
import json
from PIL import Image,ImageStat,ImageChops
ROOT=Path(__file__).resolve().parents[4]
E=ROOT/'Migration/Evidence/Expansion/WeatherWorld/W06'
def luma(name):
    return Image.open(E/'capture'/name).convert('RGB').convert('L',(.2126,.7152,.0722,0))
base=luma('weather-198.png')
after=luma('abbey-after-flash.png')
w,h=base.size
regions={'upperLeft':(0,40,w//2,h//2),'upperRight':(w//2,40,w,h//2),'lowerLeft':(0,h//2,w//2,h-40),'lowerRight':(w//2,h//2,w,h-40)}
def mean(im,box):return ImageStat.Stat(im.crop(box)).mean[0]/255
r={'note':'Mean gamma-encoded image luminance, excluding HUD rows. Spatial coverage diagnostic only, not photometric exposure or temporal smoothness certification. Particle positions vary between frames.','flash':{}}
for image in ['abbey-fullscreen-flash.png','abbey-strong-flash.png']:
    peak=luma(image)
    r['flash'][image]={key:{'before':round(mean(base,s),4),'peak':round(mean(peak,s),4),'ratio':round(mean(peak,s)/mean(base,s),3)} for key,s in regions.items()}
r['afterReturnMeanAbsoluteDifference']=round(ImageStat.Stat(ImageChops.difference(after,base)).mean[0]/255,6)
out=E/'flash-coverage.json'
if out.exists():raise SystemExit('Refuse overwrite')
out.write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
