using System;
using System.IO;
using System.Linq;
using System.Collections.Generic;
using System.Collections;
using UnityEngine;

namespace Vesper.Expansion {
 public sealed class AdventurerPlayerProbe:MonoBehaviour {
  [Serializable]public class Segment{public string name;public int frames,unfocused;public float fps,p50Ms,p95Ms,p99Ms,cpuP50Ms,cpuP95Ms,gpuP50Ms,gpuP95Ms;public int validTimings;}
  [Serializable]public class Report{public string note="Standalone player natural frame loop, no explicit render requests. Frame cadence is not a hardware display-present trace.",device;public int width,height,clicks,drags,zooms,resets,blocked,reflectionFrames;public bool focused;public float moved;public string[] errors;public Segment[] stages;public Vector3 player,camera;}
  readonly FrameTiming[] frameTimings=new FrameTiming[1];readonly List<float> cpuTimings=new List<float>(),gpuTimings=new List<float>();
  readonly List<string> errors=new List<string>();readonly List<float> samples=new List<float>();readonly List<Segment> stages=new List<Segment>();
  string output,stage="warmup";bool manual,collectTiming;int unfocused;float start;Vector3 initial;AdventurerMotor knight;AdventurerCamera control;
  [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.AfterSceneLoad)]static void Install(){var args=Environment.GetCommandLineArgs();int i=Array.IndexOf(args,"-p1QA");bool manual=false;if(i<0){i=Array.IndexOf(args,"-p1ManualQA");manual=true;}if(i<0||i+1>=args.Length)return;var p=new GameObject("Temporary player verification").AddComponent<AdventurerPlayerProbe>();p.output=args[i+1];p.manual=manual;p.collectTiming=args.Contains("-vesperTiming");Directory.CreateDirectory(p.output);}
  void OnEnable(){Application.logMessageReceived+=Log;}void OnDisable(){Application.logMessageReceived-=Log;}
  void Awake(){
   VesperShadowDiagnostics.Apply();
   var args=Environment.GetCommandLineArgs();
   if(args.Contains("-vesperNoFireShadows")||args.Contains("-vesperHardFireShadows")){
    foreach(var lamp in FindObjectsByType<Light>())if(lamp.name=="Brazier")lamp.shadows=args.Contains("-vesperNoFireShadows")?LightShadows.None:LightShadows.Hard;
    Debug.Log("VESPER_QA_DIAGNOSTIC_FIRE_SHADOW_OVERRIDE");
   }
   if(args.Contains("-vesperNoFloorCast"))foreach(var renderer in FindObjectsByType<MeshRenderer>())if(renderer.gameObject.layer==29)renderer.shadowCastingMode=UnityEngine.Rendering.ShadowCastingMode.Off;
  }
  void Log(string m,string s,LogType t){if(t==LogType.Error||t==LogType.Exception||t==LogType.Assert)errors.Add(m);}
  IEnumerator Start(){knight=FindAnyObjectByType<AdventurerMotor>();control=Camera.main.GetComponent<AdventurerCamera>();initial=knight.transform.position;yield return new WaitForSecondsRealtime(5);Begin(manual?"manual-input":"static");if(manual){while(true){yield return new WaitForSecondsRealtime(1);Save();}}yield return new WaitForSecondsRealtime(8);yield return Capture("static");End();Begin("walk");knight.Walk(new Vector3(-3.08f,0,5.21f));yield return new WaitForSecondsRealtime(8);yield return Capture("walk");End();Begin("orbit");for(float t=0;t<8;t+=Time.unscaledDeltaTime){control.Orbit(Time.unscaledDeltaTime*.065f,Mathf.Sin(t)*Time.unscaledDeltaTime*.02f);yield return null;}yield return Capture("orbit");End();Begin("zoom");for(float t=0;t<8;t+=Time.unscaledDeltaTime){control.SetZoom(10.5f+Mathf.Sin(t*.8f)*2);yield return null;}yield return Capture("zoom");End();Save();Application.Quit();}
  void Begin(string name){stage=name;samples.Clear();cpuTimings.Clear();gpuTimings.Clear();unfocused=0;start=Time.realtimeSinceStartup;}
  Segment Metrics(){var a=samples.OrderBy(x=>x).ToArray();var cpu=cpuTimings.OrderBy(x=>x).ToArray();var gpu=gpuTimings.OrderBy(x=>x).ToArray();return new Segment{validTimings=gpu.Length,cpuP50Ms=Percentile(cpu,.50f),cpuP95Ms=Percentile(cpu,.95f),gpuP50Ms=Percentile(gpu,.50f),gpuP95Ms=Percentile(gpu,.95f),name=stage,frames=a.Length,unfocused=unfocused,fps=a.Length/Mathf.Max(.01f,samples.Sum()),p50Ms=a.Length>0?a[(a.Length-1)/2]*1000:0,p95Ms=a.Length>0?a[(int)((a.Length-1)*.95f)]*1000:0,p99Ms=a.Length>0?a[(int)((a.Length-1)*.99f)]*1000:0};}
  static float Percentile(float[] values,float p){return values.Length==0?0:values[(int)((values.Length-1)*p)];}
  void End(){stages.Add(Metrics());}
  void Update(){if(collectTiming){FrameTimingManager.CaptureFrameTimings();uint timingCount=FrameTimingManager.GetLatestTimings(1,frameTimings);if(stage!="warmup"&&timingCount>0&&frameTimings[0].gpuFrameTime>0){cpuTimings.Add((float)frameTimings[0].cpuFrameTime);gpuTimings.Add((float)frameTimings[0].gpuFrameTime);}}if(stage!="warmup"){samples.Add(Time.unscaledDeltaTime);if(!Application.isFocused)unfocused++;}if(manual&&Input.GetKeyDown(KeyCode.F9))StartCoroutine(Capture("manual-"+DateTime.Now.ToString("HHmmss")));if(manual&&Input.GetKeyDown(KeyCode.F10)){End();Save();Application.Quit();}}
  IEnumerator Capture(string name){yield return new WaitForEndOfFrame();ScreenCapture.CaptureScreenshot(Path.Combine(output,name+".png"));}
  void Save(){var list=stages.ToList();if(manual&&stages.Count==0)list.Add(Metrics());var r=new Report{device=SystemInfo.graphicsDeviceName,width=Screen.width,height=Screen.height,focused=Application.isFocused,clicks=control.clicks,drags=control.drags,zooms=control.zooms,resets=control.resets,blocked=control.blocked,reflectionFrames=FindAnyObjectByType<VesperPlanarReflection>().RenderedFrameCount,moved=Vector3.Distance(initial,knight.transform.position),player=knight.transform.position,camera=Camera.main.transform.position,errors=errors.ToArray(),stages=list.ToArray()};if(Environment.GetCommandLineArgs().Contains("-vesperNoFireShadows"))r.note+=" DIAGNOSTIC: brazier shadows disabled for cost isolation; not a visual candidate.";if(Environment.GetCommandLineArgs().Contains("-vesperHardFireShadows"))r.note+=" DIAGNOSTIC: hard fire shadows.";if(Environment.GetCommandLineArgs().Contains("-vesperFullFireCasters"))r.note+=" DIAGNOSTIC: original full meshes cast fire shadows.";if(Environment.GetCommandLineArgs().Contains("-vesperNoFloorCast"))r.note+=" DIAGNOSTIC: ground shadow casting disabled.";File.WriteAllText(Path.Combine(output,"player-report.json"),JsonUtility.ToJson(r,true));}
 }
}
