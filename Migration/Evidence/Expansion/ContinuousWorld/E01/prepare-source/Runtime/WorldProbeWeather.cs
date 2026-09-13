using System;
using System.IO;
using System.Collections;
using UnityEngine;
namespace Vesper.Expansion.ContinuousWorld {
public sealed partial class WorldProbe {
 IEnumerator WeatherQA(){
  var weather=FindAnyObjectByType<WorldWeather>();Check(weather&&world.rain&&weather.splashes,"Rain and spatial weather owner exist");if(!weather||!world.rain)yield break;
  Check(weather.RainWeight(new Vector3(0,2,-48))==0&&weather.SnowWeight(new Vector3(0,2,-48))==0,"Clear river excludes both precipitation types spatially");
  Check(weather.RainWeight(new Vector3(30,10,-180))>.99f&&weather.SnowWeight(new Vector3(30,10,-180))==0,"Open abbey uses rain only");
  Check(weather.RainWeight(new Vector3(37,10,-187))==0,"Covered aisle spatial rain mask");
  Check(weather.SnowWeight(WorldLayout.Point(340)+Vector3.up)>.99f&&weather.RainWeight(WorldLayout.Point(340)+Vector3.up)==0,"White pass uses snow only");
  Check(Physics.Raycast(new Vector3(37,22,-187),Vector3.down,out var roofHit,14,WorldMotor.BlockMask)&&roofHit.point.y>15,"Real roof blocks falling precipitation above shelter");
  Check(!Physics.Raycast(new Vector3(30,22,-180),Vector3.down,12,WorldMotor.BlockMask),"Courtyard is open to sky");
  Check(!Physics.Raycast(new Vector3(30,12,-176),Vector3.right,16,WorldMotor.BlockMask),"Lancet window central opening is actual geometry");
  Check(Physics.Raycast(new Vector3(30,9.7f,-176),Vector3.right,16,WorldMotor.BlockMask),"Solid wall below lancet blocks ray");
  motor.Stop();motor.transform.position=WorldLayout.Point(180);control.SetZoom(10.3f);yield return new WaitForSecondsRealtime(4);run.SetRunning(false);
  foreach(var p in new[]{new Vector3(22,9,-182),new Vector3(27,9,-183),new Vector3(31,9,-184),new Vector3(35,9,-187),new Vector3(37,9,-187)}){yield return Reach(p,"Optional abbey shelter approach "+p);if(fatal)yield break;}
  yield return new WaitForSecondsRealtime(4);Check(world.Sheltered,"Player reaches covered space without reset");Check(world.rain.emission.rateOverTime.constant>1000,"Outdoor rain continues while player is sheltered");Check(weather.VisibleParticles(world.rain)>0,"Outside rain remains visible from shelter");yield return Capture("shelter-arrival");
  foreach(var p in new[]{new Vector3(32,9,-184),new Vector3(27,9,-183),new Vector3(22,9,-182),WorldLayout.Point(180)}){yield return Reach(p,"Shelter return "+p);if(fatal)yield break;}
  Check(!world.Sheltered&&motor.ResetSerial==0&&motor.SafetyStops==0,"Shelter round trip exits normally");
  ExpectBlocked(new Vector3(24,12,-192),"Opaque abbey wall");
  foreach(float d in new[]{48f,120f,180f,265f,342f}){motor.Stop();motor.transform.position=d==48?new Vector3(WorldLayout.Center(48.5f),WorldLayout.Level(48),-48):WorldLayout.Point(d);yield return new WaitForSecondsRealtime(4);int visibleRain=weather.VisibleParticles(world.rain),visibleSnow=weather.VisibleParticles(world.snow,true);Check(d==48?visibleRain==0&&visibleSnow==0:d==180?visibleRain>0:d==342&&world.snow?visibleSnow>0:true,"Local precipitation at "+d+" rain="+visibleRain+" snow="+visibleSnow);Check(world.waterAudio&&world.rainAudio&&world.windAudio&&world.waterAudio.isPlaying&&world.rainAudio.isPlaying&&world.windAudio.isPlaying,"Looping ambience at "+d+" volumes="+world.waterAudio.volume.ToString("F3")+","+world.rainAudio.volume.ToString("F3")+","+world.windAudio.volume.ToString("F3"));yield return Capture("weather-"+d);}
 }
 IEnumerator Film(){
  // Internal render sequence at natural simulation speed. This is not an FPS benchmark.
  Directory.CreateDirectory(output+"/frames");int frame=0;run.SetRunning(false);var timing=new StreamWriter(output+"/frames.csv");timing.WriteLine("file,realtime,fixture");
  foreach(float d in new[]{45f,95f,120f,145f,180f,242f,265f,292f,342f}){
   motor.Stop();motor.transform.position=d==45?new Vector3(WorldLayout.Center(48.5f),WorldLayout.Level(45),-45):WorldLayout.Point(d);control.SetZoom(d==45?8.2f:11.1f);yield return new WaitForSecondsRealtime(3);
   float start=Time.realtimeSinceStartup;int local=0;while(Time.realtimeSinceStartup-start<6){if(local==12)Click(WorldLayout.Point(d+5));yield return new WaitForEndOfFrame();string file="frames/frame-"+(frame++).ToString("D5")+".png";ScreenCapture.CaptureScreenshot(output+"/"+file);timing.WriteLine(FormattableString.Invariant($"{file},{Time.realtimeSinceStartup:F5},{d}"));local++;yield return new WaitForSecondsRealtime(1f/12);}
   checks.Add("SEQUENCE fixture "+d+" frames="+local);
  }
  timing.Dispose();Save();
 }
}
}
