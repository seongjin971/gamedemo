using System;
using System.IO;
using System.Linq;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.AI;
using Unity.AI.Navigation;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEditor.Build.Reporting;
namespace Vesper.Expansion.P2.Editor {
public static class P2Build {
 const string Root="Assets/Vesper/Expansion/P2";
 const string Scene="Assets/Vesper/Scenes/Expansion/VesperP2.unity";
 static Material stone,trim,wood,water,glow;
 static int meshId;
 static GameObject Box(Transform parent,string name,Vector3 pos,Vector3 size,Material mat,int layer=29){
  var g=GameObject.CreatePrimitive(PrimitiveType.Cube);g.name=name;g.transform.SetParent(parent,false);g.transform.position=pos;g.transform.localScale=size;g.layer=layer;
  if(mat)g.GetComponent<Renderer>().sharedMaterial=mat;else UnityEngine.Object.DestroyImmediate(g.GetComponent<Renderer>());
  return g;
 }
 static Material Mat(string name,Color color,float smooth=.25f){var m=new Material(Shader.Find("Universal Render Pipeline/Lit"));m.color=color;m.SetFloat("_Smoothness",smooth);AssetDatabase.CreateAsset(m,Root+"/Generated/"+name+".mat");return m;}
 static void MeshFloor(Transform parent,string name,List<Vector3> v,List<int> triangles,bool visible){
  var mesh=new Mesh{name=name,indexFormat=UnityEngine.Rendering.IndexFormat.UInt32};mesh.SetVertices(v);mesh.SetTriangles(triangles,0);mesh.RecalculateNormals();mesh.RecalculateBounds();
  mesh.uv=v.Select(p=>new Vector2(p.x,p.z)).ToArray();AssetDatabase.CreateAsset(mesh,Root+"/Generated/Mesh"+(meshId++)+".asset");
  var g=new GameObject(name);g.transform.SetParent(parent,false);g.layer=28;g.AddComponent<MeshCollider>().sharedMesh=mesh;
  if(visible){g.AddComponent<MeshFilter>().sharedMesh=mesh;g.AddComponent<MeshRenderer>().sharedMaterial=stone;}
 }
 static void Ramp(Transform p){
  MeshFloor(p,"Stone incline — 1.6m rise over 6m",new List<Vector3>{new Vector3(-2,0,6),new Vector3(2,0,6),new Vector3(2,1.6f,0),new Vector3(-2,1.6f,0)},new List<int>{0,1,2,0,2,3},true);
  for(int i=0;i<12;i++){float z=5.75f-i*.5f,y=(6-z)/6*1.6f;foreach(float x in new[]{-2.14f,2.14f})Box(p,"Incline coping",new Vector3(x,y+.18f,z),new Vector3(.25f,.36f,.49f),trim);}
 }
 static void Gate(Transform p,Vector3 pos,string label){
  foreach(float x in new[]{-1.3f,1.3f}){Box(p,"Gateway pier",pos+new Vector3(x,1.3f,0),new Vector3(.42f,2.6f,.5f),trim);Box(p,"Amber waymark",pos+new Vector3(x,2.25f,.28f),new Vector3(.16f,.32f,.08f),glow);}
  Box(p,"Gateway lintel",pos+Vector3.up*2.65f,new Vector3(3.1f,.35f,.6f),stone);
  var text=new GameObject(label);text.transform.SetParent(p,false);text.transform.position=pos+new Vector3(0,3,.1f);text.transform.rotation=Quaternion.Euler(0,180,0);var tm=text.AddComponent<TextMesh>();tm.text=label;tm.fontSize=60;tm.characterSize=.055f;tm.anchor=TextAnchor.MiddleCenter;tm.color=new Color(.9f,.72f,.4f);
 }
 static NavMeshSurface Bake(GameObject root,string name){
  var surface=root.AddComponent<NavMeshSurface>();surface.collectObjects=CollectObjects.Children;surface.useGeometry=NavMeshCollectGeometry.PhysicsColliders;surface.layerMask=(1<<28)|(1<<29);surface.overrideVoxelSize=true;surface.voxelSize=.055f;
  surface.BuildNavMesh();if(!surface.navMeshData)throw new Exception("No NavMesh for "+name);AssetDatabase.CreateAsset(surface.navMeshData,Root+"/Generated/"+name+"Nav.asset");return surface;
 }
 public static void Prepare(){try{
  Directory.CreateDirectory(Root+"/Generated");AssetDatabase.Refresh();meshId=0;
  var scene=EditorSceneManager.OpenScene("Assets/Vesper/Scenes/Expansion/VesperAdventurerRun.unity");EditorSceneManager.SaveScene(scene,Scene,false);
  var old=UnityEngine.Object.FindAnyObjectByType<AdventurerMotor>();var oldInput=old.GetComponent<AdventurerRunInput>();var anim=old.GetComponentInChildren<AdventurerRunAnimation>();var cam=Camera.main;var oldCam=cam.GetComponent<AdventurerCamera>();
  var motor=old.gameObject.AddComponent<P2Motor>();motor.home=old.home;
  var input=old.gameObject.AddComponent<P2RunInput>();input.motor=motor;
  var motion=anim.gameObject.AddComponent<P2Animation>();motion.motor=motor;motion.input=input;motion.animator=anim.animator;motion.idleClip=anim.idleClip;motion.walkClip=anim.walkClip;motion.runClip=anim.runClip;motion.authoredWalkSpeed=anim.authoredWalkSpeed;motion.authoredRunSpeed=anim.authoredRunSpeed;motion.runPhaseOffset=anim.runPhaseOffset;
  UnityEngine.Object.DestroyImmediate(anim);UnityEngine.Object.DestroyImmediate(oldInput);UnityEngine.Object.DestroyImmediate(old);UnityEngine.Object.DestroyImmediate(oldCam);
  var cc=cam.gameObject.AddComponent<P2Camera>();cc.player=motor;
  motor.transform.SetParent(null,true);cam.transform.SetParent(null,true);
  var court=new GameObject("P2 courtyard content");foreach(var root in scene.GetRootGameObjects())if(root!=court && root!=motor.gameObject && root!=cam.gameObject)root.transform.SetParent(court.transform,true);
  var conn=new GameObject("P2 crossing content");
  stone=Mat("Crossing slate",new Color(.28f,.31f,.33f));trim=Mat("Weathered coping",new Color(.37f,.36f,.31f));wood=Mat("Bridge timber",new Color(.22f,.15f,.09f));water=Mat("Blocked dark water",new Color(.035f,.095f,.12f),.8f);glow=Mat("Amber markers",new Color(.7f,.35f,.08f));glow.EnableKeyword("_EMISSION");glow.SetColor("_EmissionColor",new Color(2.5f,1.1f,.2f));
  // Collision tessellation retains the accepted courtyard walkable footprint. It is
  // baked once; the P1 flat navigator is not used by the P2 runtime.
  var nav=new VesperNavigation();var verts=new List<Vector3>();var tris=new List<int>();const float step=.2f;
  for(float z=-1.2f;z<11.2f;z+=step)for(float x=-7.7f;x<7.7f;x+=step){var a=new Vector3(x,0,z);var b=a+new Vector3(step,0,0);var c=a+new Vector3(step,0,step);var d=a+new Vector3(0,0,step);if(!nav.Valid(a)||!nav.Valid(b)||!nav.Valid(c)||!nav.Valid(d))continue;int n=verts.Count;verts.AddRange(new[]{a,b,c,d});tris.AddRange(new[]{n,n+2,n+1,n,n+3,n+2});}
  MeshFloor(court.transform,"Courtyard collision paving",verts,tris,false);
  // Existing visible masonry and roots block click rays, without mutating shared assets.
  foreach(var mf in court.GetComponentsInChildren<MeshFilter>()){
   string n=mf.gameObject.name.ToLowerInvariant();if(n.Contains("masonry batch")||n.Contains("tree")||n.Contains("root")){if(!mf.sharedMesh)continue;var g=new GameObject("Click blocker "+mf.name);g.layer=29;g.transform.SetParent(mf.transform,false);g.AddComponent<MeshCollider>().sharedMesh=mf.sharedMesh;var modifier=g.AddComponent<NavMeshModifier>();modifier.ignoreFromBuild=true;}
  }
  Gate(court.transform,new Vector3(-5,0,10.3f),"THE CROSSING");
  Box(conn.transform,"Lower stone landing",new Vector3(0,-.2f,8.5f),new Vector3(8,.4f,5),stone,28);
  Ramp(conn.transform);
  Box(conn.transform,"Bridge deck",new Vector3(0,1.42f,-2.5f),new Vector3(4,.36f,5.1f),wood,28);
  for(int i=0;i<17;i++)Box(conn.transform,"Timber joint",new Vector3(0,1.602f,-.1f-i*.3f),new Vector3(3.94f,.006f,.025f),trim,0);
  Box(conn.transform,"Upper stone landing",new Vector3(0,1.4f,-8),new Vector3(8,.4f,6),stone,28);
  Box(conn.transform,"Impassable stream",new Vector3(0,-.7f,-2.5f),new Vector3(15,.2f,5),water);
  Box(conn.transform,"Disconnected ledge",new Vector3(6,2.7f,-7),new Vector3(2,.5f,2),stone,28);
  Box(conn.transform,"Fallen masonry obstacle",new Vector3(.25f,2.3f,-7.1f),new Vector3(1.8f,1.4f,1.1f),trim);
  foreach(float x in new[]{-2.17f,2.17f}){
   Box(conn.transform,"Bridge handrail",new Vector3(x,2.5f,-2.5f),new Vector3(.18f,.18f,5.4f),wood);
   for(int i=0;i<6;i++)Box(conn.transform,"Bridge baluster",new Vector3(x,2.02f,-i),new Vector3(.17f,.95f,.17f),wood);
  }
  foreach(float x in new[]{-4.13f,4.13f}){Box(conn.transform,"Lower parapet",new Vector3(x,.45f,8.5f),new Vector3(.25f,.9f,5),trim);Box(conn.transform,"Upper parapet",new Vector3(x,2.05f,-8),new Vector3(.25f,.9f,6),trim);}
  Box(conn.transform,"Upper end wall",new Vector3(0,2.05f,-11),new Vector3(8,.9f,.3f),trim);
  Gate(conn.transform,new Vector3(0,0,10.8f),"COURTYARD");
  var light=new GameObject("Crossing moon");light.transform.SetParent(conn.transform,false);light.transform.rotation=Quaternion.Euler(48,-30,0);var l=light.AddComponent<Light>();l.type=LightType.Directional;l.color=new Color(.65f,.78f,1);l.intensity=1.6f;l.shadows=LightShadows.Soft;
  foreach(var pos in new[]{new Vector3(-3,2,7),new Vector3(3,3,-8)}){var lamp=new GameObject("Amber lantern");lamp.transform.SetParent(conn.transform,false);lamp.transform.position=pos;var ll=lamp.AddComponent<Light>();ll.type=LightType.Point;ll.color=new Color(1,.56f,.22f);ll.range=9;ll.intensity=4;Box(conn.transform,"Lantern pedestal",pos-Vector3.up*.65f,new Vector3(.45f,1.3f,.45f),trim);Box(conn.transform,"Lantern glass",pos+Vector3.up*.15f,new Vector3(.22f,.3f,.22f),glow);}
  // Nonwalkable collision tops must never become stepping stones.
  foreach(var g in conn.GetComponentsInChildren<Collider>())if(g.gameObject.layer==29){var m=g.gameObject.AddComponent<NavMeshModifier>();m.overrideArea=true;m.area=1;}
  conn.SetActive(false);Bake(court,"Courtyard");court.SetActive(false);conn.SetActive(true);Bake(conn,"Crossing");conn.SetActive(false);court.SetActive(true);
  var world=new GameObject("P2 zone owner").AddComponent<P2World>();world.courtyard=court;world.connection=conn;world.player=motor;world.cameraControl=cc;
  AssetDatabase.SaveAssets();EditorSceneManager.SaveScene(scene);File.WriteAllText("../../Migration/Evidence/Expansion/P2/prepare.txt","P2 scene saved; AI Navigation "+UnityEditor.PackageManager.PackageInfo.FindForAssembly(typeof(NavMeshSurface).Assembly).version+"; missing scripts "+UnityEngine.Object.FindObjectsByType<Transform>().Sum(t=>GameObjectUtility.GetMonoBehavioursWithMissingScriptCount(t.gameObject)));
  EditorApplication.Exit(0);
 }catch(Exception e){Debug.LogException(e);EditorApplication.Exit(1);}}
 [Serializable]class BuildData{public string result;public int errors,warnings;public double seconds;public string[] messages;}
 public static void Build(){var report=BuildPipeline.BuildPlayer(new BuildPlayerOptions{scenes=new[]{Scene},locationPathName="Builds/VesperP2/VesperP2.exe",target=BuildTarget.StandaloneWindows64,options=BuildOptions.StrictMode});File.WriteAllText("../../Migration/Evidence/Expansion/P2/build-report.json",JsonUtility.ToJson(new BuildData{result=report.summary.result.ToString(),errors=report.summary.totalErrors,warnings=report.summary.totalWarnings,seconds=report.summary.totalTime.TotalSeconds,messages=report.steps.SelectMany(s=>s.messages).Where(m=>m.type==LogType.Error||m.type==LogType.Warning).Select(m=>m.content).Distinct().ToArray()},true));EditorApplication.Exit(report.summary.result==BuildResult.Succeeded?0:1);}
}
}
