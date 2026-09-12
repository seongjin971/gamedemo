"""Historical initial scaffolding, superseded by build_hybrid_v13.py refinements.
Do not rerun against the delivered folder: it would replace the canonical builder.
The current source_seeds.json and build_hybrid_v13.py are the build inputs.
"""
from pathlib import Path
import json
OUT=Path(__file__).resolve().parent
p=OUT/'source_seeds.json';j=json.loads(p.read_text())
extra={
'upper_small_wedge':[[579,4],[648,3],[635,68],[575,109]],
'upper_mid_triangle':[[743,84],[814,76],[825,167],[787,160],[759,130]],
'upper_top_midright':[[1168,0],[1323,0],[1314,55],[1259,82],[1162,48]],
'upper_right_diagonal':[[1639,7],[1775,0],[1792,60],[1757,118],[1666,142],[1608,182],[1599,159],[1629,119],[1639,77]],
'upper_right_lowerwedge':[[1651,227],[1729,190],[1739,229],[1747,275],[1620,274]],
'upper_soil_neighbor':[[454,166],[509,158],[554,169],[558,209],[534,229],[487,223]],
'upper_organic_neighbor':[[582,173],[631,166],[674,180],[672,213],[640,247],[603,241],[568,215]],
'middle_edge_wedge':[[2011,292],[2048,291],[2048,384],[2019,352]],
'middle_upper_rightrect':[[1717,290],[1853,290],[1834,339],[1798,378],[1720,385]],
'middle_center_square':[[1127,302],[1207,292],[1216,373],[1187,389],[1138,366],[1113,350]],
'middle_center_lowrect':[[1124,395],[1190,399],[1220,420],[1214,492],[1190,520],[1140,520],[1135,471],[1112,438]],
'middle_low_wedge':[[1264,422],[1286,438],[1301,488],[1265,517],[1230,520],[1230,472]],
'middle_narrow_tall':[[825,415],[888,408],[900,432],[900,519],[838,520],[828,484]],
'middle_low_lefttri':[[763,432],[809,417],[819,467],[797,519],[723,516],[720,494]],
'middle_organic_right':[[651,379],[681,369],[706,388],[718,446],[704,469],[639,469],[616,455]],
'middle_organic_left':[[503,390],[569,379],[585,405],[611,443],[575,476],[529,469],[482,435]],
'middle_small_upper':[[491,295],[532,292],[555,309],[568,363],[521,379],[482,371]],
'lower_left_fragment':[[365,548],[426,540],[475,552],[493,579],[462,601],[431,641],[374,614],[356,587]],
'lower_narrow_course_left':[[697,547],[786,540],[824,564],[818,589],[708,585]],
'lower_narrow_course_mid':[[999,541],[1087,541],[1120,566],[1129,591],[997,589]],
'lower_narrow_course_right':[[1237,539],[1349,540],[1355,564],[1345,588],[1206,589],[1219,569]],
'lower_narrow_course_far':[[1382,541],[1518,539],[1525,565],[1520,587],[1369,590]],
'lower_left_lowtriangle':[[53,751],[103,724],[152,740],[170,806],[132,822],[71,816],[22,793]],
'lower_left_lowsquare':[[224,739],[307,738],[323,768],[333,813],[319,824],[205,822],[190,798]],
'bottom_left_lowpiece':[[68,950],[145,944],[163,974],[161,1024],[89,1024],[74,994]],
'bottom_small_middle':[[672,843],[758,845],[779,869],[774,930],[688,925],[663,901]],
'bottom_edge_right':[[1973,832],[2048,834],[2048,1024],[1979,1024],[1991,970],[1978,903]],
'bottom_right_mid':[[1756,853],[1834,849],[1866,889],[1808,921],[1770,916]],
'bottom_right_low':[[1775,938],[1837,923],[1870,946],[1883,980],[1858,1018],[1771,1018]],
'bottom_left_mid':[[259,858],[332,854],[343,885],[337,916],[250,918],[243,895]],
'upper_small_farleft':[[417,208],[449,215],[441,269],[412,273]],
'upper_soil_bottom':[[678,219],[710,205],[739,224],[755,267],[700,284],[646,276]],
'upper_tiny_right':[[778,225],[814,227],[818,271],[775,272]],
'upper_soil_top':[[687,1],[735,1],[745,48],[719,81],[684,55]],
'upper_soil_side':[[782,181],[816,190],[814,215],[763,202]],
'middle_organic_top':[[585,299],[623,285],[658,300],[685,327],[654,365],[611,378],[573,352]],
'middle_organic_bottom':[[726,374],[748,380],[764,402],[747,437],[724,440]],
'middle_right_narrow':[[1238,294],[1282,292],[1319,313],[1299,355],[1250,359],[1228,344]],
'middle_lower_small':[[475,461],[499,474],[521,505],[514,522],[467,522]],
'lower_left_edge_upper':[[0,535],[21,537],[51,579],[49,613],[0,615]],
'lower_left_edge_lower':[[0,632],[50,630],[50,683],[39,711],[0,717]],
'lower_left_center_wedge':[[381,662],[414,661],[444,690],[448,737],[421,737],[391,720],[355,716]],
'lower_left_center_low':[[444,750],[477,762],[482,816],[404,819],[391,795]],
'lower_middle_smalltop':[[553,540],[585,549],[611,581],[527,590]],
'lower_right_edge_large':[[2006,562],[2048,551],[2048,803],[2001,799],[1977,766],[1985,718],[1958,690],[1984,632]],
'lower_right_edge_low':[[1937,748],[1959,754],[1990,814],[1957,827],[1933,811]],
'bottom_left_edge':[[0,949],[44,949],[62,987],[62,1024],[0,1024]],
'bottom_left_lowmiddle':[[187,947],[237,944],[259,980],[257,1018],[185,1018]],
'bottom_left_lowsquare':[[275,938],[335,934],[346,971],[330,1018],[282,1018],[265,984]],
'bottom_center_lowleft':[[674,946],[730,945],[787,960],[797,1018],[706,1018],[665,985]],
'bottom_right_narrow':[[1670,893],[1719,870],[1746,900],[1727,944],[1753,976],[1746,1018],[1643,1018],[1641,980]],
'bottom_right_largestedge':[[1886,934],[1920,922],[1958,938],[1973,985],[1952,1024],[1903,1024]]
}
j['slabs']=[s for s in j['slabs'] if not s.get('subordinate')]
j['slabs'] += [{'id':k,'polygon':v,'subordinate':True} for k,v in extra.items()]
j['method']+=' Forty dominant contours plus subordinate neighboring stones cover actual source stone area; the added count is documented rather than merging unrelated photo stones.'
p.write_text(json.dumps(j,indent=2))
s=(OUT.parent/'PavingV12/build_hybrid_v12.py').read_text()
s=s.replace('V12','V13').replace('v12','v13').replace('120041','130045')
s=s.replace("prior=json.loads((V11/'paving-v11-mesh.json').read_text())", "prior=json.loads((OUT.parent/'PavingV12/paving-v12-mesh.json').read_text())")
s=s.replace("sourcepaths=[V11/'paving-v11-mesh.json'", "sourcepaths=[OUT.parent/'PavingV12/paving-v12-mesh.json',V11/'paving-v11-mesh.json'")
s=s.replace('math.ceil(np.linalg.norm(edge)/.075)','math.ceil(np.linalg.norm(edge)/.19)')
a=s.index('# Actual native home camera');b=s.index('\ndef make_mat',a)
s=s[:a]+'''# Full foreground coverage, exact rectangular clip; rear masked bed preserved.
def clip(poly,axis,value,sign):
 out=[]
 for a,b in zip(poly,np.roll(poly,-1,axis=0)):
  ia=sign*(a[axis]-value)>=-1e-10;ib=sign*(b[axis]-value)>=-1e-10
  if ia:out.append(a)
  if ia!=ib:out.append(a+(b-a)*(value-a[axis])/(b[axis]-a[axis]))
 return np.array(out)
def area(poly):
 return abs(sum(np.cross(a,b) for a,b in zip(poly,np.roll(poly,-1,axis=0))))*.5 if len(poly)>2 else 0
def kernel_center(poly):
 # Kernel intersection guarantees radial cap rings lie inside a concave outline.
 ker=np.array([[-100.,-100.],[100.,-100.],[100.,100.],[-100.,100.]])
 for a,b in zip(poly,np.roll(poly,-1,axis=0)):
  out=[];edge=b-a
  for c,d in zip(ker,np.roll(ker,-1,axis=0)):
   fc=np.cross(edge,c-a);fd=np.cross(edge,d-a);ic=fc>=-1e-9;idd=fd>=-1e-9
   if ic:out.append(c)
   if ic!=idd:out.append(c+(d-c)*fc/(fc-fd))
  ker=np.array(out)
  if len(ker)<3:return None
 return ker.mean(0)
def triangulate(poly):
 # Ear clipping only for non-star-shaped photo outlines; each resulting polygon
 # receives the same source id/plane, so no artificial inter-fragment crack.
 ids=list(range(len(poly)));out=[]
 while len(ids)>3:
  found=False
  for j in range(len(ids)):
   a,b,c=ids[j-1],ids[j],ids[(j+1)%len(ids)];pa,pb,pc=poly[[a,b,c]]
   if np.cross(pb-pa,pc-pb)<=1e-9:continue
   if any(inside(np.array([poly[k,0]]),np.array([poly[k,1]]),np.array([pa,pb,pc]))[0] for k in ids if k not in (a,b,c)):continue
   out.append(poly[[a,b,c]]);ids.pop(j);found=True;break
  assert found,'invalid source polygon'
 out.append(poly[ids]);return out
a=.46;e=.72
selected=[];skipped=[]
for tx in (-1,0):
 for tz in range(-1,5):
  for t in templates:
   shift=np.array([tx*PERIOD[0],tz*PERIOD[1]]);poly=t['poly']+shift
   for axis,value,sign in [(0,bounds[0][0],1),(0,bounds[1][0],-1),(1,rects[0][2],1),(1,bounds[1][2],-1)]:
    if len(poly)<3:break
    poly=clip(poly,axis,value,sign)
   if area(poly)<.035:continue
   # Retain one actual source unit, not an ear-clipped collection of slabs.
   center=kernel_center(poly)
   if center is None:
    skipped.append({'id':t['id'],'area':area(poly),'reason':'empty visibility kernel'});continue
   selected.append({'template':t,'shift':shift,'poly':poly,'center':center,'screen':None,'area':area(poly)})
assert len(selected)>300,len(selected)
''' +s[b:]
s=s.replace("if i%3==0:scale=np.array([1.0 if i%2 else .84,.82 if i%2 else 1.0])", "# No local shrink: adjacent source stones remain in their original positions.")
s=s.replace("level=[-.027,-.018,-.012,-.003,.003,-.009][i%6]", "level=[-.022,-.016,-.009,-.003,.002,-.010][i%6]")
s=s.replace('width=.065+.040*(.5+.5*math.sin(j/n*math.tau*2+i))', 'width=min(np.linalg.norm(center-p)*.22,.045+.035*(.5+.5*math.sin(j/n*math.tau*2+i)))')
s=s.replace('for fraction in (.68,.34):','for fraction in (.48,):').replace('for ring in (2,3):','for ring in (2,):').replace('faces.append((4*n+j,4*n+(j+1)%n,topcenter))','faces.append((3*n+j,3*n+(j+1)%n,topcenter))')
s=s.replace('step=.145;', 'step=.205;')
s=s.replace("'hero_count':len(stone_reports),", "'hero_count':len(stone_reports),'source_contour_count':len(templates),'skipped_contours':skipped,'foreground_body_area_m2':sum(s['area'] for s in selected),'foreground_area_m2':(rects[0][1]-rects[0][0])*(rects[0][3]-rects[0][2]),")
s=s.replace("'BEFORE V11 preserved'", "'BEFORE V12 preserved'").replace('before-v11-neutral','before-v12-neutral')
s=s.replace('scene.cycles.samples=24','scene.cycles.samples=16')
s=s.replace("'native-ground',(0,-.7,2.9),33.3070866", "'native-ground',(0,-.7,2.9),33.3070866")
s=s.replace('"""V13 source-matched 24 physical slabs over a captured stonebed.', '"""V13 contiguous source-matched foreground slabs over a captured stonebed.')
(OUT/'build_hybrid_v13.py').write_text(s)
v=(OUT.parent/'PavingV12/validate_hybrid.py').read_text().replace('v12','v13').replace("qa['hero_count']==24", "qa['hero_count']>300")
(OUT/'validate_hybrid.py').write_text(v)
area=lambda q:abs(sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(q,q[1:]+q[:1])))/2
print('SOURCE_CONTOURS',len(j['slabs']),'SOURCE_FOOTPRINT_RATIO',sum(area(g['polygon']) for g in j['slabs'])/(2048*1024))
