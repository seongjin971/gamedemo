using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using UnityEngine;

namespace Vesper.Expansion.P2 {
// Opt-in standalone regression. Synthesized IMGUI samples, not native input.
public sealed class P2ClickProbe:MonoBehaviour {
 string output; readonly List<string> checks=new List<string>(); int failures;
 P2Camera control; P2Motor motor; Camera cam; P2World world;
 [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.AfterSceneLoad)] static void Install(){
  var args=Environment.GetCommandLineArgs();int i=Array.IndexOf(args,"-p2ClickQA");if(i<0||i+1>=args.Length)return;
  var probe=new GameObject("Opt-in click regression").AddComponent<P2ClickProbe>();probe.output=args[i+1];Directory.CreateDirectory(probe.output);Application.runInBackground=true;
 }
 void Check(bool ok,string name){checks.Add((ok?"PASS ":"FAIL ")+name);if(!ok)failures++;}
 bool Click(Vector3 point){int blocked=control.blocked,clicks=control.clicks;var screen=cam.WorldToScreenPoint(point);control.HandlePointer(EventType.MouseDown,0,screen);control.HandlePointer(EventType.MouseUp,0,screen);return control.clicks==clicks+1&&control.blocked==blocked;}
 IEnumerator Reach(Vector3 point,string name){
  Check(Click(point),name+" screen click accepted");
  float until=Time.realtimeSinceStartup+15;
  bool supported=true,clear=true;int samples=0;
  while(motor.IsWalking&&Time.realtimeSinceStartup<until){
   var p=motor.transform.position;
   supported &= Physics.CheckSphere(p+Vector3.up*.035f,.14f,P2Motor.SurfaceMask,QueryTriggerInteraction.Ignore);
   clear &= !Physics.CheckCapsule(p+Vector3.up*.3f,p+Vector3.up*1.4f,.2f,P2Motor.SurfaceMask|P2Motor.BlockMask,QueryTriggerInteraction.Ignore);
   samples++;yield return null;
  }
  Check(Vector3.Distance(motor.transform.position,motor.ClickDestination)<.15f,name+" destination reached at "+motor.transform.position+" target "+motor.ClickDestination);
  Check(supported&&clear&&samples>0,name+" ground support/body clearance over "+samples+" movement frames");
 }
 IEnumerator Start(){
  yield return new WaitForSecondsRealtime(2);
  control=FindAnyObjectByType<P2Camera>();motor=control.player;cam=control.GetComponent<Camera>();world=P2World.Instance;
  ScreenCapture.CaptureScreenshot(output+"/courtyard-before.png");
  yield return new WaitForSecondsRealtime(.25f);
  yield return Reach(new Vector3(4.73f,0,.24f),"User rejected paving A");
  control.ResetView();yield return new WaitForSecondsRealtime(1);
  yield return Reach(new Vector3(4.68f,0,.35f),"User rejected paving B");
  ScreenCapture.CaptureScreenshot(output+"/courtyard-arrival.png");
  yield return new WaitForSecondsRealtime(.25f);
  control.ResetView();yield return new WaitForSecondsRealtime(1);
  yield return Reach(new Vector3(-.08f,-.08f,13.02f),"User rejected front paving");
  yield return Reach(new Vector3(0,-.08f,17.5f),"Wide front paving");
  ScreenCapture.CaptureScreenshot(output+"/expanded-front.png");yield return new WaitForSecondsRealtime(.25f);
  control.ResetView();yield return new WaitForSecondsRealtime(1);
  yield return Reach(new Vector3(5.2f,-.12f,2.08f),"User rejected tree-side open paving");
  ScreenCapture.CaptureScreenshot(output+"/expanded-tree-side.png");yield return new WaitForSecondsRealtime(.25f);
  control.ResetView();yield return new WaitForSecondsRealtime(1);
  Check(!Click(new Vector3(6,2,4)),"Actual tree trunk stays blocked");
  Check(!Click(new Vector3(-6.3f,1.3f,10.3f)),"Gateway pier stays blocked");
  Check(!Click(new Vector3(0,-.1f,24)),"Beyond front ground stays blocked");
  int clicks=control.clicks;float angle=control.Angle;
  control.HandlePointer(EventType.MouseUp,0,new Vector3(800,400));
  Check(control.clicks==clicks,"Orphan release does not click");
  control.HandlePointer(EventType.MouseDown,0,new Vector3(800,400));control.HandlePointer(EventType.MouseDrag,0,new Vector3(840,400));control.HandlePointer(EventType.MouseUp,0,new Vector3(840,400));
  yield return new WaitForSecondsRealtime(.5f);
  Check(control.clicks==clicks&&Mathf.Abs(control.Angle-angle)>.01f,"Drag orbits without moving");
  control.ResetView();yield return new WaitForSecondsRealtime(1);
  // Enter from an unobstructed screen ray to the opening floor.
  Check(Click(world.courtyardGate),"Courtyard gate screen click accepted");
  float deadline=Time.realtimeSinceStartup+15;while((world.Zone!=1||world.Busy)&&Time.realtimeSinceStartup<deadline)yield return null;
  Check(world.Zone==1&&!world.Busy,"Click reaches crossing transition");
  if(world.Zone==1){
   yield return Reach(new Vector3(0,1.6f,-2.5f),"Bridge screen click");
   Check(!Click(new Vector3(5,-.6f,-2.5f)),"Water stays blocked");
   Check(!Click(new Vector3(6,2.95f,-7)),"Disconnected ledge stays blocked");
   ScreenCapture.CaptureScreenshot(output+"/bridge.png");
   yield return new WaitForSecondsRealtime(.25f);
   Check(Click(world.connectionGate),"Return gate screen click accepted");
   deadline=Time.realtimeSinceStartup+15;while((world.Zone!=0||world.Busy)&&Time.realtimeSinceStartup<deadline)yield return null;
   Check(world.Zone==0&&!world.Busy,"Click returns to courtyard");
  }
  yield return new WaitForSecondsRealtime(.5f);
  File.WriteAllLines(output+"/checks.txt",checks);
  File.WriteAllText(output+"/summary.txt",$"Synthesized pointer events through production handler, raycast, NavMesh and moving player. Native input is separate. checks={checks.Count}; failures={failures}");
  Application.Quit(failures==0?0:1);
 }
}
}
