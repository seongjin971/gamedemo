"""Independent exported-data QA, standard Python + Pillow; never runs Blender."""
from pathlib import Path
import json,math,hashlib,collections
from PIL import Image
OUT=Path(__file__).resolve().parent

def orientation(g):
    p=g['positions'];n=g['normals'];ind=g['indices'];positive=negative=degenerate=up=0
    minimum=float('inf');edges=collections.Counter()
    for k in range(0,len(ind),3):
        ids=ind[k:k+3];a,b,c=[p[i*3:i*3+3] for i in ids]
        e=[b[j]-a[j] for j in range(3)];f=[c[j]-a[j] for j in range(3)]
        cross=[e[1]*f[2]-e[2]*f[1],e[2]*f[0]-e[0]*f[2],e[0]*f[1]-e[1]*f[0]]
        ar=math.sqrt(sum(t*t for t in cross))*.5;minimum=min(minimum,ar);degenerate+=ar<1e-12
        dot=sum(cross[j]*sum(n[i*3+j] for i in ids) for j in range(3))
        positive+=dot>0;negative+=dot<0;up+=cross[1]>0
        for i,j in [(ids[0],ids[1]),(ids[1],ids[2]),(ids[2],ids[0])]:edges[tuple(sorted((i,j)))]+=1
    return {'triangles':len(ind)//3,'positive_dot':positive,'negative_dot':negative,'degenerate':degenerate,'top_up_faces':up,'minimum_area':minimum,'boundary_edges':sum(v==1 for v in edges.values()),'nonmanifold_overfull_edges':sum(v>2 for v in edges.values())}

def main():
    g=json.loads((OUT/'paving-v11-mesh.json').read_text());m=json.loads((OUT/'heightfield-metadata.json').read_text());p=g['positions'];n=g['normals'];uv=g['uv']
    qa=orientation(g);count=len(p)//3
    qa['vertices']=count;qa['finite']=all(math.isfinite(x) for key in ['positions','normals','uv','colors'] for x in g[key])
    qa['attribute_lengths_match']=len(n)==count*3 and len(uv)==count*2 and len(g['colors'])==count*4
    qa['indices_in_bounds']=min(g['indices'])>=0 and max(g['indices'])<count
    lengths=[math.sqrt(sum(v*v for v in n[k:k+3])) for k in range(0,len(n),3)]
    qa['normal_length_range']=[min(lengths),max(lengths)]
    qa['all_colors_one']=all(v==1 for v in g['colors'])
    qa['uv_max_error']=max(max(abs(uv[k*2]-p[k*3]/9.2),abs(uv[k*2+1]-p[k*3+2]/4.6)) for k in range(count))
    im=Image.open(OUT/'maps/Tiles130_4K-PNG_Displacement.png');im.load();w,h=im.size
    def pixel(x,y):return im.getpixel((x%w,h-1-(y%h)))/65535.0
    errors=[]
    for k in range(0,count,13):
        x=(uv[k*2]%1)*w-.5;y=(uv[k*2+1]%1)*h-.5;ix=math.floor(x);iy=math.floor(y);fx=x-ix;fy=y-iy
        height=pixel(ix,iy)*(1-fx)*(1-fy)+pixel(ix+1,iy)*fx*(1-fy)+pixel(ix,iy+1)*(1-fx)*fy+pixel(ix+1,iy+1)*fx*fy
        errors.append(abs(p[k*3+1]-(-.0236+.04*(height-1))))
    qa['independent_pillow_height_samples']=len(errors);qa['max_height_sample_error_m']=max(errors)
    bounds=[[min(p[i::3]) for i in range(3)],[max(p[i::3]) for i in range(3)]]
    qa['world_bounds']=bounds;qa['exact_v10_outer_xz_within_1nm']=all(abs(bounds[k][a]-m['v10_world_bounds'][k][a])<1e-9 for k in (0,1) for a in (0,2))
    qa['minimum_water_clearance_m']=-.004-bounds[1][1]
    ref=next(p for p in sorted((OUT.parent/'StoneV7/runtime').glob('*.json')) if 'positions' in json.loads(p.read_text()))
    qa['working_source_comparison']={'path':str(ref),'sha256':hashlib.sha256(ref.read_bytes()).hexdigest(),'orientation':orientation(json.loads(ref.read_text()))}
    manifest=json.loads((OUT/'manifest.json').read_text());qa['downloaded_sources_preserved']=all(hashlib.sha256((OUT/e['path']).read_bytes()).hexdigest()==e['sha256'] for e in manifest['files'])
    qa['v10_preserved']=hashlib.sha256((OUT.parent/'PavingV10/paving-v10-mesh.json').read_bytes()).hexdigest()=='e9dace2039a9fb50ce028aa3b7cbff1f06893421dfa2d896e19c38f48d34c240'
    qa['mesh_sha256']=hashlib.sha256((OUT/'paving-v11-mesh.json').read_bytes()).hexdigest()
    previous=json.loads((OUT/'pass2/paving-v11-mesh.json').read_text())
    qa['period_change_previous_sha256']=hashlib.sha256((OUT/'pass2/paving-v11-mesh.json').read_bytes()).hexdigest()
    qa['topology_preserved_from_pass2']=g['indices']==previous['indices']
    qa['xz_preserved_from_pass2']=all(p[k]==previous['positions'][k] for k in range(len(p)) if k%3!=1)
    qa['uv_halved_from_pass2_max_error']=max(abs(v-previous['uv'][k]*.5) for k,v in enumerate(uv))
    qa['changed_height_vertices_from_pass2']=sum(abs(p[k]-previous['positions'][k])>1e-7 for k in range(1,len(p),3))
    preserved=json.loads((OUT/'pass2/preservation-manifest.json').read_text())
    qa['pass2_archive_preserved']=all(hashlib.sha256((OUT/'pass2'/p).read_bytes()).hexdigest()==h for p,h in preserved.items())
    assert qa['triangles']<=160000 and qa['positive_dot']==qa['triangles'] and qa['top_up_faces']==qa['triangles']
    assert not qa['negative_dot'] and not qa['degenerate'] and not qa['nonmanifold_overfull_edges']
    assert qa['finite'] and qa['attribute_lengths_match'] and qa['indices_in_bounds'] and qa['all_colors_one']
    assert max(abs(v-1) for v in lengths)<1e-6 and qa['uv_max_error']<1e-8 and max(errors)<2e-7
    assert qa['exact_v10_outer_xz_within_1nm'] and qa['minimum_water_clearance_m']>=.0196
    assert qa['downloaded_sources_preserved'] and qa['v10_preserved']
    assert qa['topology_preserved_from_pass2'] and qa['xz_preserved_from_pass2'] and qa['uv_halved_from_pass2_max_error']<1e-9
    assert qa['changed_height_vertices_from_pass2']>count*.99 and qa['pass2_archive_preserved']
    assert qa['working_source_comparison']['orientation']['negative_dot']==0
    qa['passed']=True
    (OUT/'export-qa.json').write_text(json.dumps(qa,indent=2),encoding='utf8');print(json.dumps(qa,indent=2))

if __name__=='__main__':main()
