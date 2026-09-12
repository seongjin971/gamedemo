using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Experimental.Rendering;
using System.Threading;
using System.Threading.Tasks;

namespace Vesper {
 // Opt-in visual recording. Async readback is separate from clean FPS QA.
 public sealed class VesperMotionProbe : MonoBehaviour {
  [Serializable] public class Frame { public string file,stage; public float time,angle,elevation,zoom; public Vector3 player,camera; public bool focused; }
  [Serializable] public class Arrival {public string stage;public int destination;public float time;public Vector3 requested,actual;}
  [Serializable] public class Report { public string note="Natural player frames requested at 12Hz, asynchronously read back and encoded to JPEG95. Inspect frame timestamps for actual sampling. This is not a clean performance benchmark or direct pointer input."; public int width,height,skipped; public float distance; public Frame[] frames;public Arrival[] arrivals; public string[] errors; }
  string output,stage="warmup"; readonly List<Frame> frames=new List<Frame>();readonly List<string> errors=new List<string>();
  readonly List<Arrival> arrivals=new List<Arrival>();
  VesperKnight knight;VesperOrbitCamera control;Vector3 previous;float distance;int pending,skipped;readonly object errorLock=new object();
  [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.AfterSceneLoad)] static void Install(){var args=Environment.GetCommandLineArgs();int i=Array.IndexOf(args,"-vesperMotionQA");if(i<0||i+1>=args.Length)return;var probe=new GameObject("Temporary motion recording").AddComponent<VesperMotionProbe>();probe.output=args[i+1];Directory.CreateDirectory(probe.output);}
  void OnEnable(){Application.logMessageReceived+=Log;}void OnDisable(){Application.logMessageReceived-=Log;}
  void Log(string message,string stack,LogType type){if(type==LogType.Error||type==LogType.Exception){lock(errorLock)errors.Add(message);}}
  IEnumerator Start(){
   knight=FindAnyObjectByType<VesperKnight>();control=Camera.main.GetComponent<VesperOrbitCamera>();previous=knight.transform.position;
   yield return new WaitForSecondsRealtime(4);
   var navigation=new VesperNavigation();
   foreach(string phase in new[]{"walk","near-root","orbit","zoom","wide-limit","close-limit"}){
    stage=phase;control.ResetView();yield return new WaitForSecondsRealtime(1);previous=knight.transform.position;
    float start=Time.realtimeSinceStartup,nextCapture=start;int destination=0;
    var destinations=new[]{new Vector3(-3.08f,0,5.21f),new Vector3(-3.08f,0,11.0f),new Vector3(0,0,9.5f)};
    bool walking=phase=="walk"||phase=="near-root";
    if(phase=="near-root"){destinations=new[]{new Vector3(3.4f,0,3.7f),new Vector3(4,0,6.7f),new Vector3(6,0,7.4f)};control.SetZoom(8.8f);foreach(var point in destinations)if(!navigation.Valid(point))throw new Exception("Near-root probe endpoint invalid "+point);}
    if(walking)knight.Walk(destinations[0]);
    if(phase=="wide-limit"){control.SetZoom(14);control.Orbit(.64f,-.24f);}
    if(phase=="close-limit"){control.SetZoom(7.5f);control.Orbit(-.51f,.42f);}
    while(Time.realtimeSinceStartup-start<(phase=="near-root"?9:6)){
     float t=Time.realtimeSinceStartup-start;
     // A* stops at a valid grid node, which can differ from the requested point
     // by more than a fixed distance threshold near an obstacle boundary.
     if(walking&&!knight.IsWalking){arrivals.Add(new Arrival{stage=phase,destination=destination,time=Time.realtimeSinceStartup,requested=destinations[destination],actual=knight.transform.position});destination=(destination+1)%destinations.Length;knight.Walk(destinations[destination]);}
     if(phase=="near-root"&&!navigation.Valid(knight.transform.position)&&!errors.Contains("Near-root route crossed clearance"))errors.Add("Near-root route crossed clearance");
     if(phase=="orbit")control.Orbit(Time.unscaledDeltaTime*.085f,Mathf.Sin(t*.9f)*Time.unscaledDeltaTime*.025f);
     if(phase=="zoom")control.SetZoom(10.5f+Mathf.Sin(t*.85f)*2.3f);
     distance+=Vector3.Distance(previous,knight.transform.position);previous=knight.transform.position;
     if(Time.realtimeSinceStartup>=nextCapture){yield return new WaitForEndOfFrame();Capture();nextCapture=Time.realtimeSinceStartup+1f/12;}
     else yield return null;
    }
   }
   while(Volatile.Read(ref pending)>0)yield return null;
   File.WriteAllText(Path.Combine(output,"motion-report.json"),JsonUtility.ToJson(new Report{width=Screen.width,height=Screen.height,skipped=skipped,distance=distance,frames=frames.ToArray(),arrivals=arrivals.ToArray(),errors=errors.ToArray()},true));Application.Quit();
  }
  void Capture(){
   if(Volatile.Read(ref pending)>=4){skipped++;return;}
   string file=frames.Count.ToString("D4")+".jpg",path=Path.Combine(output,file);int width=Screen.width,height=Screen.height;bool flipRows=SystemInfo.graphicsUVStartsAtTop;
   var target=RenderTexture.GetTemporary(width,height,0,RenderTextureFormat.ARGB32,RenderTextureReadWrite.sRGB);
   ScreenCapture.CaptureScreenshotIntoRenderTexture(target);Interlocked.Increment(ref pending);
   frames.Add(new Frame{file=file,stage=stage,time=Time.realtimeSinceStartup,player=knight.transform.position,camera=Camera.main.transform.position,angle=control.Angle,elevation=control.Elevation,zoom=Camera.main.orthographicSize,focused=Application.isFocused});
   AsyncGPUReadback.Request(target,0,TextureFormat.RGBA32,request=>{
    if(request.hasError){lock(errorLock)errors.Add("GPU readback failed: "+file);RenderTexture.ReleaseTemporary(target);Interlocked.Decrement(ref pending);return;}
    byte[] pixels=request.GetData<byte>().ToArray();RenderTexture.ReleaseTemporary(target);
    Task.Run(()=>{try{if(flipRows){int stride=width*4;var topDown=new byte[pixels.Length];for(int row=0;row<height;row++)Buffer.BlockCopy(pixels,row*stride,topDown,(height-1-row)*stride,stride);pixels=topDown;}File.WriteAllBytes(path,ImageConversion.EncodeArrayToJPG(pixels,GraphicsFormat.R8G8B8A8_UNorm,(uint)width,(uint)height,0,95));}catch(Exception e){lock(errorLock)errors.Add(e.Message);}finally{Interlocked.Decrement(ref pending);}});
   });
  }
 }
}
