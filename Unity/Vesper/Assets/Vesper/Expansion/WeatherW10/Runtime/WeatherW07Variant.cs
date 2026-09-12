using UnityEngine;
namespace Vesper.Expansion.WeatherW10 {
// Retains the W06 visual inside the new scene for exact in-process comparison fixtures.
public sealed class WeatherW07Variant:MonoBehaviour {
 public GameObject originalRoof,correctedRoof;public WeatherW07Flash flash;
 public void ShowBaseline(bool baseline){
  correctedRoof.SetActive(!baseline);flash.enabled=!baseline;
  foreach(var r in originalRoof.GetComponentsInChildren<Renderer>()){r.enabled=baseline;if(baseline)foreach(var m in r.materials){m.SetFloat("_Surface",1);m.SetFloat("_SrcBlend",5);m.SetFloat("_DstBlend",10);m.SetFloat("_ZWrite",0);m.EnableKeyword("_SURFACE_TYPE_TRANSPARENT");m.renderQueue=3000;}}
 }
}
}
