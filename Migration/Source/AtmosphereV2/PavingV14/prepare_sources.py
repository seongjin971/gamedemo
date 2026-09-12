"""Historical initial scaffolding; no Blender, map read or mesh export.
Do not rerun in the delivered folder: canonical builder/QA received subsequent
residual-conditioning and precision fixes. Use build_hybrid_v14.py to rebuild.
"""
from pathlib import Path
OUT=Path(__file__).resolve().parent;V13=OUT.parent/'PavingV13'
(OUT/'source_seeds.json').write_bytes((V13/'source_seeds.json').read_bytes())
s=(V13/'build_hybrid_v13.py').read_text()
s=s.replace('V13','V14').replace('v13','v14').replace('130045','140047')
s=s.replace("OUT.parent/'PavingV12/paving-v12-mesh.json'", "OUT.parent/'PavingV13/paving-v13-mesh.json'")
s=s.replace('(9.2,4.6)','(12.4,6.2)').replace('[9.2,4.6]','[12.4,6.2]').replace('/9.2','/12.4').replace('/4.6','/6.2')
s=s.replace('assert len(selected)>300,len(selected)', 'assert 450<=len(selected)<=550,len(selected)')
s=s.replace("assert len(indices)//3<160000", "assert len(indices)//3<=141000")
s=s.replace("depth=(.013+.006*(.5+.5*math.sin(j/n*math.tau+i))) if subordinate else (.021+.009*(.5+.5*math.sin(j/n*math.tau+i)))", "depth=.75*((.013+.006*(.5+.5*math.sin(j/n*math.tau+i))) if subordinate else (.021+.009*(.5+.5*math.sin(j/n*math.tau+i))))")
s=s.replace("ob=make_object(f'HeroScanSlab_{i:02d}_{s[\"template\"][\"id\"]}',verts,faces);me=ob.data", """ob=make_object(f'HeroScanSlab_{i:02d}_{s["template"]["id"]}',verts,faces);me=ob.data
 capattr=me.attributes.new(name='cap_surface',type='INT',domain='FACE')
 for k in range(2*n,2*n+len(captris)*3):capattr.data[k].value=1""")
s=s.replace("for face in me.polygons:face.use_smooth=False\n objects.append(ob)", """# Smooth only the cap's internal triangulation, within this body. The
 # explicit face attribute survives bmesh triangulation; bevels, sides and
 # bottom retain independent flat loop normals at the cap boundary.
 capattr=me.attributes['cap_surface'];capfaces=[f for f in me.polygons if capattr.data[f.index].value==1]
 assert len(capfaces)==len(captris)*3,('cap marker propagation failed',ob.name)
 for face in me.polygons:face.use_smooth=False
 me.update();custom=[tuple(c.vector) for c in me.corner_normals]
 sums=np.zeros((len(me.vertices),3),dtype=float)
 for face in capfaces:
  aa,bb,cc=[me.vertices[k].co for k in face.vertices];cr=np.array((bb-aa).cross(cc-aa))
  for k in face.vertices:sums[k]+=cr
 for face in capfaces:
  face.use_smooth=True
  for li in face.loop_indices:
   k=me.loops[li].vertex_index;no=sums[k]/np.linalg.norm(sums[k]);custom[li]=tuple(no)
 me.normals_split_custom_set(custom);me.update()
 smoothing_report={'cap_faces':len(capfaces),'method':'per-body cap-only area-weighted geometry normals; hard perimeter/bevel/sides','cap_face_marker':'cap_surface'}
 objects.append(ob)""")
s=s.replace("'source_id':s['template']['id'],", "'source_id':s['template']['id'],'subordinate':subordinate,'cap_smoothing':smoothing_report,")
s=s.replace("report={'hero_stones'", "report={'period_m':[12.4,6.2],'source_nominal_period_m':[2.3,1.15],'additional_art_scale_from_v13':12.4/9.2,'total_art_scale_from_source':12.4/2.3,'shoulder_drop_scale_from_v13':.75,'hero_stones'")
s=s.replace("'BEFORE V12 preserved'", "'BEFORE V13 preserved'").replace('before-v12-neutral','before-v13-neutral')
s=s.replace("for face in oldob.data.polygons:face.use_smooth=True", """for face in oldob.data.polygons:face.use_smooth=True
oldnorm=np.array(prior['normals']).reshape(-1,3);oldob.data.normals_split_custom_set_from_vertices(np.stack((oldnorm[:,0],-oldnorm[:,2],oldnorm[:,1]),1).tolist())""")
s=s.replace("'height_note':'Source40mm", "'height_note':'Photographed horizontal period enlarged with aligned UV/height; additional art scale, not source metric dimensions. Source40mm")
(OUT/'build_hybrid_v14.py').write_text(s)
v=(V13/'validate_hybrid.py').read_text().replace('v13','v14').replace('/9.2','/12.4').replace('/4.6','/6.2')
v=v.replace("qa['triangles']<160000", "qa['triangles']<=141000").replace("qa['hero_count']>300", "450<=qa['hero_count']<=550")
(OUT/'validate_hybrid.py').write_text(v)
r=(V13/'render_previews.py').read_text().replace('V13','V14').replace('v13','v14').replace('BEFORE V12 preserved','BEFORE V13 preserved').replace('before-v12-neutral','before-v13-neutral')
(OUT/'render_previews.py').write_text(r)
print('PavingV14 code and seed prepared only')
