using System.Collections;
using System.Linq;
using UnityEngine;
namespace Vesper.Expansion.ContinuousWorld {
public sealed partial class WorldProbe {
 IEnumerator MaterialDiagnostics(){
  var mats=FindObjectsByType<Renderer>().SelectMany(r=>r.sharedMaterials).Where(m=>m&&m.HasProperty("_Diagnostic")).Distinct().ToArray();
  foreach(var m in mats)checks.Add("MATERIAL "+m.name+" shader="+m.shader.name+" texture="+(m.GetTexture("_BaseMap")?m.GetTexture("_BaseMap").name:"none"));
  foreach(float d in new[]{180f,342f}){
   motor.Stop();motor.transform.position=WorldLayout.Point(d);control.SetZoom(11.1f);yield return new WaitForSecondsRealtime(3);
   foreach(float channel in new[]{0f,1f,2f,3f}){foreach(var m in mats)m.SetFloat("_Diagnostic",channel);yield return new WaitForSecondsRealtime(.3f);yield return Capture("material-"+d+"-channel-"+channel);}
  }
  foreach(var m in mats)m.SetFloat("_Diagnostic",0);Save();
 }
}
}
