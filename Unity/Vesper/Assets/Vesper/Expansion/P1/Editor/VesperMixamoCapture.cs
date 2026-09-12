// Expansion-only capture fork with explicit GPU and scene cleanup. Original capture is preserved.
using System;
using System.IO;
using System.Linq;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;
using UnityEditor;
using UnityEditor.SceneManagement;

namespace Vesper.Editor {
public static class VesperMixamoCapture {
 static VesperPlanarReflection reflectionProbe;static Camera camera;static RenderTexture target;static int frame,index;static string output;
 static readonly List<string> errors=new List<string>();
 static void StoneDiagnostic(){string water=Arg("-vesperWaterDiagnostic","");Shader.SetGlobalFloat("_VesperWaterDiagnostic",water=="coverage"?1:water=="reflection"?2:water=="direct"?3:0);string mode=Arg("-vesperDiagnostic","");Shader.SetGlobalFloat("_VesperStoneDiagnostic",mode=="albedo"?1:mode=="normals"?2:mode=="indirect"?3:mode=="moon"?4:mode=="points"?5:0);}
 public static string Arg(string key,string fallback){var a=Environment.GetCommandLineArgs();int i=Array.IndexOf(a,key);return i>=0&&i+1<a.Length?a[i+1]:fallback;}
 public static void Run(){output=Path.GetFullPath(Arg("-vesperOutput","../../.dream-loop/unity-atmosphere-v2/round-1"));Directory.CreateDirectory(output);EditorSceneManager.OpenScene(Arg("-vesperScene",Vesper.Expansion.Editor.MixamoAdventurerBuild.Scene));camera=Camera.main;reflectionProbe=UnityEngine.Object.FindAnyObjectByType<VesperPlanarReflection>();Shader.SetGlobalFloat("_VesperShadowDiagnostic",Arg("-vesperDiagnostic","")=="shadow"?1:0);if(Arg("-vesperDiagnostic","")=="no-reflection")reflectionProbe.enabled=false;if(Arg("-vesperDiagnostic","")=="no-mist")foreach(var r in UnityEngine.Object.FindObjectsByType<Renderer>())if(r.sharedMaterial&&r.sharedMaterial.shader.name=="Vesper/ValleyMist")r.enabled=false;errors.Clear();Application.logMessageReceived+=Log;index=0;Setup();EditorApplication.update+=Tick;}
 static void Log(string m,string s,LogType t){if(t==LogType.Error||t==LogType.Exception||t==LogType.Assert)errors.Add(m);}
 static void Setup(){VesperDepthPrimingDiagnostic.Apply();VesperShadowDiagnostics.Apply();StoneDiagnostic();if(target){camera.targetTexture=null;target.Release();UnityEngine.Object.DestroyImmediate(target);}bool slice=index==0;int w=slice?1037:1536,h=slice?739:1024;target=new RenderTexture(w,h,24,RenderTextureFormat.ARGB32);target.Create();camera.targetTexture=target;camera.aspect=(float)w/h;
  if(slice){var b=JsonUtility.FromJson<Bridge>(File.ReadAllText("Assets/Vesper/Import/unity-scene.json"));camera.orthographicSize=b.camera.orthoHeight*.5f;camera.transform.position=new Vector3(-b.camera.position[0],b.camera.position[1],b.camera.position[2]);camera.transform.LookAt(new Vector3(-b.camera.target[0],b.camera.target[1],b.camera.target[2]));}
  else {float a=index==2?.70f:.46f,e=index==2?.85f:.72f;camera.orthographicSize=index==3?8.8f:14.1f/1.27f;var focus=new Vector3(0,2.9f,.7f);camera.transform.position=focus+new Vector3(-Mathf.Sin(a)*Mathf.Cos(e),Mathf.Sin(e),Mathf.Cos(a)*Mathf.Cos(e))*42;camera.transform.LookAt(focus);}
  // Reproduce the camera that exposed the broad floor glare in player41 frame0129.
  if((index==2&&Arg("-vesperGlareOrbit","0")=="1")||index==4){camera.orthographicSize=11.1023626f;camera.transform.position=new Vector3(-27.1694241f,31.0741272f,15.9328890f);float a=1.05980349f,e=.73530388f;camera.transform.rotation=Quaternion.LookRotation(new Vector3(Mathf.Sin(a)*Mathf.Cos(e),-Mathf.Sin(e),-Mathf.Cos(a)*Mathf.Cos(e)));}
  foreach(var b in UnityEngine.Object.FindObjectsByType<VesperBillboard>())b.transform.rotation=camera.transform.rotation;
  foreach(var ps in UnityEngine.Object.FindObjectsByType<ParticleSystem>())ps.Simulate(2.3f,true,true);
  frame=0;
 }
 static void Tick(){try{if(++frame<20){EditorApplication.QueuePlayerLoopUpdate();return;}Shader.SetGlobalVector("_Time",new Vector4(.115f,2.3f,4.6f,6.9f));RenderPipeline.SubmitRenderRequest(camera,new UniversalRenderPipeline.SingleCameraRequest{destination=target});if(frame<25)return;
  var active=RenderTexture.active;RenderTexture.active=target;var png=new Texture2D(target.width,target.height,TextureFormat.RGB24,false);png.ReadPixels(new Rect(0,0,target.width,target.height),0,0);png.Apply();File.WriteAllBytes(output+"/"+new[]{"slice","full","orbit","zoom","glare-orbit"}[index]+".png",png.EncodeToPNG());UnityEngine.Object.DestroyImmediate(png);RenderTexture.active=active;
  if(reflectionProbe.ReflectionTexture!=null){var rt=reflectionProbe.ReflectionTexture;var prev=RenderTexture.active;RenderTexture.active=rt;var tex=new Texture2D(rt.width,rt.height,TextureFormat.RGB24,false);tex.ReadPixels(new Rect(0,0,rt.width,rt.height),0,0);tex.Apply();byte[] reflectionBytes=tex.EncodeToPNG();File.WriteAllBytes(output+"/reflection-"+new[]{"slice","full","orbit","zoom","glare-orbit"}[index]+".png",reflectionBytes);if(index==0)File.WriteAllBytes(output+"/reflection.png",reflectionBytes);UnityEngine.Object.DestroyImmediate(tex);RenderTexture.active=prev;}
  if(Arg("-vesperHDRDiagnostic","0")=="1"&&reflectionProbe.ReflectionTexture)CaptureReflectionRadiance();
  if(++index<(Arg("-vesperIncludeGlare","0")=="1"?5:4)){Setup();return;}
  int shaderErrors=new[]{"Vesper/AtmosphereStone","Vesper/AtmosphereBackdrop","Vesper/ValleyMist","Vesper/AtmosphereFlame","Vesper/ShallowWater","Vesper/StandingWater","Vesper/ReflectionSky","Vesper/RuneGlow"}.Sum(n=>ShaderUtil.GetShaderMessages(Shader.Find(n)).Count(m=>m.severity==UnityEditor.Rendering.ShaderCompilerMessageSeverity.Error));
  int missing=UnityEngine.Object.FindObjectsByType<Transform>().Sum(t=>GameObjectUtility.GetMonoBehavioursWithMissingScriptCount(t.gameObject));var reflection=UnityEngine.Object.FindAnyObjectByType<VesperPlanarReflection>();
  var report=new Report{waterDiagnostic=Arg("-vesperWaterDiagnostic",""),unpartitionedFireCasters=Environment.GetCommandLineArgs().Contains("-vesperUnpartitionedFireCasters"),fullFireCasters=Environment.GetCommandLineArgs().Contains("-vesperFullFireCasters"),glareOrbit=Arg("-vesperGlareOrbit","0")=="1",rootHullPoints=UnityEngine.Object.FindObjectsByType<VesperNavigationObstacle>().Sum(o=>o.worldPolygon.Length),localShadowTriangles=UnityEngine.Object.FindObjectsByType<MeshRenderer>().Where(r=>r.enabled&&r.name.StartsWith("Exact local fire shadow ")&&r.shadowCastingMode!=ShadowCastingMode.Off).Sum(r=>r.GetComponent<MeshFilter>().sharedMesh.triangles.Length/3),diagnostic=Arg("-vesperDiagnostic",""),scene=UnityEngine.SceneManagement.SceneManager.GetActiveScene().path,shaderErrors=shaderErrors,missingScripts=missing,errors=errors.ToArray(),reflectionFrames=reflection.RenderedFrameCount,device=SystemInfo.graphicsDeviceName};File.WriteAllText(output+"/capture.json",JsonUtility.ToJson(report,true));bool pass=shaderErrors==0&&missing==0&&errors.Count==0&&(reflection.RenderedFrameCount>0||Arg("-vesperDiagnostic","")=="no-reflection");Debug.Log(pass?"VESPER_ATMOSPHERE_CAPTURE_PASS":"VESPER_ATMOSPHERE_CAPTURE_FAIL");EditorApplication.update-=Tick;Application.logMessageReceived-=Log;camera.targetTexture=null;RenderTexture.active=null;reflectionProbe.enabled=false;target.Release();UnityEngine.Object.DestroyImmediate(target);EditorSceneManager.NewScene(NewSceneSetup.EmptyScene,NewSceneMode.Single);exitCode=pass?0:1;cleanupFrames=0;EditorApplication.update+=Finish;
 }catch(Exception e){Debug.LogException(e);EditorApplication.update-=Tick;EditorApplication.Exit(2);}}
 static int cleanupFrames,exitCode;
 static void Finish(){EditorApplication.QueuePlayerLoopUpdate();if(++cleanupFrames<30)return;EditorApplication.update-=Finish;EditorApplication.Exit(exitCode);}
 static void CaptureReflectionRadiance(){
  var rt=reflectionProbe.ReflectionTexture;var previous=RenderTexture.active;
  var linear=new Texture2D(rt.width,rt.height,TextureFormat.RGBAFloat,false,true);
  try{
   RenderTexture.active=rt;linear.ReadPixels(new Rect(0,0,rt.width,rt.height),0,0);linear.Apply();
   var pixels=linear.GetPixels();var r=new RadianceReport{note="Linear floating-point reflection target before main-camera water blending and tone mapping. PNG is not used for radiance measurement.",format=rt.graphicsFormat.ToString(),width=rt.width,height=rt.height};
   for(int pixel=0;pixel<pixels.Length;pixel++){Color c=pixels[pixel];float luminance=c.r*.2126f+c.g*.7152f+c.b*.0722f;if(luminance>r.peakLuminance){r.peakLuminance=luminance;r.peakRGB=c;r.peakX=pixel%rt.width;r.peakY=pixel/rt.width;}if(luminance>1)r.pixelsAboveOne++;if(luminance>4)r.pixelsAboveFour++;}
   string view=new[]{"slice","full","orbit","zoom","glare-orbit"}[index];File.WriteAllText(output+"/reflection-radiance-"+view+".json",JsonUtility.ToJson(r,true));File.WriteAllBytes(output+"/reflection-linear-"+view+".exr",linear.EncodeToEXR(Texture2D.EXRFlags.OutputAsFloat));
  }finally{RenderTexture.active=previous;UnityEngine.Object.DestroyImmediate(linear);}
 }
 [Serializable]class RadianceReport{public string note,format;public int width,height,peakX,peakY,pixelsAboveOne,pixelsAboveFour;public float peakLuminance;public Color peakRGB;}
 [Serializable]class Report{public string scene,device,diagnostic,waterDiagnostic;public bool fullFireCasters,unpartitionedFireCasters,glareOrbit;public int shaderErrors,missingScripts,reflectionFrames,rootHullPoints,localShadowTriangles;public string[] errors;}
}
}
