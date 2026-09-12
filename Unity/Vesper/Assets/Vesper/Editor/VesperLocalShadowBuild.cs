using System.Collections.Generic;
using System.Linq;
using UnityEditor;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;

namespace Vesper.Editor {
// Preserve the visible meshes and moon shadows. Point shadow maps only need
// triangles which intersect their light volume, not entire courtyard batches.
public static class VesperLocalShadowBuild {
 sealed class Tile {public readonly List<Vector3> vertices=new List<Vector3>(),normals=new List<Vector3>();public readonly List<int> indices=new List<int>();public readonly Dictionary<int,int> remap=new Dictionary<int,int>();}
 public static void Build(){
  var pipeline=(UniversalRenderPipelineAsset)GraphicsSettings.currentRenderPipeline;
  var settings=new SerializedObject(pipeline);settings.FindProperty("m_SupportsLightLayers").boolValue=true;settings.ApplyModifiedPropertiesWithoutUndo();EditorUtility.SetDirty(pipeline);
  var renderers=Object.FindObjectsByType<MeshRenderer>();
  foreach(var renderer in renderers)renderer.renderingLayerMask=renderer.GetComponentInParent<VesperKnight>()?7u:1u;
  var lights=Object.FindObjectsByType<Light>().Where(l=>l.name=="Brazier").OrderBy(l=>l.transform.position.x).ToArray();
  for(int lightIndex=0;lightIndex<lights.Length;lightIndex++){
   var light=lights[lightIndex];uint mask=2u<<lightIndex;var data=light.GetUniversalAdditionalLightData();data.customShadowLayers=true;data.shadowRenderingLayers=mask;
   foreach(bool twoSided in new[]{false,true}){
    var vertices=new List<Vector3>();var normals=new List<Vector3>();var indices=new List<int>();int sourceTriangles=0;
    foreach(var renderer in renderers){
     if(!renderer.enabled||renderer.shadowCastingMode==ShadowCastingMode.Off||renderer.GetComponentInParent<VesperKnight>()||(renderer.shadowCastingMode==ShadowCastingMode.TwoSided)!=twoSided)continue;
     if(renderer.bounds.SqrDistance(light.transform.position)>light.range*light.range)continue;
     var filter=renderer.GetComponent<MeshFilter>();if(!filter||!filter.sharedMesh)continue;
     var mesh=filter.sharedMesh;var local=mesh.vertices;var originalNormals=mesh.normals;var tris=mesh.triangles;sourceTriangles+=tris.Length/3;
     var matrix=renderer.localToWorldMatrix;var normalMatrix=matrix.inverse.transpose;bool flip=matrix.determinant<0;
     var world=local.Select(p=>matrix.MultiplyPoint3x4(p)).ToArray();var remap=new Dictionary<int,int>();
     for(int t=0;t<tris.Length;t+=3){
      var bounds=new Bounds(world[tris[t]],Vector3.zero);bounds.Encapsulate(world[tris[t+1]]);bounds.Encapsulate(world[tris[t+2]]);
      // Conservative AABB/sphere intersection retains crossing triangles whose
      // vertices all lie outside the light. No decimation or silhouette proxy.
      if(bounds.SqrDistance(light.transform.position)>light.range*light.range)continue;
      for(int k=0;k<3;k++){int original=tris[t+(flip&&k>0?3-k:k)];if(!remap.TryGetValue(original,out int mapped)){mapped=vertices.Count;remap.Add(original,mapped);vertices.Add(world[original]);normals.Add(normalMatrix.MultiplyVector(originalNormals[original]).normalized);}indices.Add(mapped);}
     }
    }
    if(indices.Count==0)continue;
    string id=lightIndex+(twoSided?"-two-sided":"-front");
    var shadowMesh=new Mesh{name="Exact local fire shadow triangles "+id,indexFormat=IndexFormat.UInt32};shadowMesh.SetVertices(vertices);shadowMesh.SetNormals(normals);shadowMesh.SetTriangles(indices,0);shadowMesh.RecalculateBounds();
    shadowMesh=VesperAtmosphereBuild.Save(shadowMesh,VesperAtmosphereBuild.Root+"/Meshes/LocalFireShadow-"+id+".asset");
    var material=new Material(Shader.Find("Universal Render Pipeline/Lit"));material.SetFloat("_Cull",twoSided?0:2);material=VesperAtmosphereBuild.Save(material,VesperAtmosphereBuild.Root+"/Materials/LocalFireShadow-"+id+".mat");
    // Retain the original exact combined mesh disabled for an identical-player
    // diagnostic. Default small bounds restore individual cube-face culling.
    AddProxy("Exact local fire shadow combined "+id,shadowMesh,material,mask).enabled=false;
    var tiles=new Dictionary<Vector3Int,Tile>();
    for(int t=0;t<indices.Count;t+=3){
     Vector3 center=(vertices[indices[t]]+vertices[indices[t+1]]+vertices[indices[t+2]])/3;
     var key=new Vector3Int(Mathf.FloorToInt(center.x/2),Mathf.FloorToInt(center.y/2),Mathf.FloorToInt(center.z/2));
     if(!tiles.TryGetValue(key,out var tile)){tile=new Tile();tiles.Add(key,tile);}
     // Assign once; an edge crossing a tile extends its actual mesh bounds.
     // Never clip triangles or cull using the nominal tile box.
     for(int k=0;k<3;k++){int original=indices[t+k];if(!tile.remap.TryGetValue(original,out int mapped)){mapped=tile.vertices.Count;tile.remap.Add(original,mapped);tile.vertices.Add(vertices[original]);tile.normals.Add(normals[original]);}tile.indices.Add(mapped);}
    }
    int retained=0;
    foreach(var entry in tiles.OrderBy(p=>p.Key.x).ThenBy(p=>p.Key.y).ThenBy(p=>p.Key.z)){
     var tile=entry.Value;string tileId=id+"-"+entry.Key.x+"-"+entry.Key.y+"-"+entry.Key.z;
     var mesh=new Mesh{name="Exact spatial fire caster "+tileId,indexFormat=IndexFormat.UInt32};mesh.SetVertices(tile.vertices);mesh.SetNormals(tile.normals);mesh.SetTriangles(tile.indices,0);mesh.RecalculateBounds();
     mesh=VesperAtmosphereBuild.Save(mesh,VesperAtmosphereBuild.Root+"/Meshes/LocalFireTile-"+tileId+".asset");
     AddProxy("Exact local fire shadow tile "+tileId,mesh,material,mask);retained+=tile.indices.Count;
    }
    if(retained!=indices.Count)throw new System.Exception("Fire shadow tile triangle drift");
    Debug.Log("VESPER_LOCAL_SHADOW "+id+" retained="+indices.Count/3+" source="+sourceTriangles+" tiles="+tiles.Count);
   }
  }
 }
 static MeshRenderer AddProxy(string name,Mesh mesh,Material material,uint mask){var go=new GameObject(name);go.AddComponent<MeshFilter>().sharedMesh=mesh;var proxy=go.AddComponent<MeshRenderer>();proxy.sharedMaterial=material;proxy.renderingLayerMask=mask;proxy.shadowCastingMode=ShadowCastingMode.ShadowsOnly;return proxy;}
}
}
