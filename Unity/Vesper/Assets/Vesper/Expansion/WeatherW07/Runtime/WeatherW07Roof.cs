using UnityEngine;
using UnityEngine.Rendering;
using Vesper.Expansion.WeatherWorld;
namespace Vesper.Expansion.WeatherW07 {
// Opaque slate depth at rest prevents back-facing slates and timber drawing over the roof.
// Only fade the canopy when the traveler actually enters the original shelter volume.
public sealed class WeatherW07Roof:MonoBehaviour {
 public WorldEnvironment world;
 Material[] materials;float opacity=1;bool transparent;
 void Start(){var list=new System.Collections.Generic.List<Material>();foreach(var r in GetComponentsInChildren<Renderer>())foreach(var m in r.materials)list.Add(m);materials=list.ToArray();SetSurface(false);}
 void SetSurface(bool fade){transparent=fade;foreach(var m in materials){
  m.SetFloat("_Surface",fade?1:0);m.SetFloat("_SrcBlend",(float)(fade?BlendMode.SrcAlpha:BlendMode.One));m.SetFloat("_DstBlend",(float)(fade?BlendMode.OneMinusSrcAlpha:BlendMode.Zero));m.SetFloat("_ZWrite",fade?0:1);
  if(fade)m.EnableKeyword("_SURFACE_TYPE_TRANSPARENT");else m.DisableKeyword("_SURFACE_TYPE_TRANSPARENT");m.renderQueue=fade?3000:2000;
 }}
 void Update(){if(materials==null||!world)return;opacity=Mathf.MoveTowards(opacity,world.Sheltered?.12f:1,Time.deltaTime*2);bool fade=opacity<.999f;if(fade!=transparent)SetSurface(fade);foreach(var m in materials){var c=m.GetColor("_BaseColor");c.a=opacity;m.SetColor("_BaseColor",c);}}
 void OnDestroy(){if(materials!=null)foreach(var m in materials)Destroy(m);}
}
}
