"""Read-only source energy comparison under the retained flame shader formula."""
import hashlib
import json
from pathlib import Path
from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]

def smooth(a, b, x):
    t = max(0, min(1, (x-a)/(b-a)))
    return t*t*(3-2*t)

def measure(path):
    source = Image.open(path).convert('RGBA')
    sample = source.resize((256, 256), Image.Resampling.BILINEAR)
    linear = [v/255/12.92 if v/255 <= .04045 else ((v/255+.055)/1.055)**2.4 for v in range(256)]
    total = maximum = 0
    direct_total = 0
    luminous = cores = 0
    for red, green, blue, alpha in sample.getdata():
        rgb = [linear[red], linear[green], linear[blue]]
        density = max(rgb)
        core = smooth(.18,.65,rgb[1])*smooth(.5,.95,rgb[0])
        color = [1,.32+core*.5,.075+core*.445]
        radiance = [color[k]*density**1.6*[5.5,5.5,4.5][k]*(alpha/255)*(.25+core*.75)*(1+core*4) for k in range(3)]
        lum = sum(x*y for x,y in zip(radiance,[.2126,.7152,.0722]))
        direct_total += sum(rgb[k]*[5.5,5.5,4.5][k]*(alpha/255)*[.2126,.7152,.0722][k] for k in range(3))
        total += lum
        maximum = max(maximum,lum)
        luminous += lum > .02
        cores += core >= .5
    return {'path':path.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'size':source.size,'meanLinearLuminance':total/65536,'meanDirectSourceLuminance':direct_total/65536,'peakSampleLuminance':maximum,'luminousSamples':luminous,'coreSamples':cores,'note':'256x256 source sample; no camera, warp, depth, fog, RT filtering or tone mapping.'}

if __name__ == '__main__':
    old = measure(ROOT/'Unity/Vesper/Assets/Vesper/Textures/flame-v1.png')
    new = measure(HERE/'flame-v16.png')
    report = {'baseline':old,'candidate':new,'candidateRadianceScaleForEqualSourceMean':old['meanLinearLuminance']/new['meanLinearLuminance'],'directSourceScaleForBaselineMean':old['meanLinearLuminance']/new['meanDirectSourceLuminance']}
    (HERE/'source-energy.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,indent=2))
