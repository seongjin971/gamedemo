using System;
using System.IO;
using System.Linq;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.AI;
using UnityEngine.Rendering;
using Unity.AI.Navigation;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEditor.Build.Reporting;
using Object=UnityEngine.Object;
namespace Vesper.Expansion.WeatherWorld.Editor {
public static class WeatherBuild {
 const string Root="Assets/Vesper/Expansion/WeatherWorld";
 static string Revision=>Arg("-weatherRevision","W01");
 static string Generated=>Root+"/Generated/"+Revision;
 static string ScenePath=>"Assets/Vesper/Scenes/Expansion/VesperWeatherWorld_"+Revision+".unity";
 static string Evidence=>Path.GetFullPath("../../Migration/Evidence/Expansion/WeatherWorld/"+Revision);
 static string Arg(string key,string fallback){var a=Environment.GetCommandLineArgs();int i=Array.IndexOf(a,key);return i>=0&&i+1<a.Length?a[i+1]:fallback;}
 static int serial;
 static T Save<T>(T o,string name)where T:Object{AssetDatabase.CreateAsset(o,Generated+"/"+(serial++)+"-"+name+".asset");return o;}
 static Material Clone(Material source,Dictionary<Material,Material> copies){if(!source)return null;if(copies.TryGetValue(source,out var m))return m;m=new Material(source){name=source.name+" Weather"};Save(m,"Material");copies[source]=m;string s=source.shader.name;
  if(s=="Vesper/Linear/Ground")m.shader=Shader.Find("Vesper/Weather/Ground");
  if(s=="Vesper/Linear/Road/L09")m.shader=Shader.Find("Vesper/Weather/Road");
  if(s=="Vesper/Linear/WetStone")m.shader=Shader.Find("Vesper/Weather/WetStone");
  if(s=="Vesper/Linear/Precipitation")m.shader=Shader.Find("Vesper/Weather/Precipitation");
  if(s=="Vesper/WorldFoliage")m.shader=Shader.Find("Vesper/Weather/Foliage");
  if(m.HasProperty("_Wind"))m.SetFloat("_Wind",.10f);
  return m;
 }
 [Serializable]class PrepareReport{public string scene;public int originalColliders,colliders,meshes,materials,addedTrees,addedGroundClumps,missingScripts,audioSources;public float addedMetres;public string[] routes,roots;}
 public static void Prepare(){try{
  if(File.Exists(ScenePath)||Directory.Exists(Generated))throw new Exception("Refuse to overwrite candidate "+Revision);
  Directory.CreateDirectory(Generated);Directory.CreateDirectory(Evidence);
  string template=Path.GetFullPath("../../Migration/Evidence/Expansion/WeatherWorld/W01/scene-template.txt");
  File.Copy(template,ScenePath);AssetDatabase.Refresh();
  var scene=EditorSceneManager.OpenScene(ScenePath);serial=0;
  var world=Object.FindAnyObjectByType<WorldEnvironment>();if(!world||!world.player)throw new Exception("Remapped weather components missing");
  int before=Object.FindObjectsByType<Collider>().Length;
  var landscape=GameObject.Find("Authored linear landscape");
  var sourceTrees=landscape.transform.Cast<Transform>().Where(t=>t.name.Contains("CardedRiverBirch")&&-t.position.z>48&&-t.position.z<95).ToArray();
  var sourceGround=landscape.transform.Cast<Transform>().Where(t=>(t.name.Contains("LinearGrass")||t.name.Contains("CW_HF_Limestone"))&&-t.position.z>48&&-t.position.z<90).ToArray();
  var treeLocations=sourceTrees.ToDictionary(t=>t,t=>t.position);
  var groundLocations=sourceGround.ToDictionary(t=>t,t=>t.position);
  // Only world-space terrain and trail strips stretch; authored models retain their proportions.
  var warped=new HashSet<MeshFilter>();
  foreach(var mf in Object.FindObjectsByType<MeshFilter>())if(mf.name.StartsWith("Linear terrain ")||mf.name.StartsWith("Continuous trail ")){
   var mesh=Object.Instantiate(mf.sharedMesh);var v=mesh.vertices;var colors=mesh.colors;
   for(int i=0;i<v.Length;i++){var p=mf.transform.TransformPoint(v[i]);p=WorldLayout.Map(p);v[i]=mf.transform.InverseTransformPoint(p);if(colors.Length==v.Length&&mf.name.StartsWith("Linear terrain "))colors[i].a=WorldLayout.Weights(-p.z).y;}
   mesh.vertices=v;if(colors.Length==v.Length)mesh.colors=colors;mesh.RecalculateNormals();mesh.RecalculateBounds();Save(mesh,"ExtendedSurface");mf.sharedMesh=mesh;var mc=mf.GetComponent<MeshCollider>();if(mc)mc.sharedMesh=mesh;warped.Add(mf);
  }
  foreach(Transform t in landscape.transform)t.position=WorldLayout.Map(t.position);
  foreach(var t in Object.FindObjectsByType<Transform>().Where(t=>t.name=="Route boundary"))t.position=WorldLayout.Map(t.position);
  world.shelter=new Bounds(WorldLayout.Map(world.shelter.center),world.shelter.size);
  // Fill the physically added grove with the same authored birches, moss rocks and undergrowth.
  var grove=new GameObject("Added stormwatch grove - 48 metres");grove.transform.SetParent(landscape.transform,false);int trees=0,clumps=0;
  foreach(var pair in treeLocations){var p=pair.Value;float d=WorldLayout.FromSource(-p.z)+4.8f;if(d<60||d>131)continue;var go=Object.Instantiate(pair.Key.gameObject,grove.transform);go.name="Storm grove birch "+trees++;p.z=-d;p.x+=Mathf.Sign(p.x)*1.4f;p.y=WorldLayout.Height(p.x,d)-.10f;go.transform.position=p;go.transform.Rotate(0,77,0);go.transform.localScale*=.90f;}
  foreach(var pair in groundLocations){var p=pair.Value;float d=WorldLayout.FromSource(-p.z)+2.8f;if(d<55||d>137)continue;var go=Object.Instantiate(pair.Key.gameObject,grove.transform);go.name="Storm grove ground "+clumps++;float embed=Vesper.Expansion.LinearWorld.WorldLayout.Height(p.x,-p.z)-p.y;p.z=-d;p.y=WorldLayout.Height(p.x,d)-embed;go.transform.position=p;go.transform.Rotate(0,113,0);}
  var materials=new Dictionary<Material,Material>();foreach(var r in Object.FindObjectsByType<Renderer>())r.sharedMaterials=r.sharedMaterials.Select(m=>Clone(m,materials)).ToArray();
  world.skyMaterial=Clone(world.skyMaterial,materials);RenderSettings.skybox=world.skyMaterial;
  if(world.reflection)world.reflection.reflectedSkybox=world.skyMaterial;if(world.ruinsReflection)world.ruinsReflection.reflectedSkybox=world.skyMaterial;
  var profile=Object.Instantiate(world.volume.sharedProfile);profile.components=world.volume.sharedProfile.components.Select(c=>Object.Instantiate(c)).ToList();Save(profile,"WeatherGrade");foreach(var c in profile.components)AssetDatabase.AddObjectToAsset(c,profile);world.volume.sharedProfile=profile;
  ConfigureSnow(world.snow,0);world.nearSnow=Object.Instantiate(world.snow,world.snow.transform.parent);world.nearSnow.name="Blizzard near streaks";ConfigureSnow(world.nearSnow,1);
  world.spindrift=Object.Instantiate(world.snow,world.snow.transform.parent);world.spindrift.name="Wind swept low powder";ConfigureSnow(world.spindrift,2);
  // Separate navigation data is baked for the extension; old collider and navigation assets stay intact.
  var surface=Object.FindAnyObjectByType<NavMeshSurface>();surface.RemoveData();surface.navMeshData=null;Physics.SyncTransforms();surface.BuildNavMesh();if(!surface.navMeshData)throw new Exception("Weather route navigation missing");Save(surface.navMeshData,"WeatherNavigation");
  var path=new NavMeshPath();var route=new List<string>();var stops=new[]{0f,25,46,60,84,108,132,156,198,236,270,303,348};for(int i=1;i<stops.Length;i++){bool ok=NavMesh.CalculatePath(WorldLayout.Point(stops[i-1]),WorldLayout.Point(stops[i]),NavMesh.AllAreas,path)&&path.status==NavMeshPathStatus.PathComplete;route.Add((ok?"PASS ":"FAIL ")+stops[i-1]+" -> "+stops[i]);}
  int missing=Object.FindObjectsByType<Transform>().Sum(t=>GameObjectUtility.GetMonoBehavioursWithMissingScriptCount(t.gameObject));
  AssetDatabase.SaveAssets();EditorSceneManager.SaveScene(scene);
  File.WriteAllText(Evidence+"/prepare.json",JsonUtility.ToJson(new PrepareReport{scene=ScenePath,originalColliders=before,colliders=Object.FindObjectsByType<Collider>().Length,meshes=warped.Count,materials=materials.Count,addedTrees=trees,addedGroundClumps=clumps,addedMetres=48,missingScripts=missing,audioSources=Object.FindObjectsByType<AudioSource>().Length,routes=route.ToArray(),roots=scene.GetRootGameObjects().Select(g=>g.name).ToArray()},true));
  EditorApplication.Exit(missing==0&&route.All(r=>r.StartsWith("PASS"))?0:2);
 }catch(Exception e){Debug.LogException(e);EditorApplication.Exit(1);}}
 static void ConfigureSnow(ParticleSystem ps,int kind){
  ps.Stop(true,ParticleSystemStopBehavior.StopEmittingAndClear);var main=ps.main;main.maxParticles=kind==0?5000:kind==1?1400:120;main.startLifetime=kind==2?3.2f:3.4f;main.startSize=kind==0?new ParticleSystem.MinMaxCurve(.022f,.045f):kind==1?new ParticleSystem.MinMaxCurve(.045f,.085f):new ParticleSystem.MinMaxCurve(4.5f,8.5f);main.startColor=new Color(.78f,.86f,1,kind==2?.52f:.88f);
  if(kind==2){main.startSize3D=true;main.startSizeX=new ParticleSystem.MinMaxCurve(5,9);main.startSizeY=new ParticleSystem.MinMaxCurve(1.2f,2.8f);main.startSizeZ=1;}
  var shape=ps.shape;shape.scale=kind==2?new Vector3(16,.4f,26):new Vector3(28,4,32);
  var velocity=ps.velocityOverLifetime;velocity.x=kind==2?6:12;velocity.y=kind==2?.02f:-3.7f;velocity.z=2.5f;
  var collision=ps.collision;collision.enabled=kind==0;collision.quality=ParticleSystemCollisionQuality.Low;
  var noise=ps.noise;noise.enabled=kind!=2;noise.strength=kind==0?.25f:.4f;noise.frequency=.16f;noise.scrollSpeed=.55f;
  var renderer=ps.GetComponent<ParticleSystemRenderer>();renderer.renderMode=kind==2?ParticleSystemRenderMode.HorizontalBillboard:ParticleSystemRenderMode.Stretch;renderer.velocityScale=kind==2?0:.035f;renderer.lengthScale=kind==2?1:3.5f;
  var mat=new Material(renderer.sharedMaterial){name=ps.name};mat.SetFloat("_Kind",kind==2?3:1);mat.SetColor("_BaseColor",new Color(.73f,.83f,1,kind==2?.72f:1));Save(mat,"SnowMaterial");renderer.sharedMaterial=mat;
  var color=ps.colorOverLifetime;color.enabled=true;var gradient=new Gradient();gradient.SetKeys(new[]{new GradientColorKey(Color.white,0),new GradientColorKey(Color.white,1)},new[]{new GradientAlphaKey(0,0),new GradientAlphaKey(1,.15f),new GradientAlphaKey(.7f,.7f),new GradientAlphaKey(0,1)});color.color=gradient;
 }
 public static void Refine(){try{
  if(File.Exists(ScenePath)||Directory.Exists(Generated))throw new Exception("Refuse to overwrite candidate "+Revision);
  Directory.CreateDirectory(Generated);Directory.CreateDirectory(Evidence);AssetDatabase.Refresh();serial=0;
  var scene=EditorSceneManager.OpenScene("Assets/Vesper/Scenes/Expansion/VesperWeatherWorld_W01.unity");EditorSceneManager.SaveScene(scene,ScenePath,false);
  var world=Object.FindAnyObjectByType<WorldEnvironment>();var materials=new Dictionary<Material,Material>();foreach(var r in Object.FindObjectsByType<Renderer>())r.sharedMaterials=r.sharedMaterials.Select(m=>Clone(m,materials)).ToArray();
  world.skyMaterial=Clone(world.skyMaterial,materials);RenderSettings.skybox=world.skyMaterial;if(world.reflection)world.reflection.reflectedSkybox=world.skyMaterial;if(world.ruinsReflection)world.ruinsReflection.reflectedSkybox=world.skyMaterial;
  var profile=Object.Instantiate(world.volume.sharedProfile);profile.components=world.volume.sharedProfile.components.Select(c=>Object.Instantiate(c)).ToList();Save(profile,"WeatherGrade");foreach(var c in profile.components)AssetDatabase.AddObjectToAsset(c,profile);world.volume.sharedProfile=profile;
  ConfigureSnow(world.snow,0);ConfigureSnow(world.nearSnow,1);ConfigureSnow(world.spindrift,2);
  AssetDatabase.SaveAssets();EditorSceneManager.SaveScene(scene);File.WriteAllText(Evidence+"/refine.json","{\"source\":\"W01\",\"geometryChanged\":false,\"localizedDistantGlow\":true,\"layeredBlizzard\":true,\"audioSources\":"+Object.FindObjectsByType<AudioSource>().Length+"}");EditorApplication.Exit(0);
 }catch(Exception e){Debug.LogException(e);EditorApplication.Exit(1);}}
 [Serializable]class BuildData{public string result,path;public int errors,warnings;public double seconds;public string[] messages;}
 public static void Build(){try{Directory.CreateDirectory(Evidence);string path="Builds/VesperWeatherWorld_"+Revision+"/VesperLinear.exe";if(File.Exists(path))throw new Exception("Refuse to overwrite build "+path);var r=BuildPipeline.BuildPlayer(new BuildPlayerOptions{scenes=new[]{ScenePath},locationPathName=path,target=BuildTarget.StandaloneWindows64,options=BuildOptions.StrictMode});File.WriteAllText(Evidence+"/build.json",JsonUtility.ToJson(new BuildData{result=r.summary.result.ToString(),path=path,errors=r.summary.totalErrors,warnings=r.summary.totalWarnings,seconds=r.summary.totalTime.TotalSeconds,messages=r.steps.SelectMany(s=>s.messages).Where(m=>m.type==LogType.Error||m.type==LogType.Warning).Select(m=>m.content).Distinct().ToArray()},true));EditorApplication.Exit(r.summary.result==BuildResult.Succeeded?0:1);}catch(Exception e){Debug.LogException(e);EditorApplication.Exit(1);}}
}
}
