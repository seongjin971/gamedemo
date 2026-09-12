using System;
using System.IO;
using System.Linq;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;
using UnityEditor;
using UnityEditor.SceneManagement;

namespace Vesper.Editor {
[InitializeOnLoad]
public static class VesperValidation {
    [Serializable]class SmokeResult {public float movedDistance;public bool validPosition;public int reflectionFrames;public string[] errors;}
    static VesperValidation(){EditorApplication.update+=Poll;}
    public static void Run(){
      EditorSceneManager.OpenScene("Assets/Vesper/Scenes/VesperMigrationSlice.unity");
      var nav=new VesperNavigation();int paths=0;
      if(nav.Valid(new Vector3(7.2f,0,3.7f))||nav.Valid(new Vector3(20,0,5)))throw new Exception("Navigation blocker/boundary failure");
      for(float x=-7;x<=7;x+=2)for(float z=0;z<=11;z+=2){var destination=new Vector3(x,0,z);if(!nav.Valid(destination))continue;var route=nav.Path(new Vector3(-2.25f,0,7.5f),destination);if(route.Count==0)throw new Exception("No route for valid destination");for(int i=0;i<route.Count;i++){if(!nav.Valid(route[i]))throw new Exception("Invalid route node");if(i>0)for(int s=1;s<10;s++)if(!nav.Valid(Vector3.Lerp(route[i-1],route[i],s/10f)))throw new Exception("Route crosses obstruction");}paths++;}
      int missing=UnityEngine.Object.FindObjectsByType<Transform>().Sum(t=>GameObjectUtility.GetMonoBehavioursWithMissingScriptCount(t.gameObject));if(missing!=0)throw new Exception("Missing scripts");
      foreach(var r in UnityEngine.Object.FindObjectsByType<MeshRenderer>())foreach(var m in r.sharedMaterials)if(!m||!m.shader||m.shader.name=="Hidden/InternalErrorShader")throw new Exception("Invalid material");
      var profile=UnityEngine.Object.FindAnyObjectByType<Volume>().sharedProfile;
      if(!profile||profile.components.Count!=3||profile.components.Any(c=>!c||!AssetDatabase.Contains(c))||!profile.TryGet<Tonemapping>(out var tone)||tone.mode.value!=TonemappingMode.ACES)throw new Exception("Saved volume overrides are invalid");
      Directory.CreateDirectory("../../.dream-loop/unity-migration");File.WriteAllText("../../.dream-loop/unity-migration/validation.json","{\"navigationRoutes\":"+paths+",\"missingScripts\":"+missing+",\"materialsValid\":true,\"savedVolumeOverrides\":3}");Debug.Log("VESPER_VALIDATION_PASS routes="+paths);
    }
    public static void PlaySmoke(){Run();var result=Path.GetFullPath("../../.dream-loop/unity-migration/play-smoke.json");if(File.Exists(result))File.Copy(result,result+".previous",true);if(File.Exists(result))File.Delete(result);SessionState.SetString("VesperSmokeResult",result);SessionState.SetFloat("VesperSmokeStart",(float)EditorApplication.timeSinceStartup);Environment.SetEnvironmentVariable("VESPER_PLAY_SMOKE",result);EditorApplication.isPlaying=true;}
    static void Poll(){var path=SessionState.GetString("VesperSmokeResult","");if(string.IsNullOrEmpty(path))return;
      if(File.Exists(path)){SessionState.EraseString("VesperSmokeResult");Environment.SetEnvironmentVariable("VESPER_PLAY_SMOKE",null);int code=3;
        try {var report=JsonUtility.FromJson<SmokeResult>(File.ReadAllText(path));if(report!=null&&report.validPosition&&report.movedDistance>1&&report.reflectionFrames>=2&&report.errors!=null&&report.errors.Length==0)code=0;}catch(Exception e){Debug.LogException(e);}
        Debug.Log(code==0?"VESPER_PLAY_SMOKE_PASS":"VESPER_PLAY_SMOKE_FAIL");EditorApplication.isPlaying=false;int exitCode=code;EditorApplication.delayCall+=()=>EditorApplication.Exit(exitCode);}
      else if(EditorApplication.timeSinceStartup-SessionState.GetFloat("VesperSmokeStart",0)>90){Debug.LogError("VESPER_PLAY_SMOKE_TIMEOUT");SessionState.EraseString("VesperSmokeResult");EditorApplication.Exit(3);}
    }
}
}
