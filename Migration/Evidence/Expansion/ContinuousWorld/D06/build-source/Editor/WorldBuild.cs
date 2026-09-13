using System;
using System.IO;
using System.Linq;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.AI;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;
using Unity.AI.Navigation;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEditor.Build.Reporting;
using Vesper.Expansion.P2;

namespace Vesper.Expansion.ContinuousWorld.Editor {
public static class WorldBuild {
 public const string Root="Assets/Vesper/Expansion/ContinuousWorld";
 public const string ScenePath="Assets/Vesper/Scenes/Expansion/VesperContinuousWorld.unity";
 static string generated,revision;static int meshSerial;
 static Material earth,stone,water,snow,grass;
 public static string Arg(string key,string fallback){var args=Environment.GetCommandLineArgs();int i=Array.IndexOf(args,key);return i>=0&&i+1<args.Length?args[i+1]:fallback;}
 static string Evidence=>Path.GetFullPath("../../Migration/Evidence/Expansion/ContinuousWorld/"+revision);
 public static Material Material(string name,Color color,float smooth=.25f){var m=new Material(Shader.Find("Universal Render Pipeline/Lit"));m.color=color;m.SetFloat("_Smoothness",smooth);AssetDatabase.CreateAsset(m,generated+"/"+name+".mat");return m;}
 public static GameObject Box(Transform parent,string name,Vector3 pos,Vector3 scale,Material mat,int layer=29){var g=GameObject.CreatePrimitive(PrimitiveType.Cube);g.name=name;g.layer=layer;g.transform.SetParent(parent,false);g.transform.position=pos;g.transform.localScale=scale;g.GetComponent<Renderer>().sharedMaterial=mat;return g;}
 public static GameObject MeshObject(Transform parent,string name,List<Vector3> verts,List<int> tris,Material mat,int layer,bool collider=true,Color[] colors=null){
  var mesh=new Mesh{name=name,indexFormat=IndexFormat.UInt32};mesh.SetVertices(verts);mesh.SetTriangles(tris,0);mesh.uv=verts.Select(v=>new Vector2(v.x*.20f,v.z*.20f)).ToArray();if(colors!=null)mesh.colors=colors;mesh.RecalculateNormals();mesh.RecalculateBounds();AssetDatabase.CreateAsset(mesh,generated+"/mesh-"+(meshSerial++)+".asset");
  var g=new GameObject(name);g.layer=layer;g.transform.SetParent(parent,false);g.AddComponent<MeshFilter>().sharedMesh=mesh;g.AddComponent<MeshRenderer>().sharedMaterial=mat;if(collider)g.AddComponent<MeshCollider>().sharedMesh=mesh;return g;
 }
 static void Terrain(Transform parent){
  for(int z0=-448;z0<32;z0+=32)for(int x0=-80;x0<80;x0+=32){
   int cells=z0>=-96&&x0>=-48&&x0<=16?64:16;float spacing=32f/cells;
   var verts=new List<Vector3>();var tris=new List<int>();var colors=new List<Color>();
   for(int iz=0;iz<=cells;iz++)for(int ix=0;ix<=cells;ix++){
    float x=x0+ix*spacing,z=z0+iz*spacing,d=-z;verts.Add(new Vector3(x,WorldLayout.Height(x,d),z));
    var w=WorldLayout.Weights(d);float path=1-Mathf.SmoothStep(0,1,Mathf.InverseLerp(3,5.5f,Mathf.Abs(x-WorldLayout.Center(d))));
    var ground=new Color(.28f,.34f,.20f)*w.x+new Color(.24f,.28f,.24f)*w.y+new Color(.70f,.77f,.79f)*w.z;
    var trail=new Color(.45f,.40f,.30f)*w.x+new Color(.29f,.31f,.30f)*w.y+new Color(.60f,.66f,.70f)*w.z;
    colors.Add(Color.Lerp(ground,trail,path));
   }
   for(int iz=0;iz<cells;iz++)for(int ix=0;ix<cells;ix++){int a=iz*(cells+1)+ix;tris.AddRange(new[]{a,a+cells+1,a+1,a+1,a+cells+1,a+cells+2});}
   MeshObject(parent,"Continuous terrain "+x0+" "+z0,verts,tris,earth,28,true,colors.ToArray());
  }
 }
 static void Bridge(Transform parent){
  float center=WorldLayout.Center(48.5f),height=WorldLayout.Level(48.5f);var bridge=Box(parent,"Walkable bridge deck",new Vector3(center,height-.3f,-48.5f),new Vector3(6,.6f,14),stone,28);
  foreach(float x in new[]{-3.1f,3.1f})Box(parent,"Bridge parapet",new Vector3(center+x,height+.45f,-48.5f),new Vector3(.35f,.9f,14),stone);
 }
 static WorldEnvironment Lighting(WorldMotor player,Camera camera){
  var world=new GameObject("Continuous environment owner").AddComponent<WorldEnvironment>();world.player=player;
  var sun=new GameObject("Shared climate sun").AddComponent<Light>();sun.type=LightType.Directional;sun.transform.rotation=Quaternion.Euler(48,-38,0);sun.intensity=1.5f;sun.shadows=LightShadows.Soft;world.sun=sun;
  sun.GetUniversalAdditionalLightData().softShadowQuality=SoftShadowQuality.Low;
  RenderSettings.ambientMode=AmbientMode.Trilight;RenderSettings.sun=sun;
  var sky=new Material(Shader.Find("Skybox/Procedural"));sky.SetColor("_SkyTint",new Color(.54f,.64f,.70f));sky.SetColor("_GroundColor",new Color(.35f,.4f,.36f));sky.SetFloat("_AtmosphereThickness",1.1f);AssetDatabase.CreateAsset(sky,generated+"/ClimateSky.mat");RenderSettings.skybox=sky;world.skyMaterial=sky;
  var volume=new GameObject("Continuous world grading").AddComponent<Volume>();volume.isGlobal=true;volume.priority=100;
  var profile=ScriptableObject.CreateInstance<VolumeProfile>();AssetDatabase.CreateAsset(profile,generated+"/ClimateGrade.asset");
  var tone=profile.Add<Tonemapping>();tone.mode.Override(TonemappingMode.ACES);
  var grade=profile.Add<ColorAdjustments>();grade.postExposure.Override(.15f);grade.contrast.Override(8);grade.saturation.Override(-5);
  var bloom=profile.Add<Bloom>();bloom.intensity.Override(.12f);bloom.threshold.Override(1.3f);
  foreach(var c in profile.components)AssetDatabase.AddObjectToAsset(c,profile);volume.sharedProfile=profile;world.volume=volume;
  camera.farClipPlane=300;camera.nearClipPlane=.1f;camera.backgroundColor=new Color(.56f,.66f,.71f);
  return world;
 }
 static void Bake(GameObject root){
  foreach(var c in root.GetComponentsInChildren<Collider>())if(c.gameObject.layer==29){var m=c.gameObject.AddComponent<NavMeshModifier>();m.overrideArea=true;m.area=1;}
  var surface=root.AddComponent<NavMeshSurface>();surface.collectObjects=CollectObjects.Children;surface.useGeometry=NavMeshCollectGeometry.PhysicsColliders;surface.layerMask=(1<<28)|(1<<29);surface.overrideVoxelSize=true;surface.voxelSize=.12f;surface.overrideTileSize=true;surface.tileSize=128;
  surface.BuildNavMesh();if(!surface.navMeshData)throw new Exception("Navigation bake failed");AssetDatabase.CreateAsset(surface.navMeshData,generated+"/ContinuousNavigation.asset");
 }
 [Serializable]class RouteReport{public float distance,walkSeconds;public string[] routes;public int objects,triangles,missingScripts;}
 public static void Prepare(){try{
  revision=Arg("-worldRevision","A01");generated=Root+"/Generated/"+revision;Directory.CreateDirectory(generated);Directory.CreateDirectory(Evidence);AssetDatabase.Refresh();meshSerial=0;
  var scene=EditorSceneManager.OpenScene("Assets/Vesper/Scenes/Expansion/VesperP2ClickFix.unity");EditorSceneManager.SaveScene(scene,ScenePath,false);
  var old=UnityEngine.Object.FindAnyObjectByType<P2Motor>();var camera=Camera.main;var oldMotion=old.GetComponentInChildren<P2Animation>();var oldInput=old.GetComponent<P2RunInput>();var oldCamera=camera.GetComponent<P2Camera>();
  var player=old.gameObject.AddComponent<WorldMotor>();player.home=WorldLayout.Point(0);player.transform.position=player.home;player.transform.rotation=Quaternion.Euler(0,180,0);
  var input=old.gameObject.AddComponent<WorldRunInput>();input.motor=player;
  var anim=oldMotion.gameObject.AddComponent<WorldAnimation>();anim.motor=player;anim.input=input;anim.animator=oldMotion.animator;anim.idleClip=oldMotion.idleClip;anim.walkClip=oldMotion.walkClip;anim.runClip=oldMotion.runClip;anim.authoredWalkSpeed=oldMotion.authoredWalkSpeed;anim.authoredRunSpeed=oldMotion.authoredRunSpeed;anim.runPhaseOffset=oldMotion.runPhaseOffset;
  UnityEngine.Object.DestroyImmediate(oldMotion);UnityEngine.Object.DestroyImmediate(oldInput);UnityEngine.Object.DestroyImmediate(old);UnityEngine.Object.DestroyImmediate(oldCamera);
  player.transform.SetParent(null,true);camera.transform.SetParent(null,true);
  foreach(var ambient in player.GetComponentsInChildren<Vesper.Expansion.AdventurerAmbient>())UnityEngine.Object.DestroyImmediate(ambient);
  // New-scene material instance: do not inherit the courtyard's reflection/probe state.
  var travelerSource=AssetDatabase.LoadAssetAtPath<Material>("Assets/Vesper/Expansion/P1/Materials/Traveler.mat");
  var traveler=new Material(travelerSource){name="Daylight traveler"};traveler.SetFloat("_EnvironmentReflections",0);traveler.EnableKeyword("_ENVIRONMENTREFLECTIONS_OFF");traveler.SetFloat("_Smoothness",.23f);AssetDatabase.CreateAsset(traveler,generated+"/DaylightTraveler.mat");
  foreach(var skin in player.GetComponentsInChildren<SkinnedMeshRenderer>()){skin.SetPropertyBlock(null);skin.sharedMaterials=Enumerable.Repeat(traveler,skin.sharedMesh.subMeshCount).ToArray();skin.lightProbeUsage=LightProbeUsage.Off;skin.reflectionProbeUsage=ReflectionProbeUsage.Off;}
  foreach(var root in scene.GetRootGameObjects())if(root!=player.gameObject&&root!=camera.gameObject)UnityEngine.Object.DestroyImmediate(root);
  var control=camera.gameObject.AddComponent<WorldCamera>();control.player=player;control.homeTarget=player.home+Vector3.up*1.2f;control.homeSize=11.1f;
  camera.orthographic=true;camera.orthographicSize=11.1f;
  earth=Material("Earth",Color.white);var terrainShader=Shader.Find("Vesper/ContinuousTerrain");if(terrainShader)earth.shader=terrainShader;
  stone=Material("PathStone",new Color(.44f,.43f,.37f));water=Material("River",new Color(.05f,.24f,.29f),.88f);snow=Material("Snow",new Color(.8f,.86f,.9f));grass=Material("Grass",new Color(.32f,.4f,.24f));
  var terrain=new GameObject("Continuous collision and terrain");Terrain(terrain.transform);Bridge(terrain.transform);
  Box(terrain.transform,"Deep river - not walkable",new Vector3(0,-1.0f,-47.5f),new Vector3(175,.08f,27),water);
  foreach(float d in new[]{25f,85f,130f,175f,230f,275f,330f,375f}){var p=WorldLayout.Point(d,7);p.y=WorldLayout.Height(p.x,d);Box(terrain.transform,"Route waystone "+d,p+Vector3.up*.65f,new Vector3(.8f,1.3f,.65f),stone);}
  // First collision test objects are outside the continuous primary walking lane.
  var block=WorldLayout.Point(18,3.8f);Box(terrain.transform,"Blocked test outcrop",block+Vector3.up,new Vector3(1.5f,2,2),stone);
  var world=Lighting(player,camera);string stage=Arg("-worldStage","A");if(stage!="A")WorldVisuals.Waterside(terrain,world,generated);if(stage=="C"||stage=="D"||stage=="E")WorldVisuals.Ruins(terrain,world);if(stage=="D"||stage=="E")WorldVisuals.SnowPass(terrain,world);Bake(terrain);Physics.SyncTransforms();
  var edgeDiagnostics=new List<string>();foreach(float d in new[]{12f,35f,60f,82f,120f,165f,195f,230f,265f,315f,360f}){var p=WorldLayout.Point(d+2,2.2f);bool sampled=NavMesh.SamplePosition(p,out var n,.6f,NavMesh.AllAreas);var hits=Physics.OverlapCapsule(p+Vector3.up*.4f,p+Vector3.up*1.4f,.23f,WorldMotor.BlockMask,QueryTriggerInteraction.Ignore);edgeDiagnostics.Add("d="+d+" target="+p+" sampled="+sampled+" near="+n.position+" correction="+Vector3.Distance(p,n.position)+" body="+string.Join(";",hits.Select(h=>h.name+" "+h.bounds.center)));}File.WriteAllLines(Evidence+"/edge-geometry.txt",edgeDiagnostics);
  var results=new List<string>();float distance=0;var path=new NavMeshPath();
  for(int i=1;i<WorldLayout.Bends.Length;i++){var start=WorldLayout.Point(WorldLayout.Bends[i-1].y);var end=WorldLayout.Point(WorldLayout.Bends[i].y);bool ok=NavMesh.CalculatePath(start,end,NavMesh.AllAreas,path)&&path.status==NavMeshPathStatus.PathComplete;results.Add((ok?"PASS ":"FAIL ")+start+" -> "+end);if(ok)for(int j=1;j<path.corners.Length;j++)distance+=Vector3.Distance(path.corners[j-1],path.corners[j]);}
  AssetDatabase.SaveAssets();EditorSceneManager.SaveScene(scene);
  File.WriteAllText(Evidence+"/prepare.json",JsonUtility.ToJson(new RouteReport{distance=distance,walkSeconds=distance/2.25f,routes=results.ToArray(),objects=UnityEngine.Object.FindObjectsByType<Transform>().Length,triangles=terrain.GetComponentsInChildren<MeshFilter>().Sum(m=>m.sharedMesh.triangles.Length/3),missingScripts=UnityEngine.Object.FindObjectsByType<Transform>().Sum(t=>GameObjectUtility.GetMonoBehavioursWithMissingScriptCount(t.gameObject))},true));
  EditorApplication.Exit(results.Any(s=>s.StartsWith("FAIL"))?2:0);
 }catch(Exception e){Debug.LogException(e);EditorApplication.Exit(1);}}
 [Serializable]class BuildReportData{public string result,path;public int errors,warnings;public double seconds;public string[] messages;}
 public static void Build(){revision=Arg("-worldRevision","A01");Directory.CreateDirectory(Evidence);string path="Builds/VesperContinuousWorld_"+revision+"/VesperWorld.exe";var report=BuildPipeline.BuildPlayer(new BuildPlayerOptions{scenes=new[]{ScenePath},locationPathName=path,target=BuildTarget.StandaloneWindows64,options=BuildOptions.StrictMode});File.WriteAllText(Evidence+"/build.json",JsonUtility.ToJson(new BuildReportData{result=report.summary.result.ToString(),path=path,errors=report.summary.totalErrors,warnings=report.summary.totalWarnings,seconds=report.summary.totalTime.TotalSeconds,messages=report.steps.SelectMany(s=>s.messages).Where(m=>m.type==LogType.Error||m.type==LogType.Warning).Select(m=>m.content).Distinct().ToArray()},true));EditorApplication.Exit(report.summary.result==BuildResult.Succeeded?0:1);}
}
}
