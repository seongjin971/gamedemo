using System;
using System.IO;
using System.Linq;
using UnityEngine;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEditor.Build.Reporting;
namespace Vesper.Expansion.WeatherW10.Editor {
public static class WeatherW10Build {
 const string E="../../Migration/Evidence/Expansion/WeatherWorld/W10";
 const string Scene="Assets/Vesper/Scenes/Expansion/VesperWeatherWorld_W10.unity";
 [Serializable] class Built { public string result,path; public int errors,warnings; public double seconds; public string[] messages; }
 public static void PrepareAndBuild(){try{
  if(File.Exists(Scene)||Directory.Exists("Builds/VesperWeatherWorld_W10"))throw new Exception("Existing W10 is preserved");
  AssetDatabase.Refresh();
  if(!AssetDatabase.CopyAsset("Assets/Vesper/Scenes/Expansion/VesperWeatherWorld_W09.unity",Scene))throw new Exception("Scene copy failed");
  string text=File.ReadAllText(Scene);
  foreach(string file in Directory.GetFiles("Assets/Vesper/Expansion/WeatherW10/Runtime","*.cs")){
   string name=Path.GetFileName(file),old=null;
   foreach(string version in new[]{"WeatherWorld","WeatherW07","WeatherW08"}){
    string candidate="Assets/Vesper/Expansion/"+version+"/Runtime/"+name;
    if(File.Exists(candidate)){old=candidate;break;}
   }
   if(old==null)continue;
   string from=AssetDatabase.AssetPathToGUID(old),to=AssetDatabase.AssetPathToGUID(file);
   if(string.IsNullOrEmpty(from)||string.IsNullOrEmpty(to))throw new Exception("Missing script GUID "+file);
   text=text.Replace("guid: "+from,"guid: "+to);
  }
  File.WriteAllText(Scene,text);AssetDatabase.ImportAsset(Scene,ImportAssetOptions.ForceUpdate);
  var scene=EditorSceneManager.OpenScene(Scene);
  if(!UnityEngine.Object.FindAnyObjectByType<WorldCamera>()||!UnityEngine.Object.FindAnyObjectByType<WorldEnvironment>()||!UnityEngine.Object.FindAnyObjectByType<WorldMotor>())throw new Exception("Versioned references failed");
  foreach(var go in scene.GetRootGameObjects())foreach(var t in go.GetComponentsInChildren<Transform>(true))if(GameObjectUtility.GetMonoBehavioursWithMissingScriptCount(t.gameObject)>0)throw new Exception("Missing script "+t.name);
  // Do not save/rewrite the loaded scene: preserve every original serialized value.
  string path="Builds/VesperWeatherWorld_W10/VesperLinear.exe";
  var r=BuildPipeline.BuildPlayer(new BuildPlayerOptions{scenes=new[]{Scene},locationPathName=path,target=BuildTarget.StandaloneWindows64,options=BuildOptions.StrictMode});
  File.WriteAllText(E+"/build.json",JsonUtility.ToJson(new Built{result=r.summary.result.ToString(),path=path,errors=r.summary.totalErrors,warnings=r.summary.totalWarnings,seconds=r.summary.totalTime.TotalSeconds,messages=r.steps.SelectMany(s=>s.messages).Where(m=>m.type==LogType.Error||m.type==LogType.Warning).Select(m=>m.content).Distinct().ToArray()},true));
  EditorApplication.Exit(r.summary.result==BuildResult.Succeeded?0:1);
 }catch(Exception e){Debug.LogException(e);EditorApplication.Exit(1);}}
}
}
