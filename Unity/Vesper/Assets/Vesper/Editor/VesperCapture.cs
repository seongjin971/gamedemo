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
public static class VesperCapture {
    public static void BuildAndRun(){VesperImport.Build();Run();}
    static int frames;static string output;static RenderTexture target;static Camera camera;
    static readonly List<string> errors=new List<string>();
    static void Log(string message,string stack,LogType type){if(type==LogType.Error||type==LogType.Exception||type==LogType.Assert)errors.Add(message);}
    public static void Run(){
      VesperValidation.Run();errors.Clear();Application.logMessageReceived+=Log;
      EditorSceneManager.OpenScene("Assets/Vesper/Scenes/VesperMigrationSlice.unity");
      var data=JsonUtility.FromJson<Bridge>(File.ReadAllText("Assets/Vesper/Import/unity-scene.json"));
      camera=Camera.main;target=new RenderTexture(data.camera.width,data.camera.height,24,RenderTextureFormat.ARGB32){antiAliasing=1};target.Create();camera.targetTexture=target;camera.aspect=(float)target.width/target.height;
      output=Path.GetFullPath("../../.dream-loop/unity-migration");Directory.CreateDirectory(output);
      frames=0;EditorApplication.update+=Tick;
    }
    static void Tick(){try{
      if(++frames<30){EditorApplication.QueuePlayerLoopUpdate();return;}
      var request=new UniversalRenderPipeline.SingleCameraRequest{destination=target};RenderPipeline.SubmitRenderRequest(camera,request);
      if(frames<35)return;
      var old=RenderTexture.active;RenderTexture.active=target;var png=new Texture2D(target.width,target.height,TextureFormat.RGB24,false);png.ReadPixels(new Rect(0,0,target.width,target.height),0,0);png.Apply();RenderTexture.active=old;
      File.WriteAllBytes(output+"/unity-slice.png",png.EncodeToPNG());UnityEngine.Object.DestroyImmediate(png);
      int shaderErrors=new[]{"Vesper/WetStone","Vesper/Flame"}.Sum(name=>ShaderUtil.GetShaderMessages(Shader.Find(name)).Count(m=>m.severity==UnityEditor.Rendering.ShaderCompilerMessageSeverity.Error));
      var reflection=UnityEngine.Object.FindAnyObjectByType<VesperPlanarReflection>();
      if(reflection&&reflection.ReflectionTexture){var reflected=reflection.ReflectionTexture;var active=RenderTexture.active;RenderTexture.active=reflected;var proof=new Texture2D(reflected.width,reflected.height,TextureFormat.RGB24,false);proof.ReadPixels(new Rect(0,0,reflected.width,reflected.height),0,0);proof.Apply();File.WriteAllBytes(output+"/unity-reflection.png",proof.EncodeToPNG());RenderTexture.active=active;UnityEngine.Object.DestroyImmediate(proof);}
      File.WriteAllText(output+"/render-report.json","{\"width\":"+target.width+",\"height\":"+target.height+",\"shaderErrors\":"+shaderErrors+",\"runtimeErrors\":"+errors.Count+",\"reflectionFrames\":"+(reflection?reflection.RenderedFrameCount:0)+",\"device\":\""+SystemInfo.graphicsDeviceName+"\"}");
      bool pass=shaderErrors==0&&errors.Count==0&&reflection&&reflection.RenderedFrameCount>0;
      Debug.Log((pass?"VESPER_CAPTURE_PASS ":"VESPER_CAPTURE_FAIL ")+output+"/unity-slice.png");Application.logMessageReceived-=Log;EditorApplication.update-=Tick;camera.targetTexture=null;target.Release();EditorApplication.Exit(pass?0:1);
    }catch(Exception e){Debug.LogException(e);EditorApplication.update-=Tick;EditorApplication.Exit(2);}}
}
}
