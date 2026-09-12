using System;
using System.IO;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using Unity.AI.Navigation;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.AI;

namespace Vesper.Expansion.P2.Editor {
public static class P2GroundBuild {
 public const string Scene="Assets/Vesper/Scenes/Expansion/VesperP2ClickFix.unity";
 public const string Nav="Assets/Vesper/Expansion/P2/Generated/ClickFixCourtyardNav.asset";
 const string FloorMesh="Assets/Vesper/Expansion/P2/Generated/ClickFixGroundSupport.asset";
 [Serializable]class Geometry{public Vector3[] vertices;public int[] triangles;}
 public static void Inspect(){
  EditorSceneManager.OpenScene(Scene);var world=UnityEngine.Object.FindAnyObjectByType<P2World>();var sb=new StringBuilder();
  sb.AppendLine(JsonUtility.ToJson(world.courtyard.GetComponent<NavMeshSurface>().GetBuildSettings()));
  foreach(var p in new[]{new Vector3(4.79f,-.1f,.11f),new Vector3(5.06f,-.1f,2.09f)}){
   NavMesh.SamplePosition(p,out var nh,.65f,NavMesh.AllAreas);var path=new NavMeshPath();NavMesh.CalculatePath(world.player.transform.position,nh.position,NavMesh.AllAreas,path);
   sb.AppendLine($"target={p} path={path.status}");foreach(var corner in path.corners)sb.AppendLine(corner.ToString("F4"));
  }
  for(float x=-3.1f;x<-2.6f;x+=.025f){var p=new Vector3(x,-.1f,-1.48f);bool found=NavMesh.SamplePosition(p,out var nh,.35f,NavMesh.AllAreas);sb.AppendLine($"sample {p:F4}: {found} {nh.position:F4}");}
  Physics.SyncTransforms();
  for(float z=0;z<=8;z+=2)for(float x=-3;x<=2;x+=.2f){
   if(!Physics.SphereCast(new Vector3(x,.35f,z),.12f,Vector3.down,out var hit,.9f,P2Motor.SurfaceMask|P2Motor.BlockMask,QueryTriggerInteraction.Ignore))continue;
   var overlaps=Physics.OverlapCapsule(hit.point+Vector3.up*.16f,hit.point+Vector3.up*1.55f,.055f,P2Motor.SurfaceMask|P2Motor.BlockMask,QueryTriggerInteraction.Ignore);
   if(overlaps.Length>0)sb.AppendLine($"occupied {hit.point:F3} by "+string.Join(" | ",overlaps.Select(c=>$"{c.name} bounds={c.bounds}")));
  }
  NavMesh.Raycast(world.player.transform.position,new Vector3(4.79f,-.1f,.11f),out var edge,NavMesh.AllAreas);sb.AppendLine($"Nav edge {edge.position:F4}");
  var floorMesh=AssetDatabase.LoadAssetAtPath<Mesh>(FloorMesh);var navTriangles=NavMesh.CalculateTriangulation();
  File.WriteAllText(P2ClickAudit.Evidence+"/support-geometry.json",JsonUtility.ToJson(new Geometry{vertices=floorMesh.vertices,triangles=floorMesh.triangles}));
  File.WriteAllText(P2ClickAudit.Evidence+"/navigation-geometry.json",JsonUtility.ToJson(new Geometry{vertices=navTriangles.vertices,triangles=navTriangles.indices}));
  for(float z=4.8f;z<5.7f;z+=.1f)for(float x=-.3f;x<.3f;x+=.1f){var origin=new Vector3(x,.35f,z);bool floor=Physics.Raycast(origin,Vector3.down,out var fh,.9f,P2Motor.SurfaceMask|P2Motor.BlockMask);bool proxy=Physics.Raycast(origin,Vector3.down,out var ph,.9f,1<<27);sb.AppendLine($"edge sample {origin:F3} physical={floor} hit={fh.point:F4} normal={fh.normal:F4} proxy={proxy} proxyHit={ph.point:F4}");}
  File.WriteAllText(P2ClickAudit.Evidence+"/ground-paths-02.txt",sb.ToString());EditorApplication.Exit(0);
 }
 public static void Prepare(){try{
  var scene=EditorSceneManager.OpenScene("Assets/Vesper/Scenes/Expansion/VesperP2.unity");
  EditorSceneManager.SaveScene(scene,Scene);
  var world=UnityEngine.Object.FindAnyObjectByType<P2World>();
  var surface=world.courtyard.GetComponent<NavMeshSurface>();surface.RemoveData();
  foreach(var collider in world.courtyard.GetComponentsInChildren<Collider>()){
   if(collider.name=="Courtyard collision paving"){UnityEngine.Object.DestroyImmediate(collider.gameObject);continue;}
   if(!collider.name.StartsWith("Click blocker "))continue;
   var modifier=collider.GetComponent<NavMeshModifier>();
   modifier.ignoreFromBuild=false;
   if(collider.name.StartsWith("Click blocker Masonry batch ")){
    collider.gameObject.layer=28;modifier.overrideArea=false;
   }else {modifier.overrideArea=true;modifier.area=1;}
  }
  // Reconstruct the low courtyard paving from actual collision samples, rather
  // than the old rectangular/polygon footprint. Decorative stair risers must not
  // become detours for the ground motor. Original masonry remains the click and
  // foot-height surface; this separate layer is only used for navigation baking.
  Physics.SyncTransforms();
  const float cell=.15f;const int nx=135,nz=155;
  var points=new Vector3[nx,nz];var valid=new bool[nx,nz];
  for(int iz=0;iz<nz;iz++)for(int ix=0;ix<nx;ix++){
   float x=-10.05f+ix*cell,z=-1.8f+iz*cell;
   if(!Physics.SphereCast(new Vector3(x,.35f,z),.12f,Vector3.down,out var hit,.9f,P2Motor.SurfaceMask|P2Motor.BlockMask,QueryTriggerInteraction.Ignore))continue;
   if(hit.collider.gameObject.layer!=28 || hit.normal.y<.8f || hit.point.y>.12f || hit.point.y<-.5f)continue;
   var groundPoint=new Vector3(x,hit.point.y,z);
   // Small occupancy radius plus the baked agent radius provides body clearance.
   if(Physics.CheckCapsule(groundPoint+Vector3.up*.16f,groundPoint+Vector3.up*1.55f,.055f,P2Motor.SurfaceMask|P2Motor.BlockMask,QueryTriggerInteraction.Ignore))continue;
   points[ix,iz]=groundPoint;valid[ix,iz]=true;
  }
  var verts=new List<Vector3>();var tris=new List<int>();
  for(int iz=0;iz<nz-1;iz++)for(int ix=0;ix<nx-1;ix++){
   if(!valid[ix,iz]||!valid[ix+1,iz]||!valid[ix+1,iz+1]||!valid[ix,iz+1])continue;
   int n=verts.Count;verts.AddRange(new[]{points[ix,iz],points[ix+1,iz],points[ix+1,iz+1],points[ix,iz+1]});tris.AddRange(new[]{n,n+2,n+1,n,n+3,n+2});
  }
  var mesh=new Mesh{name="Visible courtyard ground support",indexFormat=UnityEngine.Rendering.IndexFormat.UInt32};mesh.SetVertices(verts);mesh.SetTriangles(tris,0);mesh.RecalculateNormals();mesh.RecalculateBounds();
  if(AssetDatabase.LoadAssetAtPath<Mesh>(FloorMesh))AssetDatabase.DeleteAsset(FloorMesh);AssetDatabase.CreateAsset(mesh,FloorMesh);
  var support=new GameObject("P2 visible-ground navigation support");support.transform.SetParent(world.courtyard.transform,false);support.layer=27;support.AddComponent<MeshCollider>().sharedMesh=mesh;
  surface.layerMask=1<<27;surface.collectObjects=CollectObjects.Children;
  var settings=surface.GetBuildSettings();settings.agentRadius=.25f;settings.agentHeight=1.7f;settings.agentClimb=.2f;
  var sources=new List<NavMeshBuildSource>();UnityEngine.AI.NavMeshBuilder.CollectSources(world.courtyard.transform,1<<27,NavMeshCollectGeometry.PhysicsColliders,0,new List<NavMeshBuildMarkup>(),sources);
  var data=UnityEngine.AI.NavMeshBuilder.BuildNavMeshData(settings,sources,new Bounds(new Vector3(0,0,10),new Vector3(22,3,26)),Vector3.zero,Quaternion.identity);
  surface.navMeshData=data;surface.AddData();
  if(!surface.navMeshData)throw new Exception("Visible-ground bake failed");
  if(AssetDatabase.LoadAssetAtPath<NavMeshData>(Nav))AssetDatabase.DeleteAsset(Nav);
  AssetDatabase.CreateAsset(surface.navMeshData,Nav);
  world.courtyardSpawn=Ground(world.courtyardSpawn);world.returnSpawn=Ground(world.returnSpawn);world.courtyardGate=Ground(world.courtyardGate);
  world.player.home=world.courtyardSpawn;world.player.transform.position=world.courtyardSpawn;
  AssetDatabase.SaveAssets();EditorSceneManager.SaveScene(scene);
  var sb=new StringBuilder("x,z,groundY,normalY,firstCollider,navDistance,complete\n");
  for(float z=-5;z<=20;z+=1)for(float x=-9;x<=9;x+=1){
   if(!Physics.Raycast(new Vector3(x,10,z),Vector3.down,out var hit,12,P2Motor.SurfaceMask|P2Motor.BlockMask))continue;
   bool found=NavMesh.SamplePosition(hit.point,out var nh,.65f,NavMesh.AllAreas);
   var path=new NavMeshPath();bool complete=found&&NavMesh.CalculatePath(world.player.transform.position,nh.position,NavMesh.AllAreas,path)&&path.status==NavMeshPathStatus.PathComplete;
   sb.AppendLine($"{x},{z},{hit.point.y:F3},{hit.normal.y:F3},{hit.collider.name},{(found?nh.distance:-1):F3},{complete}");
  }
  Directory.CreateDirectory(P2ClickAudit.Evidence);File.WriteAllText(P2ClickAudit.Evidence+"/visible-ground-grid.csv",sb.ToString());
  EditorApplication.Exit(0);
 }catch(Exception e){Debug.LogException(e);EditorApplication.Exit(1);}}
 static Vector3 Ground(Vector3 p){if(Physics.Raycast(p+Vector3.up*.3f,Vector3.down,out var hit,.8f,P2Motor.SurfaceMask))return hit.point;return p;}
}
}
