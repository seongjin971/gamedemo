using System;
using System.IO;
using System.Linq;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
namespace Vesper.Expansion.LinearWorld {
// Explicit road-package evidence. No component is installed during normal play.
public sealed class LinearRoadProbe:MonoBehaviour {
 [Serializable]public class Frame {public float progress;public Vector3 position;public string image;}
 [Serializable]public class Perf {public string name;public int frames,unfocused;public float fps,p95Ms,maxMs;}
 [Serializable]public class Report {public string mode,device,note;public int width,height,fixtures,frames,clicks,rejected,safetyStops,resets,audioSources,failures;public float distance;public Frame[] captures;public string[] checks,errors;public Perf[] performance;}
 string mode,output;WorldMotor motor;WorldCamera control;WorldRunInput run;WorldEnvironment env;Camera camera;
 List<Frame> captures=new List<Frame>();List<string> checks=new List<string>(),errors=new List<string>();List<Perf> performance=new List<Perf>();int fixtures,frames,failures;float distance;StreamWriter trace;
 [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.AfterSceneLoad)]static void Install(){var a=Environment.GetCommandLineArgs();foreach(string key in new[]{"-roadCapture","-roadTraverse","-roadPerformance"}){int i=Array.IndexOf(a,key);if(i<0||i+1>=a.Length)continue;var p=new GameObject("Road evidence probe").AddComponent<LinearRoadProbe>();p.mode=key;p.output=a[i+1];Directory.CreateDirectory(p.output);break;}}
 void OnEnable(){Application.logMessageReceived+=Log;}void OnDisable(){Application.logMessageReceived-=Log;trace?.Dispose();}
 void Log(string m,string stack,LogType type){if(type==LogType.Error||type==LogType.Exception||type==LogType.Assert)errors.Add(m);}
 void Save(){if(!motor)return;File.WriteAllText(output+"/report.json",JsonUtility.ToJson(new Report{mode=mode,device=SystemInfo.graphicsDeviceName,note="Unmodified Unity runtime captures. Fixture placement is not traversal; screen pointer traversal is synthetic. Native device acceptance is separate. FPS is engine frame cadence, not display-present timing.",width=Screen.width,height=Screen.height,fixtures=fixtures,frames=frames,clicks=control.clicks,rejected=control.blocked,safetyStops=motor.SafetyStops,resets=control.resets,audioSources=FindObjectsByType<AudioSource>().Length,failures=failures,distance=distance,captures=captures.ToArray(),checks=checks.ToArray(),errors=errors.ToArray(),performance=performance.ToArray()},true));}
 void Check(bool ok,string label){checks.Add((ok?"PASS ":"FAIL ")+label);if(!ok)failures++;Save();}
 IEnumerator Place(float d){motor.Stop();motor.transform.SetPositionAndRotation(WorldLayout.Point(d),Quaternion.Euler(0,180,0));fixtures++;yield return new WaitForSecondsRealtime(3);}
 IEnumerator Snap(string name){yield return new WaitForEndOfFrame();ScreenCapture.CaptureScreenshot(output+"/"+name+".png");captures.Add(new Frame{progress=-motor.transform.position.z,position=motor.transform.position,image=name+".png"});yield return null;Save();}
 IEnumerator Pictures(){foreach(float d in new[]{25f,46,50,85,122,126,150,176,182,215,228,234,238,244,260,275}){yield return Place(d);Check(Vector3.Distance(motor.transform.position,WorldLayout.Point(d))<.01f,"Capture fixture "+d+" intact");yield return Snap("road-"+d);}}
 IEnumerator Reach(float d,string label){
  Vector3 target=WorldLayout.Point(d),screen=camera.WorldToScreenPoint(target);int c=control.clicks,b=control.blocked;control.HandlePointer(EventType.MouseDown,0,screen);control.HandlePointer(EventType.MouseUp,0,screen);
  Check(screen.z>0&&screen.x>0&&screen.x<Screen.width&&screen.y>0&&screen.y<Screen.height&&control.clicks==c+1&&control.blocked==b,label+" screen pointer accepted");if(control.blocked!=b)yield break;
  bool support=true,body=true,continuous=true;var prev=motor.transform.position;var weather=env.Weights;int reset=motor.ResetSerial;float until=Time.realtimeSinceStartup+18;
  while(motor.IsWalking&&Time.realtimeSinceStartup<until){yield return null;var p=motor.transform.position;float step=Vector3.Distance(p,prev);support&=motor.Ground(p,out var hit)&&Mathf.Abs(hit.point.y-p.y)<.13f;body&=motor.BodyClear(p);continuous&=step<run.runningSpeed*Mathf.Min(Time.deltaTime,.05f)+.06f&&motor.ResetSerial==reset&&(env.Weights-weather).magnitude<.07f;distance+=step;frames++;trace.WriteLine(FormattableString.Invariant($"{Time.realtimeSinceStartup:F4},{p.x:F4},{p.y:F4},{p.z:F4},{step:F5},{env.Weights.x:F5},{env.Weights.y:F5},{env.Weights.z:F5},{support},{body},{continuous}"));prev=p;weather=env.Weights;}
  Check(!motor.IsWalking&&Vector3.Distance(motor.transform.position,target)<.35f&&support&&body&&continuous,label+" arrival/support/body/climate continuity: "+motor.LastReject);
 }
 IEnumerator Traverse(){
  trace=new StreamWriter(output+"/road-transitions.csv");trace.WriteLine("time,x,y,z,step,clear,rain,snow,supported,bodyClear,continuous");
  foreach(var segment in new[]{new Vector2(38,62),new Vector2(112,136),new Vector2(166,190),new Vector2(208,256)}){
   yield return Place(segment.x);run.SetRunning(false);yield return Snap("start-"+segment.x);
   for(float d=segment.x+6;d<=segment.y;d+=6){yield return Reach(d,"forward "+d);if(failures>0)break;}
   yield return Snap("end-"+segment.y);if(failures>0)break;
   run.SetRunning(true);for(float d=segment.y-6;d>=segment.x;d-=6){yield return Reach(d,"reverse "+d);if(failures>0)break;}
   yield return Snap("returned-"+segment.x);if(failures>0)break;
  }
  Check(motor.SafetyStops==0,"No safety stop");Check(control.resets==0,"No camera reset");Check(FindObjectsByType<AudioSource>().Length==0,"No audio sources");trace.Flush();trace.Dispose();trace=null;
 }
 IEnumerator Performance(){foreach(float d in new[]{85f,150,234,275}){yield return Place(d);foreach(string action in new[]{"static","walk","orbit"}){if(action=="walk"){run.SetRunning(false);motor.Walk(WorldLayout.Point(d+18));}var samples=new List<float>();int unfocused=0;float start=Time.realtimeSinceStartup;while(Time.realtimeSinceStartup-start<6){if(action=="orbit")control.Orbit(Mathf.Sin((Time.realtimeSinceStartup-start)*1.2f)*Time.unscaledDeltaTime*.10f,0);yield return null;samples.Add(Time.unscaledDeltaTime);if(!Application.isFocused)unfocused++;}var ordered=samples.OrderBy(x=>x).ToArray();performance.Add(new Perf{name=d+"-"+action,frames=samples.Count,unfocused=unfocused,fps=samples.Count/samples.Sum(),p95Ms=ordered[(int)((ordered.Length-1)*.95f)]*1000,maxMs=ordered.Last()*1000});motor.Stop();Save();}}}
 IEnumerator Start(){yield return new WaitForSecondsRealtime(2);motor=FindAnyObjectByType<WorldMotor>();control=FindAnyObjectByType<WorldCamera>();run=motor.GetComponent<WorldRunInput>();env=FindAnyObjectByType<WorldEnvironment>();camera=control.GetComponent<Camera>();control.nativeInput=false;run.keyboardEnabled=false;if(mode=="-roadCapture")yield return Pictures();else if(mode=="-roadTraverse")yield return Traverse();else yield return Performance();Save();yield return new WaitForSecondsRealtime(.5f);Application.Quit(failures==0&&errors.Count==0?0:1);}
}
}
