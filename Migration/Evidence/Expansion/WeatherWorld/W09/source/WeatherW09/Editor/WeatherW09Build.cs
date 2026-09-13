using System;
using System.IO;
using System.Linq;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEditor.Build.Reporting;
using Vesper.Expansion.WeatherW07;
using Object=UnityEngine.Object;
namespace Vesper.Expansion.WeatherW09.Editor {
public static class WeatherW09Build {
 const string E="../../Migration/Evidence/Expansion/WeatherWorld/W09";
 const string Scene="Assets/Vesper/Scenes/Expansion/VesperWeatherWorld_W09.unity";
 [Serializable]class Built{public string result,path;public int errors,warnings;public double seconds;public string[] messages;}
 public static void PrepareAndBuild(){try{
  if(File.Exists(Scene)||Directory.Exists("Builds/VesperWeatherWorld_W09"))throw new Exception("Existing W09");
  Directory.CreateDirectory(E);Directory.CreateDirectory("Assets/Vesper/Expansion/WeatherW09/Materials");AssetDatabase.Refresh();var scene=EditorSceneManager.OpenScene("Assets/Vesper/Scenes/Expansion/VesperWeatherWorld_W08.unity");EditorSceneManager.SaveScene(scene,Scene,false);
  var variant=Object.FindAnyObjectByType<WeatherW07Variant>();var copies=new Dictionary<Material,Material>();
  foreach(var renderer in variant.correctedRoof.GetComponentsInChildren<Renderer>())renderer.sharedMaterials=renderer.sharedMaterials.Select(m=>{
   if(copies.TryGetValue(m,out var copy))return copy;copy=new Material(m){name="W09 "+m.name};
   // Include the genuine URP transparent shader variant in this new player. At runtime
   // WeatherW07Roof returns to opaque depth before the first ordinary frame.
   copy.SetFloat("_Surface",1);copy.SetFloat("_SrcBlend",(float)BlendMode.SrcAlpha);copy.SetFloat("_DstBlend",(float)BlendMode.OneMinusSrcAlpha);copy.SetFloat("_ZWrite",0);copy.EnableKeyword("_SURFACE_TYPE_TRANSPARENT");copy.renderQueue=3000;
   AssetDatabase.CreateAsset(copy,"Assets/Vesper/Expansion/WeatherW09/Materials/"+copy.name+".mat");copies[m]=copy;return copy;
  }).ToArray();
  AssetDatabase.SaveAssets();EditorSceneManager.SaveScene(scene);
  string path="Builds/VesperWeatherWorld_W09/VesperLinear.exe";var r=BuildPipeline.BuildPlayer(new BuildPlayerOptions{scenes=new[]{Scene},locationPathName=path,target=BuildTarget.StandaloneWindows64,options=BuildOptions.StrictMode});
  File.WriteAllText(E+"/build.json",JsonUtility.ToJson(new Built{result=r.summary.result.ToString(),path=path,errors=r.summary.totalErrors,warnings=r.summary.totalWarnings,seconds=r.summary.totalTime.TotalSeconds,messages=r.steps.SelectMany(s=>s.messages).Where(m=>m.type==LogType.Error||m.type==LogType.Warning).Select(m=>m.content).Distinct().ToArray()},true));EditorApplication.Exit(r.summary.result==BuildResult.Succeeded?0:1);
 }catch(Exception e){Debug.LogException(e);EditorApplication.Exit(1);}}
}
}
