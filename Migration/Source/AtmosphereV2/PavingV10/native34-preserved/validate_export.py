"""Compare native winding against actual working sources, independent of Blender.
python validate_export.py [--compare-rejected]
"""
import json,math,hashlib,sys
from pathlib import Path
OUT=Path(__file__).resolve().parent
ROOT=next(p for p in OUT.parents if (p/'ArtSource').is_dir())

def inspect(path):
    data=json.loads(path.read_text());p=data['positions'];n=data['normals'];ix=data['indices']
    finite=all(math.isfinite(v) for key in ('positions','normals','uv','colors') for v in data.get(key,[]))
    assert len(n)==len(p) and len(p)%3==0 and len(ix)%3==0
    valid=min(ix)>=0 and max(ix)<len(p)//3
    positive=negative=tangent=degenerate=top_up=top_down=0;minimum_area=float('inf')
    for k in range(0,len(ix),3):
        ids=ix[k:k+3];a,b,c=[p[i*3:i*3+3] for i in ids]
        u=[b[j]-a[j] for j in range(3)];v=[c[j]-a[j] for j in range(3)]
        cross=[u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]]
        length=math.sqrt(sum(x*x for x in cross));minimum_area=min(minimum_area,length*.5)
        if length<1e-10:degenerate+=1;continue
        average=[sum(n[i*3+j] for i in ids)/3 for j in range(3)]
        dot=sum(cross[j]*average[j] for j in range(3))/length
        positive+=dot>1e-7;negative+=dot< -1e-7;tangent+=abs(dot)<=1e-7
        if average[1]>.9:
            top_up+=cross[1]>0;top_down+=cross[1]<=0
    lengths=[math.sqrt(sum(n[k+j]**2 for j in range(3))) for k in range(0,len(n),3)]
    return data,{'path':str(path.relative_to(ROOT)),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
        'triangles':len(ix)//3,'vertices':len(p)//3,'finite':finite,'valid_indices':valid,
        'cross_dot_normal_positive':positive,'cross_dot_normal_negative':negative,'cross_dot_normal_tangent':tangent,
        'degenerate_triangles':degenerate,'minimum_triangle_area':minimum_area,
        'provided_top_normals_positive_y_and_geometric_top_up':top_up,'provided_top_normals_positive_y_but_geometric_top_down':top_down,
        'normal_length_min_max':[min(lengths),max(lengths)]}

data,current=inspect(OUT/'paving-v10-mesh.json')
paths=[ROOT/'Migration/Source/AtmosphereV2/StoneV7/runtime/30387f49-1a6e-42e9-80e4-01b8c8c559c1.json',
       ROOT/'Migration/Source/AtmosphereV2/StoneV7/runtime/740f8589-aea6-4e9f-831f-6adbdb49ada3.json']
tree=ROOT/'Migration/Source/AtmosphereV2/TreeV10/tree-v10-mesh.json'
if tree.exists():paths.append(tree)
references=[inspect(p)[1] for p in paths]
assert all(r['cross_dot_normal_positive']>0 and r['cross_dot_normal_negative']==0 for r in references),references
qa={'contract':'Actual working native StoneV7 (plus TreeV10 when present) uses cross(edge1,edge2) dot supplied normals > 0. The prior negative-dot clockwise check was incorrect and failed actual Unity.',
    'current':current,'actual_working_source_comparison':references,'matches_working_source_sign':current['cross_dot_normal_negative']==0 and current['cross_dot_normal_positive']>0,
    'native_visual_verification':'Pending root Unity reimport/capture; this numeric check does not assert live visibility.'}
if '--compare-rejected' in sys.argv:
    rejected,old=inspect(OUT/'rejected-winding/paving-v10-mesh.json')
    preserved={key:data[key]==rejected[key] for key in ('positions','normals','uv','colors')}
    exactly_once=all(data['indices'][k:k+3]==[rejected['indices'][k],rejected['indices'][k+2],rejected['indices'][k+1]] for k in range(0,len(data['indices']),3))
    qa.update({'rejected_winding':old,'non_index_arrays_identical':preserved,'each_triangle_reversed_exactly_once':exactly_once})
    assert all(preserved.values()) and exactly_once
assert current['finite'] and current['valid_indices'] and current['degenerate_triangles']==0
assert current['cross_dot_normal_positive']==current['triangles'] and current['cross_dot_normal_negative']==0 and current['cross_dot_normal_tangent']==0
assert current['provided_top_normals_positive_y_and_geometric_top_up']>0 and current['provided_top_normals_positive_y_but_geometric_top_down']==0
(OUT/'export-qa.json').write_text(json.dumps(qa,indent=2))
print(json.dumps(qa,indent=2))
