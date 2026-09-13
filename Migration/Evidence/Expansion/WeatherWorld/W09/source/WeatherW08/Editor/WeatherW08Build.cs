using System;
using System.IO;
using System.Linq;
using UnityEngine;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEditor.Build.Reporting;
using Vesper.Expansion.WeatherWorld;
using Vesper.Expansion.WeatherW07;
using Object=UnityEngine.Object;
namespace Vesper.Expansion.WeatherW08.Editor {
public static class WeatherW08Build {
 const string E="../../Migration/Evidence/Expansion/WeatherWorld/W08";
 const string Scene="Assets/Vesper/Scenes/Expansion/VesperWeatherWorld_W08.unity";
 [Serializable]class Built{public string result,path;public int errors,warnings;public double seconds;public string[] messages;}
 public static void PrepareAndBuild(){try{
  if(File.Exists(Scene)||Directory.Exists("Builds/VesperWeatherWorld_W08"))throw new Exception("Existing W08");
  Directory.CreateDirectory(E);AssetDatabase.Refresh();var scene=EditorSceneManager.OpenScene("Assets/Vesper/Scenes/Expansion/VesperWeatherWorld_W07.unity");EditorSceneManager.SaveScene(scene,Scene,false);
  var world=Object.FindAnyObjectByType<WorldEnvironment>();var flash=world.gameObject.AddComponent<WeatherW08Flash>();flash.world=world;flash.comparisonGate=Object.FindAnyObjectByType<WeatherW07Flash>();
  flash.screenMaterial=new Material(Shader.Find("Vesper/WeatherW08/ScreenFlash")){name="W08 screen flash"};AssetDatabase.CreateAsset(flash.screenMaterial,"Assets/Vesper/Expansion/WeatherW08/ScreenFlash.mat");AssetDatabase.SaveAssets();EditorSceneManager.SaveScene(scene);
  string path="Builds/VesperWeatherWorld_W08/VesperLinear.exe";var r=BuildPipeline.BuildPlayer(new BuildPlayerOptions{scenes=new[]{Scene},locationPathName=path,target=BuildTarget.StandaloneWindows64,options=BuildOptions.StrictMode});
  File.WriteAllText(E+"/build.json",JsonUtility.ToJson(new Built{result=r.summary.result.ToString(),path=path,errors=r.summary.totalErrors,warnings=r.summary.totalWarnings,seconds=r.summary.totalTime.TotalSeconds,messages=r.steps.SelectMany(s=>s.messages).Where(m=>m.type==LogType.Error||m.type==LogType.Warning).Select(m=>m.content).Distinct().ToArray()},true));EditorApplication.Exit(r.summary.result==BuildResult.Succeeded?0:1);
 }catch(Exception e){Debug.LogException(e);EditorApplication.Exit(1);}}
}
}
