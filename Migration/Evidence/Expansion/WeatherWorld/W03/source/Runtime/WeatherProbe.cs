using System;
using System.IO;
using System.Linq;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
namespace Vesper.Expansion.WeatherWorld {
// Opt-in instrumentation of the actual player render. Absent during ordinary play.
public sealed class WeatherProbe:MonoBehaviour {
 [Serializable]public class Capture{public string image;public float progress,flash,rain,snow,darkness;}
 [Serializable]public class Perf{public string scene;public int frames;public float fps,p95Ms,maxMs;}
 [Serializable]public class Report{public string mode,device,note;public int width,height,failures,clicks,safetyStops,audioSources;public float distance;public string[] checks,errors;public Capture[] captures;public Perf[] performance;}
 string mode,output;WorldMotor motor;WorldCamera control;WorldRunInput run;WorldEnvironment env;Camera camera;
 readonly List<Capture> captures=new List<Capture>();readonly List<Perf> perf=new List<Perf>();readonly List<string> checks=new List<string>(),errors=new List<string>();int failures;float distance;
 [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.AfterSceneLoad)]static void Install(){var a=Environment.GetCommandLineArgs();foreach(string key in new[]{"-weatherCapture","-weatherTraverse","-weatherPerformance","-weatherMotion"}){int i=Array.IndexOf(a,key);if(i<0||i+1>=a.Length)continue;var p=new GameObject("Weather evidence probe").AddComponent<WeatherProbe>();p.mode=key;p.output=a[i+1];Directory.CreateDirectory(p.output);break;}}
 void OnEnable(){Application.logMessageReceived+=Log;}void OnDisable(){Application.logMessageReceived-=Log;}
 void Log(string m,string stack,LogType t){if(t==LogType.Error||t==LogType.Exception||t==LogType.Assert)errors.Add(m);}
 void Save(){if(!motor)return;File.WriteAllText(output+"/report.json",JsonUtility.ToJson(new Report{mode=mode,device=SystemInfo.graphicsDeviceName,note="Actual Unity renders. Screenshot fixtures and synthetic pointer checks are not native user acceptance. Performance is uncapped engine cadence, not display present timing. Motion export is separate from performance measurement.",width=Screen.width,height=Screen.height,failures=failures,clicks=control.clicks,safetyStops=motor.SafetyStops,audioSources=FindObjectsByType<AudioSource>().Length,distance=distance,checks=checks.ToArray(),errors=errors.ToArray(),captures=captures.ToArray(),performance=perf.ToArray()},true));}
 void Check(bool ok,string text){checks.Add((ok?"PASS ":"FAIL ")+text);if(!ok)failures++;Save();}
 IEnumerator Place(float d){motor.Stop();motor.transform.SetPositionAndRotation(WorldLayout.Point(d),Quaternion.Euler(0,180,0));yield return new WaitForSecondsRealtime(4);}
 IEnumerator Snap(string name){yield return new WaitForEndOfFrame();ScreenCapture.CaptureScreenshot(output+"/"+name+".png");captures.Add(new Capture{image=name+".png",progress=env.Progress,flash=env.Flash,rain=env.Weights.y,snow=env.Weights.z,darkness=WorldLayout.Darkness(env.Progress)});yield return null;Save();}
 IEnumerator Pictures(){env.FlashOverride=0;foreach(float d in new[]{323f,282,258,25,60,84,104,122,150,198}){yield return Place(d);yield return Snap("weather-"+d);}env.FlashOverride=1;env.StrongOverride=false;yield return new WaitForSecondsRealtime(.1f);yield return Snap("abbey-distant-flash");env.StrongOverride=true;yield return new WaitForSecondsRealtime(.1f);yield return Snap("abbey-strong-flash");env.FlashOverride=0;}
 IEnumerator Reach(float d){var target=WorldLayout.Point(d);var screen=camera.WorldToScreenPoint(target);int old=control.clicks,blocked=control.blocked;control.HandlePointer(EventType.MouseDown,0,screen);control.HandlePointer(EventType.MouseUp,0,screen);Check(screen.z>0&&screen.x>0&&screen.x<Screen.width&&screen.y>0&&screen.y<Screen.height&&control.clicks==old+1&&control.blocked==blocked,"screen pointer accepted "+d);if(control.blocked!=blocked)yield break;bool support=true,body=true,continuous=true;var previous=motor.transform.position;var weights=env.Weights;float dark=WorldLayout.Darkness(env.Progress),until=Time.realtimeSinceStartup+14;int reset=motor.ResetSerial;while(motor.IsWalking&&Time.realtimeSinceStartup<until){yield return null;var p=motor.transform.position;float step=Vector3.Distance(p,previous);support&=motor.Ground(p,out var hit)&&Mathf.Abs(hit.point.y-p.y)<.13f;body&=motor.BodyClear(p);continuous&=step<run.runningSpeed*Mathf.Min(Time.deltaTime,.05f)+.06f&&motor.ResetSerial==reset&&(env.Weights-weights).magnitude<.07f&&Mathf.Abs(WorldLayout.Darkness(env.Progress)-dark)<.07f;distance+=step;previous=p;weights=env.Weights;dark=WorldLayout.Darkness(env.Progress);}Check(!motor.IsWalking&&Vector3.Distance(motor.transform.position,target)<.35f&&support&&body&&continuous,"arrival, support and continuous climate "+d+": "+motor.LastReject);}
 IEnumerator Traverse(){env.FlashOverride=0;foreach(var segment in new[]{new Vector2(42,66),new Vector2(102,126),new Vector2(132,150),new Vector2(264,288)}){yield return Place(segment.x);run.SetRunning(false);for(float d=segment.x+6;d<=segment.y;d+=6){yield return Reach(d);if(failures>0)yield break;}yield return Snap("forward-"+segment.y);run.SetRunning(true);for(float d=segment.y-6;d>=segment.x;d-=6){yield return Reach(d);if(failures>0)yield break;}}Check(motor.SafetyStops==0,"No safety stops");Check(FindObjectsByType<AudioSource>().Length==0,"No audio sources");}
 IEnumerator Performance(){env.FlashOverride=-1;foreach(float d in new[]{84f,198,282,323}){yield return Place(d);foreach(string action in new[]{"static","walk"}){if(action=="walk"){run.SetRunning(false);motor.Walk(WorldLayout.Point(d+15));}var samples=new List<float>();float until=Time.realtimeSinceStartup+6;while(Time.realtimeSinceStartup<until){yield return null;samples.Add(Time.unscaledDeltaTime);}var sorted=samples.OrderBy(x=>x).ToArray();perf.Add(new Perf{scene=d+"-"+action,frames=samples.Count,fps=samples.Count/samples.Sum(),p95Ms=sorted[(int)((sorted.Length-1)*.95f)]*1000,maxMs=sorted.Last()*1000});motor.Stop();Save();}}}
 IEnumerator Motion(){
  int serial=0;using(var trace=new StreamWriter(output+"/frames.csv")){
   trace.WriteLine("file,time,progress,flash,strong");
   foreach(float d in new[]{84f,198,323}){
    env.FlashOverride=0;yield return Place(d);env.FlashOverride=-1;
    float start=Time.realtimeSinceStartup;bool first=false,second=false;
    while(Time.realtimeSinceStartup-start<(d==198?9:5)){
     float t=Time.realtimeSinceStartup-start;if(d==198&&t>1&&!first){env.PreviewFlash(false);first=true;}if(d==198&&t>5&&!second){env.PreviewFlash(true);second=true;}
     yield return new WaitForEndOfFrame();string file="motion-"+(serial++).ToString("D4")+".png";ScreenCapture.CaptureScreenshot(output+"/"+file);trace.WriteLine(FormattableString.Invariant($"{file},{Time.realtimeSinceStartup:F5},{d},{env.Flash:F5},{env.StrongFlash}"));yield return new WaitForSecondsRealtime(.0333f);
    }
   }
  }
 }
 IEnumerator Start(){yield return new WaitForSecondsRealtime(2);motor=FindAnyObjectByType<WorldMotor>();if(!motor){Application.Quit(2);yield break;}control=FindAnyObjectByType<WorldCamera>();run=motor.GetComponent<WorldRunInput>();env=FindAnyObjectByType<WorldEnvironment>();camera=control.GetComponent<Camera>();control.nativeInput=false;run.keyboardEnabled=false;if(mode=="-weatherCapture")yield return Pictures();else if(mode=="-weatherTraverse")yield return Traverse();else if(mode=="-weatherPerformance")yield return Performance();else yield return Motion();Save();yield return new WaitForSecondsRealtime(.5f);Application.Quit(failures==0&&errors.Count==0?0:1);}
}
}
