using System;
using System.IO;
using System.Linq;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.AI;
namespace Vesper.Expansion.ContinuousWorld {
// Opt-in QA only. Screen-derived synthetic input is reported separately from native events.
public sealed partial class WorldProbe:MonoBehaviour {
 [Serializable]public class Performance{public string name;public int frames,unfocused;public float fps,p95Ms,maxMs;}
 [Serializable]public class Report{public string mode,device,note;public int width,height,failures,samples,clicks,blocked,drags,zooms,resets,safetyStops;public float distance;public string[] checks,errors;public Performance[] performance;}
 string output,mode;WorldMotor motor;WorldCamera control;WorldRunInput run;WorldEnvironment world;Camera cam;
 readonly List<string> checks=new List<string>(),errors=new List<string>();readonly List<Performance> performances=new List<Performance>();
 int failures,samples;float distance;StreamWriter trace;float nextManualSave;bool fatal;
 [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.AfterSceneLoad)]static void Install(){
  var args=Environment.GetCommandLineArgs();foreach(string option in new[]{"-worldQA","-worldEdges","-worldManual","-worldPerformance","-worldCapture","-worldWeatherQA","-worldFilm"}){int i=Array.IndexOf(args,option);if(i<0||i+1>=args.Length)continue;var p=new GameObject("Opt-in world evidence").AddComponent<WorldProbe>();p.output=args[i+1];p.mode=option;Directory.CreateDirectory(p.output);Application.runInBackground=true;break;}
 }
 void OnEnable(){Application.logMessageReceived+=Log;}void OnDisable(){Application.logMessageReceived-=Log;trace?.Dispose();}
 void Log(string m,string s,LogType t){if(t==LogType.Error||t==LogType.Exception||t==LogType.Assert)errors.Add(m);}
 void Check(bool ok,string name){checks.Add((ok?"PASS ":"FAIL ")+name);if(!ok)failures++;Debug.Log("WORLD CHECK "+checks[checks.Count-1]);Save();}
 void Save(){if(!motor||!control)return;File.WriteAllText(output+"/report.json",JsonUtility.ToJson(new Report{mode=mode,device=SystemInfo.graphicsDeviceName,note="Opt-in runtime evidence. Synthetic pointer checks and automatic placement are not native device acceptance. Natural frame cadence is not display-present timing.",width=Screen.width,height=Screen.height,failures=failures,samples=samples,distance=distance,clicks=control.clicks,blocked=control.blocked,drags=control.drags,zooms=control.zooms,resets=control.resets,safetyStops=motor.SafetyStops,checks=checks.ToArray(),errors=errors.ToArray(),performance=performances.ToArray()},true));}
 void Update(){
  if(!motor)return;
  if(mode=="-worldManual"){
   distance+=motor.Distance;samples++;
   if(Time.unscaledTime>nextManualSave){nextManualSave=Time.unscaledTime+1;Save();}
   if(Input.GetKeyDown(KeyCode.F9))StartCoroutine(Capture("manual-"+DateTime.Now.ToString("HHmmss")));
   if(Input.GetKeyDown(KeyCode.F10)){Save();Application.Quit();}
  }
 }
 IEnumerator Capture(string name){yield return new WaitForEndOfFrame();ScreenCapture.CaptureScreenshot(output+"/"+name+".png");yield return null;}
 bool Click(Vector3 p){
  var screen=cam.WorldToScreenPoint(p);if(screen.x<4||screen.x>Screen.width-4||screen.y<4||screen.y>Screen.height-4||screen.z<=0){Debug.Log("WORLD OFFSCREEN "+p+" "+screen);return false;}
  int count=control.clicks,blocked=control.blocked;control.HandlePointer(EventType.MouseDown,0,screen);control.HandlePointer(EventType.MouseUp,0,screen);return control.clicks==count+1&&control.blocked==blocked;
 }
 void ExpectBlocked(Vector3 p,string label){int count=control.clicks,rejections=control.blocked;Click(p);Check(control.clicks==count+1&&control.blocked==rejections+1,label+" received visible screen click and rejected: "+motor.LastReject);}
 IEnumerator Reach(Vector3 p,string name,bool record=true){
  bool clicked=Click(p);Check(clicked,name+" screen input -> ray -> complete path"+(clicked?"":" rejected="+motor.LastReject));if(!clicked){fatal=true;yield break;}
  float deadline=Time.realtimeSinceStartup+35;bool support=true,clear=true,continuous=true;int count=0;float maxStep=0;var prev=motor.transform.position;var weights=world.Weights;int reset=motor.ResetSerial;
  while(motor.IsWalking&&Time.realtimeSinceStartup<deadline){yield return null;var pos=motor.transform.position;float step=Vector3.Distance(prev,pos);maxStep=Mathf.Max(maxStep,step);
   support &= motor.Ground(pos,out var hit)&&Mathf.Abs(hit.point.y-pos.y)<.13f;clear &=motor.BodyClear(pos);
   continuous &=step<=run.runningSpeed*Mathf.Min(Time.deltaTime,.05f)+.05f&&motor.ResetSerial==reset&&(world.Weights-weights).magnitude<.06f;
   count++;samples++;distance+=step;if(trace!=null&&record)trace.WriteLine(FormattableString.Invariant($"{Time.realtimeSinceStartup:F4},{pos.x:F4},{pos.y:F4},{pos.z:F4},{step:F5},{world.Weights.x:F4},{world.Weights.y:F4},{world.Weights.z:F4},{support},{clear}"));prev=pos;weights=world.Weights;
  }
  bool arrived=!motor.IsWalking&&Vector3.Distance(motor.transform.position,motor.ClickDestination)<.30f;
  Check(arrived&&support&&clear&&continuous&&count>0,name+" arrival/support/body/continuity frames="+count+" arrived="+arrived+" supported="+support+" clear="+clear+" continuous="+continuous+" maxStep="+maxStep.ToString("F3")+" actual="+motor.transform.position+" wanted="+motor.ClickDestination+" last="+motor.LastReject);
  if(!arrived||!support||!clear||!continuous){fatal=true;yield break;}
 }
 IEnumerator Route(){
  trace=new StreamWriter(output+"/traversal.csv");trace.WriteLine("time,x,y,z,step,clearWeight,rainWeight,snowWeight,support,bodyClear");
  Check(FindObjectsByType<WorldMotor>().Length==1&&FindObjectsByType<WorldCamera>().Length==1,"One player and one input camera");
  Check(!FindAnyObjectByType<Vesper.Expansion.P2.P2World>(),"No P2 fade/teleport/zone transition owner");
  int priorClicks=control.clicks;control.HandlePointer(EventType.MouseUp,0,new Vector3(700,400));Check(control.clicks==priorClicks,"Orphan release ignored");
  float angle=control.Angle;control.HandlePointer(EventType.MouseDown,0,new Vector3(700,400));control.HandlePointer(EventType.MouseDrag,0,new Vector3(760,400));control.HandlePointer(EventType.MouseUp,0,new Vector3(760,400));yield return new WaitForSecondsRealtime(.5f);Check(control.clicks==priorClicks&&Mathf.Abs(control.Angle-angle)>.02f,"Drag changes camera without click");control.Orbit(.24f,0);yield return new WaitForSecondsRealtime(.6f);
  for(int trip=0;trip<3;trip++){
   run.SetRunning(true);
   for(int direction=0;direction<2;direction++){
    for(int j=1;j<=75;j++){
     float d=direction==0?j*5:375-j*5;var p=WorldLayout.Point(d);
     if(d>42&&d<56)p.x=WorldLayout.Center(48.5f);
     yield return Reach(p,"trip"+(trip+1)+" "+(direction==0?"out ":"back ")+d);
     if(fatal)yield break;
     if(trip==0&&(j%15==0||d==45||d==120||d==265))yield return Capture((direction==0?"out-":"back-")+d);
     if(d==120||d==265){motor.Stop();yield return new WaitForSecondsRealtime(.2f);var weight=world.Weights;yield return new WaitForSecondsRealtime(.25f);Check((world.Weights-weight).magnitude<.0001f,"Stable climate while stopped at "+d);}
    }
   }
   Check(motor.ResetSerial==0,"Full continuous round trip "+(trip+1)+" without reset");
  }
  trace.Flush();trace.Dispose();trace=null;
  Check(motor.SafetyStops==0,"No movement safety abort during full route");
 }
 IEnumerator Measure(){
  foreach(float d in new[]{48f,120f,180f,265f,342f}){
   motor.Stop();motor.transform.position=d==48?new Vector3(WorldLayout.Center(48.5f),WorldLayout.Level(48),-48):WorldLayout.Point(d);yield return new WaitForSecondsRealtime(2.5f);
   foreach(string action in new[]{"static","walk","orbit","zoom"}){
    run.SetRunning(false);if(action=="walk")motor.Walk(WorldLayout.Point(d+12));
    var timings=new List<float>();int unfocused=0;float start=Time.realtimeSinceStartup;
    while(Time.realtimeSinceStartup-start<8){if(action=="orbit")control.Orbit(Mathf.Sin((Time.realtimeSinceStartup-start)*1.1f)*Time.unscaledDeltaTime*.10f,0);if(action=="zoom")control.SetZoom(11.1f+Mathf.Sin(Time.realtimeSinceStartup-start)*1.8f);yield return null;timings.Add(Time.unscaledDeltaTime);if(!Application.isFocused)unfocused++;}
    var sorted=timings.OrderBy(x=>x).ToArray();performances.Add(new Performance{name=d+"-"+action,frames=timings.Count,unfocused=unfocused,fps=timings.Count/timings.Sum(),p95Ms=sorted[(int)((sorted.Length-1)*.95f)]*1000,maxMs=sorted[sorted.Length-1]*1000});motor.Stop();Save();
   }
  }
 }
 IEnumerator Edges(){
  // Explicit local fixture placements: not counted as seamless traversal or user input.
  foreach(float d in new[]{12f,35f,60f,82f,120f,165f,195f,230f,265f,315f,360f}){
   motor.Stop();motor.transform.position=WorldLayout.Point(d);yield return new WaitForSecondsRealtime(2.5f);run.SetRunning(false);
   float sole=float.PositiveInfinity;var baked=new Mesh();foreach(var skin in motor.GetComponentsInChildren<SkinnedMeshRenderer>()){skin.BakeMesh(baked);foreach(var v in baked.vertices)sole=Mathf.Min(sole,skin.transform.TransformPoint(v).y);}Destroy(baked);float soleGap=sole-motor.transform.position.y;Check(soleGap>-.12f&&soleGap<.22f,"Idle visible sole height "+d+" gap="+soleGap.ToString("F3"));
   yield return Reach(WorldLayout.Point(d+2,2.2f),"Walking side ground "+d);if(fatal)yield break;
   run.SetRunning(true);yield return Reach(WorldLayout.Point(d,-2.2f),"Running reverse side ground "+d);if(fatal)yield break;
  }
  motor.Stop();motor.transform.position=WorldLayout.Point(12);yield return new WaitForSecondsRealtime(2.5f);
  ExpectBlocked(WorldLayout.Point(18,3.8f)+Vector3.up,"Solid outcrop");
  var trunk=FindObjectsByType<CapsuleCollider>().Where(c=>c.name=="Tree trunk").OrderBy(c=>Vector3.Distance(c.bounds.center,motor.transform.position)).FirstOrDefault();if(trunk)ExpectBlocked(trunk.bounds.center,"Visible tree trunk");
  float bx=WorldLayout.Center(48.5f);motor.transform.position=new Vector3(bx,WorldLayout.Level(48.5f),-48.5f);yield return new WaitForSecondsRealtime(2.5f);
  ExpectBlocked(new Vector3(bx+6,-.1f,-48.5f),"Water without under-bridge fallback");
  ExpectBlocked(new Vector3(bx+3.1f,WorldLayout.Level(48.5f)+.7f,-48.5f),"Bridge parapet");
  yield return Capture("bridge-blockers");
  motor.Stop();motor.transform.position=WorldLayout.Point(110);yield return new WaitForSecondsRealtime(2.5f);
  run.SetRunning(false);foreach(float d in new[]{114f,118f,122f,118f,122f,118f,114f}){yield return Reach(WorldLayout.Point(d),"Walking climate boundary reverse "+d);if(fatal)yield break;motor.Stop();yield return new WaitForSecondsRealtime(.25f);}
  motor.Stop();motor.transform.position=WorldLayout.Point(255);yield return new WaitForSecondsRealtime(2.5f);
  foreach(float d in new[]{259f,263f,267f,263f,267f,263f,259f}){run.SetRunning(d==267);yield return Reach(WorldLayout.Point(d),"Snow boundary stop/reverse "+d);if(fatal)yield break;motor.Stop();yield return new WaitForSecondsRealtime(.25f);}
  float zoom=control.Zoom;control.SetZoom(6.5f);yield return new WaitForSecondsRealtime(1);var viewport=cam.WorldToViewportPoint(motor.transform.position+Vector3.up*.8f);Check(viewport.x>.1f&&viewport.x<.9f&&viewport.y>.1f&&viewport.y<.9f,"Close zoom keeps traveler in frame on slope");control.SetZoom(zoom);
  if(world.snow){motor.Stop();motor.transform.position=WorldLayout.Point(375);run.SetRunning(false);yield return new WaitForSecondsRealtime(3);yield return Reach(WorldLayout.Point(379),"Overlook forward ground");if(fatal)yield break;yield return Reach(WorldLayout.Point(382),"Overlook last safe ground");if(fatal)yield break;yield return new WaitForSecondsRealtime(2);float cliffX=WorldLayout.Center(375)-9.2f;var cliff=new Vector3(cliffX,WorldLayout.Height(cliffX,375),-375);ExpectBlocked(cliff,"Visible steep overlook face");yield return Capture("overlook-edge");yield return Reach(WorldLayout.Point(375),"Overlook return from edge");}
 }
 IEnumerator Start(){
  yield return new WaitForSecondsRealtime(2);motor=FindAnyObjectByType<WorldMotor>();control=FindAnyObjectByType<WorldCamera>();cam=control.GetComponent<Camera>();run=motor.GetComponent<WorldRunInput>();world=FindAnyObjectByType<WorldEnvironment>();
  if(mode=="-worldManual"){yield return Capture("manual-start");yield break;}run.keyboardEnabled=false;
  if(mode=="-worldQA")yield return Route();
  else if(mode=="-worldEdges")yield return Edges();
  else if(mode=="-worldPerformance")yield return Measure();
  else if(mode=="-worldWeatherQA")yield return WeatherQA();
  else if(mode=="-worldFilm")yield return Film();
  else foreach(float d in new[]{0f,35f,48f,70f,95f,120f,145f,180f,220f,242f,265f,292f,342f,375f}){motor.Stop();motor.transform.position=WorldLayout.Point(d);if(d>43&&d<54)motor.transform.position=new Vector3(WorldLayout.Center(48.5f),WorldLayout.Level(d),-d);yield return new WaitForSecondsRealtime(2);yield return Capture("view-"+d);}
  if(mode=="-worldCapture"){motor.Stop();motor.transform.position=new Vector3(WorldLayout.Center(48.5f),WorldLayout.Level(45),-45);control.SetZoom(8.2f);yield return new WaitForSecondsRealtime(4);yield return Capture("hero-water-45-zoom8_2");control.Orbit(.14f,-.10f);yield return new WaitForSecondsRealtime(2);yield return Capture("hero-water-open-angle");control.Orbit(-.14f,.10f);}
  if(mode=="-worldCapture"&&world.rain){motor.Stop();motor.transform.position=new Vector3(28,9,-180);control.SetZoom(11.1f);yield return new WaitForSecondsRealtime(4);yield return Capture("hero-abbey-west");motor.transform.position=new Vector3(37,9,-187);control.SetZoom(8.2f);yield return new WaitForSecondsRealtime(4);yield return Capture("sheltered-aisle");}
  trace?.Flush();Save();yield return new WaitForSecondsRealtime(.2f);Application.Quit(failures==0&&errors.Count==0?0:1);
 }
}
}
