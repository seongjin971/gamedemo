using System.Collections;
using System.Collections.Generic;
using System.Linq;
using UnityEngine;
namespace Vesper.Expansion.ContinuousWorld {
public sealed partial class WorldProbe {
 IEnumerator Ablation(){
  // Explicit diagnostic mode only: isolate active effects without altering project/shared assets.
  var reflections=new[]{world.reflection,world.ruinsReflection}.Where(r=>r).ToArray();
  var weather=new[]{world.rain,world.snow,FindAnyObjectByType<WorldWeather>()?.splashes}.Where(p=>p).ToArray();var shadows=world.sun.shadows;
  try{
   foreach(float d in new[]{48f,180f,342f}){
    motor.Stop();motor.transform.position=WorldLayout.Point(d);control.SetZoom(11.1f);yield return new WaitForSecondsRealtime(4);
    foreach(string variant in new[]{"all","reflection-off","precipitation-off","shadows-off"}){
     foreach(var r in reflections)r.gameObject.SetActive(variant!="reflection-off");
     foreach(var p in weather)p.gameObject.SetActive(variant!="precipitation-off");
     world.sun.shadows=variant=="shadows-off"?LightShadows.None:shadows;
     yield return new WaitForSecondsRealtime(2);
     var times=new List<float>();int unfocused=0;float start=Time.realtimeSinceStartup;
     while(Time.realtimeSinceStartup-start<6){yield return null;times.Add(Time.unscaledDeltaTime);if(!Application.isFocused)unfocused++;}
     var ordered=times.OrderBy(t=>t).ToArray();performances.Add(new Performance{name=d+"-"+variant,frames=times.Count,unfocused=unfocused,fps=times.Count/times.Sum(),p95Ms=ordered[(int)((ordered.Length-1)*.95f)]*1000,maxMs=ordered[ordered.Length-1]*1000});Save();
    }
   }
  }finally{foreach(var r in reflections)r.gameObject.SetActive(true);foreach(var p in weather)p.gameObject.SetActive(true);world.sun.shadows=shadows;}
 }
}
}
