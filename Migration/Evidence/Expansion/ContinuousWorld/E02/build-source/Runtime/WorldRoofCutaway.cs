using UnityEngine;
using UnityEngine.Rendering;
namespace Vesper.Expansion.ContinuousWorld {
// The real roof collider and its shade remain while the local camera sees the traveler below.
public sealed class WorldRoofCutaway:MonoBehaviour {
 public WorldEnvironment world;Material[] materials;float opacity=1;
 void Start(){var list=new System.Collections.Generic.List<Material>();foreach(var r in GetComponentsInChildren<Renderer>())foreach(var material in r.materials){material.SetFloat("_Surface",1);material.SetFloat("_SrcBlend",(float)BlendMode.SrcAlpha);material.SetFloat("_DstBlend",(float)BlendMode.OneMinusSrcAlpha);material.SetFloat("_ZWrite",0);material.EnableKeyword("_SURFACE_TYPE_TRANSPARENT");material.renderQueue=3000;list.Add(material);}materials=list.ToArray();}
 void Update(){if(materials==null||!world)return;opacity=Mathf.MoveTowards(opacity,world.Sheltered?.12f:1,Time.deltaTime*2);foreach(var m in materials){var c=m.GetColor("_BaseColor");c.a=opacity;m.SetColor("_BaseColor",c);}}
 void OnDestroy(){if(materials!=null)foreach(var m in materials)Destroy(m);}
}
}
