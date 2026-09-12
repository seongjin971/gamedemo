from pathlib import Path
import json
from PIL import Image,ImageDraw
SOURCE=Path(__file__).resolve().parent;camera=json.loads((SOURCE/'structural-camera-comparison.json').read_text());region=Image.new('L',(1536,1024),0);ImageDraw.Draw(region).polygon([tuple(p) for p in camera['near_facade_projection_quad_pixels']],fill=255)
rp=region.load();data={}
for label in ('v2','v3'):
    im=Image.open(SOURCE/('structural-'+label+'-geometry-alpha.png')).convert('RGBA');px=im.load();count=clear=opaque=0;coords=[]
    for y in range(im.height):
        for x in range(im.width):
            if rp[x,y]:
                count+=1
                if px[x,y][3]<128:clear+=1;coords.append((x,y))
                else:opaque+=1
    data[label]={'near_facade_pixels':count,'camera_visible_open_pixels':clear,'opaque_pixels':opaque,'open_fraction_of_near_facade':clear/count,'open_fraction_of_entire_frame':clear/(1536*1024),'open_pixel_bounds':[[min(x for x,y in coords),min(y for x,y in coords)],[max(x for x,y in coords),max(y for x,y in coords)]]}
report={'method':'Camera-ray visibility from rendered geometry alpha, alpha<128 inside the identical projected near facade rectangle: source X=3.25, length -7..7, world up -0.95..2.8. Includes occlusion by the entire actual bridge. This is visible open silhouette above water, not a horizontal ray test or only analytic ellipse area. Antialiased perimeter pixels can contribute less than one pixel of boundary error.','comparison':data,'visible_open_pixel_ratio_v3_over_v2':data['v3']['camera_visible_open_pixels']/data['v2']['camera_visible_open_pixels'],'visible_open_pixel_increase_percent':100*(data['v3']['camera_visible_open_pixels']/data['v2']['camera_visible_open_pixels']-1),'camera_manifest':'structural-camera-comparison.json','visual_assessment':'Paired raised-water previews show a broader continuous curved opening and narrower piers in V3, with the same upper deck and parapets. Controlled geometry improvement; no independent Unity water-gate score or full-scene acceptance claimed.'}
(SOURCE/'structural-opening-visibility.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
