using System;
using System.IO;
using System.Linq;
using System.Collections.Generic;
using UnityEngine;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEditor.Build.Reporting;
using Vesper.Expansion.WeatherWorld;
using Object=UnityEngine.Object;
namespace Vesper.Expansion.WeatherW07.Editor {
public static class WeatherW07Build {
 const string E="../../Migration/Evidence/Expansion/WeatherWorld/W07";
 const string Scene="Assets/Vesper/Scenes/Expansion/VesperWeatherWorld_W07.unity";
 const string Generated="Assets/Vesper/Expansion/WeatherW07/Generated";
 [Serializable] class Item{public string name,path;public Vector3 position,scale,min,max;public string[] materials;}
 [Serializable] class Inspection{public Bounds shelter;public Item[] items;}
 static string PathOf(Transform t)=>t.parent?PathOf(t.parent)+"/"+t.name:t.name;
 public static void Inspect(){try{
  if(File.Exists(E+"/inspection.json"))throw new Exception("Existing inspection");
  EditorSceneManager.OpenScene("Assets/Vesper/Scenes/Expansion/VesperWeatherWorld_W06.unity");
  var world=Object.FindAnyObjectByType<WorldEnvironment>();
  var items=Object.FindObjectsByType<MeshRenderer>().Where(r=>r.name.Contains("Chapel")||r.transform.parent&&r.transform.parent.name.Contains("Chapel")).Select(r=>new Item{name=r.name,path=PathOf(r.transform),position=r.transform.position,scale=r.transform.lossyScale,min=r.bounds.min,max=r.bounds.max,materials=r.sharedMaterials.Select(m=>m?m.name+" | "+m.shader.name+" | "+AssetDatabase.GetAssetPath(m):"null").ToArray()}).ToArray();
  File.WriteAllText(E+"/inspection.json",JsonUtility.ToJson(new Inspection{shelter=world.shelter,items=items},true));EditorApplication.Exit(0);
 }catch(Exception e){Debug.LogException(e);EditorApplication.Exit(1);}}
 static void Beam(Transform parent,string name,Vector3 start,Vector3 end,float width,float depth,Material material){
  // An exact octagonal chamfered timber joint, using the existing authored timber atlas.
  var go=new GameObject(name);go.transform.SetParent(parent,false);go.transform.position=start;go.transform.rotation=Quaternion.FromToRotation(Vector3.forward,(end-start).normalized);
  float x=width*.5f,y=depth*.5f,c=Mathf.Min(width,depth)*.10f,len=Vector3.Distance(start,end);
  var ring=new[]{new Vector2(-x+c,-y),new Vector2(x-c,-y),new Vector2(x,-y+c),new Vector2(x,y-c),new Vector2(x-c,y),new Vector2(-x+c,y),new Vector2(-x,y-c),new Vector2(-x,-y+c)};
  var v=new List<Vector3>();var uv=new List<Vector2>();var tri=new List<int>();
  for(int i=0;i<8;i++){var a=ring[i];var b=ring[(i+1)%8];int n=v.Count;v.AddRange(new[]{new Vector3(a.x,a.y,0),new Vector3(b.x,b.y,0),new Vector3(b.x,b.y,len),new Vector3(a.x,a.y,len)});uv.AddRange(new[]{new Vector2(0,0),new Vector2(1,0),new Vector2(1,1),new Vector2(0,1)});tri.AddRange(new[]{n,n+1,n+2,n,n+2,n+3});}
  for(int endIndex=0;endIndex<2;endIndex++){int n=v.Count;v.Add(new Vector3(0,0,endIndex*len));uv.Add(new Vector2(.5f,.5f));foreach(var p in ring){v.Add(new Vector3(p.x,p.y,endIndex*len));uv.Add(new Vector2(p.x/width+.5f,p.y/depth+.5f));}for(int i=0;i<8;i++){int a=n+1+i,b=n+1+(i+1)%8;tri.AddRange(endIndex==0?new[]{n,b,a}:new[]{n,a,b});}}
  var mesh=new Mesh{name=name};mesh.SetVertices(v);mesh.SetUVs(0,uv);mesh.SetTriangles(tri,0);mesh.RecalculateNormals();mesh.RecalculateBounds();AssetDatabase.CreateAsset(mesh,Generated+"/"+name+".asset");go.AddComponent<MeshFilter>().sharedMesh=mesh;go.AddComponent<MeshRenderer>().sharedMaterial=material;
 }
 [Serializable] class Prepared{public string source;public int collidersBefore,collidersAfter,missingScripts,audioSources;public Vector3 originalRoofPosition,newRoofPosition,newRoofScale;public Bounds shelter;}
 public static void Prepare(){try{
  if(File.Exists(Scene)||Directory.Exists(Generated))throw new Exception("Refuse to overwrite W07");
  Directory.CreateDirectory(Generated);AssetDatabase.Refresh();var scene=EditorSceneManager.OpenScene("Assets/Vesper/Scenes/Expansion/VesperWeatherWorld_W06.unity");EditorSceneManager.SaveScene(scene,Scene,false);
  int colliderCount=Object.FindObjectsByType<Collider>().Length;var world=Object.FindAnyObjectByType<WorldEnvironment>();
  var roof=GameObject.Find("ChapelSurfaces/CW_ChapelBrokenSlateRoof6x8m");if(!roof)roof=Object.FindObjectsByType<Transform>().First(t=>t.name=="ChapelSurfaces/CW_ChapelBrokenSlateRoof6x8m").gameObject;
  var prior=roof.GetComponent<WorldRoofCutaway>();if(prior)Object.DestroyImmediate(prior);
  var corrected=Object.Instantiate(roof,roof.transform.parent);corrected.name="W07 seated slate canopy";
  foreach(var c in corrected.GetComponentsInChildren<Collider>())Object.DestroyImmediate(c);
  corrected.transform.position=new Vector3(6.80f,7.20f,-195.5f);corrected.transform.localScale=new Vector3(.80f,.7f,.50f);
  var copies=new Dictionary<Material,Material>();foreach(var r in corrected.GetComponentsInChildren<Renderer>())r.sharedMaterials=r.sharedMaterials.Select(m=>{if(copies.TryGetValue(m,out var copy))return copy;copy=new Material(m){name="W07 "+m.name};AssetDatabase.CreateAsset(copy,Generated+"/"+copy.name+".mat");copies.Add(m,copy);return copy;}).ToArray();
  foreach(var r in roof.GetComponentsInChildren<Renderer>())r.enabled=false;
  var frame=new GameObject("W07 canopy joints");frame.transform.SetParent(corrected.transform,false);frame.transform.SetPositionAndRotation(Vector3.zero,Quaternion.identity);frame.transform.localScale=new Vector3(1/.8f,1/.7f,1/.5f);
  var timber=corrected.GetComponentInChildren<Renderer>().sharedMaterials.First();
  Beam(frame.transform,"Arch wall plate",new Vector3(4.60f,7.035f,-197.60f),new Vector3(4.60f,7.035f,-193.40f),.26f,.20f,timber);
  Beam(frame.transform,"Pier wall plate",new Vector3(9f,6.87f,-197.60f),new Vector3(9f,6.87f,-193.40f),.30f,.34f,timber);
  foreach(float z in new[]{-194f,-197f})Beam(frame.transform,"Tie beam "+(-z),new Vector3(4.55f,7.01f,z),new Vector3(9.06f,7.01f,z),.22f,.24f,timber);
  Beam(frame.transform,"Arch cantilever brace",new Vector3(4.60f,6.18f,-195.55f),new Vector3(4.60f,6.98f,-194.26f),.19f,.19f,timber);
  foreach(float z in new[]{-194f,-197f})Beam(frame.transform,"Pier knee brace "+(-z),new Vector3(9f,6.10f,z),new Vector3(8.15f,6.94f,z),.18f,.18f,timber);
  corrected.AddComponent<WeatherW07Roof>().world=world;
  var flash=world.gameObject.AddComponent<WeatherW07Flash>();flash.world=world;
  var variants=world.gameObject.AddComponent<WeatherW07Variant>();variants.originalRoof=roof;variants.correctedRoof=corrected;variants.flash=flash;
  AssetDatabase.SaveAssets();EditorSceneManager.SaveScene(scene);
  var data=new Prepared{source="W06",collidersBefore=colliderCount,collidersAfter=Object.FindObjectsByType<Collider>().Length,missingScripts=Object.FindObjectsByType<Transform>().Sum(t=>GameObjectUtility.GetMonoBehavioursWithMissingScriptCount(t.gameObject)),audioSources=Object.FindObjectsByType<AudioSource>().Length,originalRoofPosition=roof.transform.position,newRoofPosition=corrected.transform.position,newRoofScale=corrected.transform.localScale,shelter=world.shelter};
  File.WriteAllText(E+"/prepare.json",JsonUtility.ToJson(data,true));EditorApplication.Exit(data.missingScripts==0&&data.collidersBefore==data.collidersAfter?0:1);
 }catch(Exception e){Debug.LogException(e);EditorApplication.Exit(1);}}
 [Serializable] class Built{public string result,path;public int errors,warnings;public double seconds;public string[] messages;}
 public static void Build(){try{
  string path="Builds/VesperWeatherWorld_W07/VesperLinear.exe";if(File.Exists(path))throw new Exception("Existing W07 build");
  var scene=EditorSceneManager.OpenScene(Scene);
  var joints=GameObject.Find("W07 canopy joints");var timber=AssetDatabase.LoadAssetAtPath<Material>(Generated+"/W07 22-Material.mat");
  if(!joints||!timber)throw new Exception("Canopy timber missing");foreach(var renderer in joints.GetComponentsInChildren<Renderer>())renderer.sharedMaterial=timber;
  EditorSceneManager.SaveScene(scene);File.WriteAllText(E+"/timber-material.json","{\"source\":\"W06 22-Material timber slot\",\"joints\":7}");
  var r=BuildPipeline.BuildPlayer(new BuildPlayerOptions{scenes=new[]{Scene},locationPathName=path,target=BuildTarget.StandaloneWindows64,options=BuildOptions.StrictMode});
  File.WriteAllText(E+"/build.json",JsonUtility.ToJson(new Built{result=r.summary.result.ToString(),path=path,errors=r.summary.totalErrors,warnings=r.summary.totalWarnings,seconds=r.summary.totalTime.TotalSeconds,messages=r.steps.SelectMany(s=>s.messages).Where(m=>m.type==LogType.Error||m.type==LogType.Warning).Select(m=>m.content).Distinct().ToArray()},true));EditorApplication.Exit(r.summary.result==BuildResult.Succeeded?0:1);
 }catch(Exception e){Debug.LogException(e);EditorApplication.Exit(1);}}
}
}
