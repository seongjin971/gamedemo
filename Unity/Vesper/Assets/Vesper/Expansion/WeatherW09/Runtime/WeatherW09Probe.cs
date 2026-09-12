using System;
using System.IO;
using System.Linq;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Rendering.Universal;
using Vesper.Expansion.WeatherWorld;
using Vesper.Expansion.WeatherW07;
namespace Vesper.Expansion.WeatherW09 {
// Opt-in actual player rendering and only the changed canopy/rain area, never a full-world suite.
public sealed class WeatherW09Probe:MonoBehaviour {
 [Serializable]public class Perf{public string scene;public int frames;public float fps,p95Ms,maxMs;}
 [Serializable]public class Report{public string mode,device,note;public int width,height,failures,clicks,safetyStops,audioSources;public float distance;public string[] captures,checks,errors;public Perf[] performance;}
 string mode,output;WorldEnvironment env;WorldMotor motor;WorldCamera control;WorldRunInput run;Camera camera;WeatherW07Variant variant;
 List<string> captures=new List<string>(),checks=new List<string>(),errors=new List<string>();List<Perf> perf=new List<Perf>();int failures;float distance;
 [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.AfterSceneLoad)]static void Install(){var a=Environment.GetCommandLineArgs();foreach(string key in new[]{"-w09Capture","-w09Traverse","-w09Performance"}){int i=Array.IndexOf(a,key);if(i<0||i+1>=a.Length)continue;var p=new GameObject("W09 targeted evidence").AddComponent<WeatherW09Probe>();p.mode=key;p.output=a[i+1];Directory.CreateDirectory(p.output);break;}}
 void OnEnable(){Application.logMessageReceived+=Log;}void OnDisable(){Application.logMessageReceived-=Log;}
 void Log(string m,string stack,LogType t){if(t==LogType.Error||t==LogType.Exception||t==LogType.Assert)errors.Add(m);}
 void Save(){if(!motor)return;File.WriteAllText(output+"/report.json",JsonUtility.ToJson(new Report{mode=mode,device=SystemInfo.graphicsDeviceName,note="Actual 1920x1080 Unity player. Fixtures/synthetic clicks are not user acceptance. Performance is engine cadence; concurrent-processes.json records the user's preserved W06 process. No OBS recording.",width=Screen.width,height=Screen.height,failures=failures,clicks=control.clicks,safetyStops=motor.SafetyStops,audioSources=FindObjectsByType<AudioSource>().Length,distance=distance,captures=captures.ToArray(),checks=checks.ToArray(),errors=errors.ToArray(),performance=perf.ToArray()},true));}
 void Check(bool ok,string s){checks.Add((ok?"PASS ":"FAIL ")+s);if(!ok)failures++;Save();}
 IEnumerator Place(float d){motor.Stop();motor.transform.SetPositionAndRotation(WorldLayout.Point(d),Quaternion.Euler(0,180,0));control.enabled=true;control.SnapToPlayer();yield return new WaitForSecondsRealtime(3);}
 IEnumerator Snap(string name){yield return new WaitForEndOfFrame();ScreenCapture.CaptureScreenshot(output+"/"+name+".png");captures.Add(name+".png");yield return null;Save();}
 void CloseView(float angle){control.enabled=false;var target=new Vector3(6.5f,4.9f,-195.5f);camera.orthographicSize=4.6f;camera.transform.position=target+new Vector3(-Mathf.Sin(angle)*.65f,.76f,Mathf.Cos(angle)*.65f).normalized*42;camera.transform.LookAt(target);}
 IEnumerator Pictures(){
  env.FlashOverride=0;yield return Place(198);
  variant.ShowBaseline(true);yield return new WaitForSecondsRealtime(.5f);yield return Snap("abbey-W06-normal");
  env.FlashOverride=1;env.StrongOverride=false;yield return null;yield return Snap("abbey-W06-flash");env.StrongOverride=true;yield return null;yield return Snap("abbey-W06-strong");
  env.FlashOverride=0;variant.ShowBaseline(false);yield return new WaitForSecondsRealtime(.5f);yield return Snap("abbey-W09-normal");
  env.FlashOverride=1;env.StrongOverride=false;yield return null;yield return Snap("abbey-W09-flash");env.StrongOverride=true;yield return null;yield return Snap("abbey-W09-strong");env.FlashOverride=0;yield return new WaitForSecondsRealtime(1);yield return Snap("abbey-after-flash");
  foreach(float angle in new[]{.59f,.05f,1.1f}){CloseView(angle);variant.ShowBaseline(true);yield return new WaitForSecondsRealtime(.4f);yield return Snap("canopy-W06-"+angle);variant.ShowBaseline(false);yield return new WaitForSecondsRealtime(.4f);yield return Snap("canopy-W09-"+angle);}
  motor.transform.position=new Vector3(7,2.2f,-195.5f);CloseView(.59f);yield return new WaitForSecondsRealtime(1);yield return Snap("canopy-sheltered");Check(env.Sheltered,"Original shelter activates roof cutaway");
  yield return Place(150);yield return Snap("rainwood-normal");env.FlashOverride=1;env.StrongOverride=false;yield return null;yield return Snap("rainwood-flash");env.FlashOverride=0;
  yield return Place(323);yield return Snap("snow-retained");
 }
 IEnumerator Reach(Vector3 target,bool pointer){
  int old=control.clicks,blocked=control.blocked;bool accepted;
  if(pointer){var s=camera.WorldToScreenPoint(target);control.HandlePointer(EventType.MouseDown,0,s);control.HandlePointer(EventType.MouseUp,0,s);accepted=s.z>0&&s.x>0&&s.x<Screen.width&&s.y>0&&s.y<Screen.height&&control.clicks==old+1&&control.blocked==blocked;}
  else accepted=motor.Walk(target);
  Check(accepted,(pointer?"Screen click":"Navigation motor request")+" accepted "+target+" "+motor.LastReject);if(!accepted)yield break;
  bool safe=true;var before=motor.transform.position;float until=Time.realtimeSinceStartup+20;int reset=motor.ResetSerial;
  while(motor.IsWalking&&Time.realtimeSinceStartup<until){yield return null;var p=motor.transform.position;safe&=motor.Ground(p,out var g)&&Mathf.Abs(g.point.y-p.y)<.13f&&motor.BodyClear(p)&&motor.ResetSerial==reset;distance+=Vector3.Distance(p,before);before=p;}
  Check(!motor.IsWalking&&Vector3.Distance(motor.transform.position,target)<.4f&&safe,"Arrived with support and clearance "+target);
 }
 IEnumerator Traverse(){env.FlashOverride=-1;yield return Place(192);run.SetRunning(false);env.PreviewFlash(false);
  foreach(float d in new[]{198f,204,198,192}){yield return Reach(WorldLayout.Point(d),true);if(failures>0)yield break;}
  yield return Place(197);yield return Reach(new Vector3(3.5f,2.2f,-197),false);if(failures>0)yield break;
  yield return Reach(new Vector3(6.8f,2.2f,-197),false);yield return new WaitForSecondsRealtime(.7f);Check(env.Sheltered,"Entered original shelter through arch");yield return Snap("shelter-entry");
  yield return Reach(new Vector3(3.5f,2.2f,-197),false);yield return new WaitForSecondsRealtime(.7f);Check(!env.Sheltered,"Exited shelter and opaque roof returned");yield return Reach(WorldLayout.Point(197),false);
  Check(motor.SafetyStops==0,"No safety stops");Check(FindObjectsByType<AudioSource>().Length==0,"No audio sources");
 }
 IEnumerator Performance(){env.FlashOverride=0;foreach(float d in new[]{150f,198,323}){yield return Place(d);foreach(string action in new[]{"static","walk"}){
  if(action=="walk"){run.SetRunning(false);motor.Walk(WorldLayout.Point(d+15));}var samples=new List<float>();float until=Time.realtimeSinceStartup+6;
  while(Time.realtimeSinceStartup<until){yield return null;samples.Add(Time.unscaledDeltaTime);}var sorted=samples.OrderBy(x=>x).ToArray();perf.Add(new Perf{scene=d+"-"+action,frames=samples.Count,fps=samples.Count/samples.Sum(),p95Ms=sorted[(int)((sorted.Length-1)*.95f)]*1000,maxMs=sorted.Last()*1000});motor.Stop();Save();}}
  yield return Place(198);env.volume.profile.TryGet<ColorAdjustments>(out var grade);float sun=env.sun.intensity,normal=grade.postExposure.value;
  using(var trace=new StreamWriter(output+"/pulse-timing.csv")){trace.WriteLine("strong,time,flash,exposure,sun");foreach(bool strong in new[]{false,true}){env.FlashOverride=-1;env.PreviewFlash(strong);float start=Time.time,peak=0,second=0,tail=1,peakEV=0;bool sunFixed=true;
   while(Time.time-start<1.3f){yield return new WaitForEndOfFrame();float t=Time.time-start;peak=Mathf.Max(peak,env.Flash);if(t>.26f&&t<.45f)second=Mathf.Max(second,env.Flash);if(t>1)tail=Mathf.Min(tail,env.Flash);peakEV=Mathf.Max(peakEV,grade.postExposure.value-normal);sunFixed&=Mathf.Abs(sun-env.sun.intensity)<.00001f;trace.WriteLine(FormattableString.Invariant($"{strong},{t:F5},{env.Flash:F5},{grade.postExposure.value:F5},{env.sun.intensity:F5}"));}
   Check(peak>.90f&&second>.63f&&tail<.001f,"Two brief pulses and recovery strong="+strong);Check(sunFixed,"Unchanged sun intensity strong="+strong);Check(peakEV>(strong?3.0f:2.45f),"Stronger measured exposure strong="+strong+" EV="+peakEV);Check(Mathf.Abs(grade.postExposure.value-normal)<.001f,"Original darkness restored strong="+strong);env.FlashOverride=0;yield return new WaitForSecondsRealtime(.5f);
  }}
 }
 IEnumerator Start(){yield return new WaitForSecondsRealtime(2);env=FindAnyObjectByType<WorldEnvironment>();motor=env.player;control=FindAnyObjectByType<WorldCamera>();run=motor.GetComponent<WorldRunInput>();camera=control.GetComponent<Camera>();variant=FindAnyObjectByType<WeatherW07Variant>();control.nativeInput=false;run.keyboardEnabled=false;
  if(mode=="-w09Capture")yield return Pictures();else if(mode=="-w09Traverse")yield return Traverse();else yield return Performance();Save();yield return new WaitForSecondsRealtime(.5f);Application.Quit(failures==0&&errors.Count==0?0:1);
 }
}
}
