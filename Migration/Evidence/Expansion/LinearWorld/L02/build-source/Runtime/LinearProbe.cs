using System;
using System.IO;
using System.Linq;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
namespace Vesper.Expansion.LinearWorld {
// Opt-in evidence only; fixture capture is explicitly separate from traversal and native input.
public sealed class LinearProbe:MonoBehaviour {
 [Serializable]public class Perf{public string name;public int frames,unfocused;public float fps,p95Ms,maxMs;}
 [Serializable]public class Report{public string mode,device,note;public int width,height,failures,fixtures,frames,clicks,drags,zooms,resets,rejected,safetyStops;public float distance;public Vector3 position;public string[] checks,errors;public Perf[] performance;}
 string mode,output;WorldMotor motor;WorldCamera camera;WorldRunInput run;WorldEnvironment environment;Camera cam;
 List<string> checks=new List<string>(),errors=new List<string>();List<Perf> perf=new List<Perf>();int failures,fixtures,frames;float distance;StreamWriter trace;
 [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.AfterSceneLoad)]static void Install(){var args=Environment.GetCommandLineArgs();foreach(string option in new[]{"-linearCapture","-linearTraverse","-linearPerformance","-linearManual"}){int i=Array.IndexOf(args,option);if(i<0||i+1>=args.Length)continue;var p=new GameObject("Linear evidence").AddComponent<LinearProbe>();p.mode=option;p.output=args[i+1];Directory.CreateDirectory(p.output);break;}}
 void OnEnable(){Application.logMessageReceived+=Log;}void OnDisable(){Application.logMessageReceived-=Log;trace?.Dispose();}
 void Log(string message,string stack,LogType type){if(type==LogType.Error||type==LogType.Exception||type==LogType.Assert)errors.Add(message);}
 void Check(bool ok,string message){checks.Add((ok?"PASS ":"FAIL ")+message);if(!ok)failures++;Save();}
 void Save(){if(!motor)return;File.WriteAllText(output+"/report.json",JsonUtility.ToJson(new Report{mode=mode,device=SystemInfo.graphicsDeviceName,note="Runtime originals. Capture placements are fixtures, not traversal. Synthetic screen pointers are not native device acceptance. Frame cadence is not display-present timing.",width=Screen.width,height=Screen.height,failures=failures,fixtures=fixtures,frames=frames,clicks=camera.clicks,drags=camera.drags,zooms=camera.zooms,resets=camera.resets,rejected=camera.blocked,safetyStops=motor.SafetyStops,distance=distance,position=motor.transform.position,checks=checks.ToArray(),errors=errors.ToArray(),performance=perf.ToArray()},true));}
 IEnumerator Snap(string name){yield return new WaitForEndOfFrame();ScreenCapture.CaptureScreenshot(output+"/"+name+".png");yield return null;}
 IEnumerator Place(float d){motor.Stop();motor.transform.position=WorldLayout.Point(d);motor.transform.rotation=Quaternion.Euler(0,180,0);fixtures++;yield return new WaitForSecondsRealtime(2.6f);}
 IEnumerator Pictures(){foreach(float d in new[]{25f,85f,150f,215f,275f}){yield return Place(d);yield return Snap("hero-"+d);foreach(float delta in new[]{-5f,5f}){yield return Place(d+delta);yield return Snap("near-"+(d+delta));}}}
 IEnumerator Reach(Vector3 target,string label){
  var screen=cam.WorldToScreenPoint(target);int clicks=camera.clicks,blocks=camera.blocked;camera.HandlePointer(EventType.MouseDown,0,screen);camera.HandlePointer(EventType.MouseUp,0,screen);
  Check(screen.z>0&&screen.x>0&&screen.x<Screen.width&&screen.y>0&&screen.y<Screen.height&&camera.clicks==clicks+1&&camera.blocked==blocks,label+" screen click accepted");
  if(camera.blocked!=blocks)yield break;
  float until=Time.realtimeSinceStartup+20;bool support=true,body=true,continuity=true;var prev=motor.transform.position;var weight=environment.Weights;int serial=motor.ResetSerial;
  while(motor.IsWalking&&Time.realtimeSinceStartup<until){yield return null;var p=motor.transform.position;float step=Vector3.Distance(prev,p);support&=motor.Ground(p,out var hit)&&Mathf.Abs(hit.point.y-p.y)<.13f;body&=motor.BodyClear(p);continuity&=step<run.runningSpeed*Mathf.Min(Time.deltaTime,.05f)+.06f&&motor.ResetSerial==serial&&(environment.Weights-weight).magnitude<.07f;distance+=step;frames++;trace?.WriteLine(FormattableString.Invariant($"{Time.realtimeSinceStartup:F4},{p.x:F4},{p.y:F4},{p.z:F4},{step:F5},{environment.Weights.x:F4},{environment.Weights.y:F4},{environment.Weights.z:F4},{support},{body}"));prev=p;weight=environment.Weights;}
  Check(!motor.IsWalking&&Vector3.Distance(motor.transform.position,target)<.35f&&support&&body&&continuity,label+" arrival/support/body/climate continuity; "+motor.LastReject);
 }
 IEnumerator Traverse(){
  trace=new StreamWriter(output+"/changed-route.csv");trace.WriteLine("time,x,y,z,step,clear,rain,snow,supported,bodyClear");
  yield return Place(0);run.SetRunning(true);
  for(float d=6;d<=300;d+=6){yield return Reach(WorldLayout.Point(d),"straight "+d);if(failures>0)break;if(d==24||d==84||d==150||d==216||d==276)yield return Snap("travel-"+d);}
  Check(motor.SafetyStops==0,"No movement safety abort");
  // Local return tests on the bridge and both weather blends, not the old450-click bundle.
  foreach(float d in new[]{28f,96f,228f}){yield return Place(d);run.SetRunning(false);yield return Reach(WorldLayout.Point(d-6),"local reverse "+d);}
  var weather=environment.GetComponent<WorldWeather>();Check(weather.RainWeight(WorldLayout.Point(25)+Vector3.up)<.001f,"No rain at clear river");Check(weather.SnowWeight(WorldLayout.Point(85)+Vector3.up)<.001f,"No snow in damp wood");
  var covered=environment.shelter.center;Check(weather.RainWeight(covered)==0&&weather.SnowWeight(covered)==0,"Roof bounds block weather");
  trace.Flush();trace.Dispose();trace=null;
 }
 IEnumerator Performance(){foreach(float d in new[]{25f,85f,150f,215f,275f}){yield return Place(d);foreach(string action in new[]{"static","walk","orbit"}){if(action=="walk"){run.SetRunning(false);motor.Walk(WorldLayout.Point(d+18));}var data=new List<float>();int unfocused=0;float start=Time.realtimeSinceStartup;while(Time.realtimeSinceStartup-start<6){if(action=="orbit")camera.Orbit(Mathf.Sin((Time.realtimeSinceStartup-start)*1.2f)*Time.unscaledDeltaTime*.10f,0);yield return null;data.Add(Time.unscaledDeltaTime);if(!Application.isFocused)unfocused++;}var ordered=data.OrderBy(x=>x).ToArray();perf.Add(new Perf{name=d+"-"+action,frames=data.Count,unfocused=unfocused,fps=data.Count/data.Sum(),p95Ms=ordered[(int)((ordered.Length-1)*.95f)]*1000,maxMs=ordered.Last()*1000});motor.Stop();Save();}}}
 IEnumerator Start(){yield return new WaitForSecondsRealtime(2);motor=FindAnyObjectByType<WorldMotor>();camera=FindAnyObjectByType<WorldCamera>();environment=FindAnyObjectByType<WorldEnvironment>();run=motor.GetComponent<WorldRunInput>();cam=camera.GetComponent<Camera>();if(mode=="-linearManual"){yield return Snap("manual-start");yield break;}run.keyboardEnabled=false;if(mode=="-linearCapture")yield return Pictures();else if(mode=="-linearTraverse")yield return Traverse();else yield return Performance();Save();yield return new WaitForSecondsRealtime(.4f);Application.Quit(failures==0&&errors.Count==0?0:1);}
 void Update(){if(mode!="-linearManual"||!motor)return;distance+=motor.Distance;frames++;if(Input.GetKeyDown(KeyCode.F6))StartCoroutine(Place(25));if(Input.GetKeyDown(KeyCode.F7))StartCoroutine(Place(150));if(Input.GetKeyDown(KeyCode.F8))StartCoroutine(Place(275));if(Input.GetKeyDown(KeyCode.F9))StartCoroutine(Snap("manual-"+DateTime.Now.ToString("HHmmss")));if(Input.GetKeyDown(KeyCode.F10)){Save();Application.Quit();}if(frames%60==0)Save();}
}
}
