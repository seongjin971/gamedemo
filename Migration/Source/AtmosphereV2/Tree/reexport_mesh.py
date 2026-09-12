import bpy,json,math
from pathlib import Path
work=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(work/'tree-v7.blend'))
mesh=bpy.data.objects['Sculpted bark roots and fine branches'].data
mesh.calc_loop_triangles()
positions=[];normals=[];uv=[];indices=[];lookup={}
for tri in mesh.loop_triangles:
    for li in (tri.loops[0],tri.loops[2],tri.loops[1]):
        p=mesh.vertices[mesh.loops[li].vertex_index].co;n=mesh.corner_normals[li].vector
        pos=(-p.x,p.z,-p.y);norm=(-n.x,n.z,-n.y);tex=tuple(mesh.uv_layers.active.data[li].uv)
        key=pos+norm+tex
        if key not in lookup:
            lookup[key]=len(positions)//3;positions.extend(pos);normals.extend(norm);uv.extend(tex)
        indices.append(lookup[key])
assert all(math.isfinite(x) for x in positions+normals+uv)
(work/'tree-v7-mesh.json').write_text(json.dumps({'positions':positions,'normals':normals,'uv':uv,'indices':indices},separators=(',',':')))
report=json.loads((work/'tree-v7-report.json').read_text())
report.update(export_vertices=len(positions)//3,indices=len(indices),coordinate_conversion='Blender (x,y,z) to Unity (-x,z,-y)',winding='triangle corners [0,2,1], reversed for X reflection',export_deduplication='exact position + corner normal + UV tuple; seams preserved')
(work/'tree-v7-report.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report))
