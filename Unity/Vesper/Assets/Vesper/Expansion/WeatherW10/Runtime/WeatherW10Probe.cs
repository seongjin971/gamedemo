using System;
using System.IO;
using System.Linq;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
namespace Vesper.Expansion.WeatherW10 {
// Opt-in player input regression for this request; never a full traversal suite.
public sealed class WeatherW10Probe:MonoBehaviour {
 [Serializable] public class Perf { public string scene; public int frames; public float fps,p95Ms,maxMs; }
 [Serializable] public class Report { public string note,device; public int width,height,failures,clicks,drags,audioSources,safetyStops; public float distance; public string[] checks,errors,captures; public Perf[] performance; }
 WorldCamera control; WorldMotor motor; WorldEnvironment env; WorldRunInput run; Camera camera; string output;
 List<string> checks=new List<string>(),errors=new List<string>(),captures=new List<string>(); List<Perf> perf=new List<Perf>(); int failures; float distance;
 [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.AfterSceneLoad)] static void Install(){var args=Environment.GetCommandLineArgs();int i=Array.IndexOf(args,"-w10InputQA");if(i<0||i+1>=args.Length)return;var p=new GameObject("W10 targeted input evidence").AddComponent<WeatherW10Probe>();p.output=args[i+1];Directory.CreateDirectory(p.output);}
 void OnEnable(){Application.logMessageReceived+=Log;} void OnDisable(){Application.logMessageReceived-=Log;}
 void Log(string message,string stack,LogType type){if(type==LogType.Error||type==LogType.Exception||type==LogType.Assert)errors.Add(message);}
 void Save(){if(!motor)return;File.WriteAllText(output+"/report.json",JsonUtility.ToJson(new Report{note="Actual Unity player, synthetic calls through the same key/pointer handlers used by native polling. Not physical keyboard/user acceptance. Engine cadence, no OBS recording.",device=SystemInfo.graphicsDeviceName,width=Screen.width,height=Screen.height,failures=failures,clicks=control.clicks,drags=control.drags,audioSources=FindObjectsByType<AudioSource>().Length,safetyStops=motor.SafetyStops,distance=distance,checks=checks.ToArray(),errors=errors.ToArray(),captures=captures.ToArray(),performance=perf.ToArray()},true));}
 void Check(bool ok,string message){checks.Add((ok?"PASS ":"FAIL ")+message);if(!ok)failures++;Save();}
 IEnumerator Snap(string name){yield return new WaitForEndOfFrame();ScreenCapture.CaptureScreenshot(output+"/"+name+".png");captures.Add(name+".png");yield return null;Save();}
 IEnumerator Place(float d){motor.Stop();motor.transform.SetPositionAndRotation(WorldLayout.Point(d),Quaternion.Euler(0,180,0));control.SnapToPlayer();yield return new WaitForSecondsRealtime(2);}
 IEnumerator Keys(bool q,bool e,float duration){float until=Time.realtimeSinceStartup+duration;while(Time.realtimeSinceStartup<until){control.HandleKeys(q,e,false,0,Time.unscaledDeltaTime);yield return null;}yield return new WaitForSecondsRealtime(.8f);}
 IEnumerator Reach(float d,bool drag){
  var point=WorldLayout.Point(d);var screen=camera.WorldToScreenPoint(point);int clicks=control.clicks,blocked=control.blocked;float yaw=control.Angle,pitch=control.Elevation;
  var press=drag?screen+new Vector3(170,-90,0):screen;
  control.HandlePointer(EventType.MouseDown,0,press);
  if(drag)control.HandlePointer(EventType.MouseDrag,0,screen+new Vector3(90,45,0));
  control.HandlePointer(EventType.MouseUp,0,screen);
  Check(control.clicks==clicks+1&&control.blocked==blocked,"Movement accepted after "+(drag?"large pointer drag":"click")+" to "+d+" "+motor.LastReject);
  bool safe=true,stable=true;var previous=motor.transform.position;float until=Time.realtimeSinceStartup+15;
  while(motor.IsWalking&&Time.realtimeSinceStartup<until){yield return null;var p=motor.transform.position;distance+=Vector3.Distance(previous,p);previous=p;safe&=motor.Ground(p,out var g)&&Mathf.Abs(g.point.y-p.y)<.13f&&motor.BodyClear(p);stable&=Mathf.Abs(control.Angle-yaw)<.0001f&&Mathf.Abs(control.Elevation-pitch)<.0001f;}
  Check(!motor.IsWalking&&Vector3.Distance(motor.transform.position,point)<.4f&&safe,"Arrival and collision support at "+d);
  Check(stable,"Yaw and elevation stay fixed through pointer motion and walking to "+d);
 }
 IEnumerator Sample(float d){yield return Place(d);motor.Walk(WorldLayout.Point(d+12));var samples=new List<float>();float until=Time.realtimeSinceStartup+6;while(Time.realtimeSinceStartup<until){yield return null;samples.Add(Time.unscaledDeltaTime);}motor.Stop();var sorted=samples.OrderBy(x=>x).ToArray();perf.Add(new Perf{scene=d+"-walk",frames=samples.Count,fps=samples.Count/samples.Sum(),p95Ms=sorted[(int)((sorted.Length-1)*.95f)]*1000,maxMs=sorted.Last()*1000});Save();}
 IEnumerator Start(){
  yield return new WaitForSecondsRealtime(2);control=FindAnyObjectByType<WorldCamera>();motor=control.player;env=FindAnyObjectByType<WorldEnvironment>();run=motor.GetComponent<WorldRunInput>();camera=control.GetComponent<Camera>();control.nativeInput=false;run.keyboardEnabled=false;env.FlashOverride=0;
  yield return Place(192);yield return Snap("start-qe-help");
  float yaw=control.Angle,pitch=control.Elevation;yield return Keys(true,false,.4f);Check(control.Angle<yaw-.12f&&Mathf.Abs(control.Elevation-pitch)<.0001f,"Q rotates left, fixed elevation");yield return Snap("q-left");
  yaw=control.Angle;yield return Keys(false,true,.4f);Check(control.Angle>yaw+.12f&&Mathf.Abs(control.Elevation-pitch)<.0001f,"E rotates right, fixed elevation");yield return Snap("e-right");
  yaw=control.Angle;yield return Keys(true,true,.35f);Check(Mathf.Abs(control.Angle-yaw)<.0001f,"Q and E together do not rotate");
  yield return Reach(198,true);yield return Snap("drag-release-walk-fixed-angle");yield return Reach(192,false);
  yaw=control.Angle;float zoom=control.Zoom;control.HandleKeys(false,false,false,1,.016f);yield return new WaitForSecondsRealtime(.8f);Check(control.Zoom<zoom&&Mathf.Abs(control.Angle-yaw)<.0001f&&Mathf.Abs(control.Elevation-pitch)<.0001f,"Wheel zoom does not rotate");control.SetZoom(zoom);
  yield return Keys(true,false,.25f);yaw=control.Angle;control.HandleKeys(false,false,true,0,.016f);yield return new WaitForSecondsRealtime(.8f);Check(Vector3.Distance(motor.transform.position,motor.home)<.05f&&Mathf.Abs(control.Angle-yaw)<.0001f&&Mathf.Abs(control.Elevation-pitch)<.0001f,"R returns home without rotating");
  yield return Place(192);run.SetRunning(true);Check(run.Requested&&Mathf.Abs(motor.walkSpeed-5.4f)<.0001f,"Shift running speed retained");run.SetRunning(false);
  var s=camera.WorldToScreenPoint(WorldLayout.Point(198));int before=control.clicks;control.HandlePointer(EventType.MouseUp,0,s);Check(control.clicks==before,"Unpaired release ignored");
  control.HandlePointer(EventType.MouseDown,0,s);control.enabled=false;control.enabled=true;control.HandlePointer(EventType.MouseUp,0,s);Check(control.clicks==before,"Disabling input cancels held pointer");
  yaw=control.Angle;Check(!control.HandlePointer(EventType.MouseDown,1,s)&&!control.HandlePointer(EventType.MouseDrag,1,s+Vector3.one*80)&&!control.HandlePointer(EventType.MouseUp,1,s),"Right mouse ignored");yield return new WaitForSecondsRealtime(.4f);Check(Mathf.Abs(control.Angle-yaw)<.0001f,"Other pointer buttons never rotate");
  yield return Place(198);env.FlashOverride=1;env.StrongOverride=true;yield return null;yield return Snap("w09-strong-flash-retained");env.FlashOverride=0;
  yield return Sample(150);yield return Sample(198);yield return Sample(323);yield return Snap("snow-retained");
  Check(control.drags==0,"No mouse orbit events");Check(motor.SafetyStops==0,"No safety stops");Check(FindObjectsByType<AudioSource>().Length==0,"No audio sources");Save();yield return new WaitForSecondsRealtime(.5f);Application.Quit(failures==0&&errors.Count==0?0:1);
 }
}
}
