using System;
using System.IO;
using System.Linq;
using UnityEngine;
using UnityEditor;
using UnityEditor.Build.Reporting;
namespace Vesper.Editor {
 public static class VesperPlayerBuild {
  [Serializable]class PlayerBuildReport{public string result;public int errors,warnings;public double seconds;public string[] warningMessages;}
  static void SetFrameTiming(bool collect){var timing=typeof(PlayerSettings).GetProperty("enableFrameTimingStats",System.Reflection.BindingFlags.Static|System.Reflection.BindingFlags.Public);if(timing==null||!timing.CanWrite)throw new InvalidOperationException("FrameTiming PlayerSettings API unavailable");timing.SetValue(null,collect);Debug.Log("VESPER_FRAME_TIMING_ENABLED "+collect);}
  public static void CaptureCheckpoint(){SetFrameTiming(false);AssetDatabase.SaveAssets();VesperAtmosphereCapture.Run();}
  public static void Run(){SetFrameTiming(VesperAtmosphereCapture.Arg("-vesperFrameTiming","0")=="1");string output=Path.GetFullPath(VesperAtmosphereCapture.Arg("-vesperPlayerOutput","../../.dream-loop/unity-atmosphere-v2/player-v2/Vesper.exe"));Directory.CreateDirectory(Path.GetDirectoryName(output));var report=BuildPipeline.BuildPlayer(new BuildPlayerOptions{scenes=new[]{VesperAtmosphereBuild.Scene},locationPathName=output,target=BuildTarget.StandaloneWindows64,options=BuildOptions.StrictMode});File.WriteAllText(Path.Combine(Path.GetDirectoryName(output),"build-report.json"),JsonUtility.ToJson(new PlayerBuildReport{result=report.summary.result.ToString(),errors=report.summary.totalErrors,warnings=report.summary.totalWarnings,seconds=report.summary.totalTime.TotalSeconds,warningMessages=report.steps.SelectMany(step=>step.messages).Where(message=>message.type==LogType.Warning).Select(message=>message.content).Distinct().ToArray()},true));Debug.Log("VESPER_PLAYER_BUILD_"+report.summary.result);EditorApplication.Exit(report.summary.result==BuildResult.Succeeded?0:1);}
 }
}
