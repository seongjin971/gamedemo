using System.Linq;
using UnityEngine;
using UnityEditor;
namespace Vesper.Expansion.ContinuousWorld.Editor {
public static partial class WorldVisuals {
 // Run only on a freshly generated, separately named Visual F candidate.
 public static void RecomposeVisualF(GameObject collision, WorldEnvironment world) {
  foreach(var r in collision.GetComponentsInChildren<MeshRenderer>())if(r.name.StartsWith("Continuous terrain"))r.sharedMaterial.shader=Shader.Find("Vesper/VisualF/Ground");
  var abbey=GameObject.Find("Rainwood and roofless abbey").transform;
  var models=abbey.Cast<Transform>().ToArray();
  foreach(var t in models) {
   var p=t.position;
   // Remove unsupported upper belfry fragments; replace with grounded rear masonry below.
   if(p.y>15.5f && t.name.Contains("Lancet")) {Object.DestroyImmediate(t.gameObject);continue;}
   if(t.name.Contains("GothicButtress") && t.localScale.y>2) {Object.DestroyImmediate(t.gameObject);continue;}
   // The entry now addresses the road, with room for the traveler to approach it.
   if(t.name.Contains("EntranceArch")) {t.position=new Vector3(24,9,-182);t.rotation=Quaternion.Euler(0,90,0);}
   if(t.name.Contains("BrokenSlateRoof")) {t.position=new Vector3(31,15.75f,-188);}
   // Existing east-aisle roof posts move with the roof, preserving a load-bearing frame.
   if(t.name.Contains("GothicButtress") && (Mathf.Abs(p.x-34)<.1f||Mathf.Abs(p.x-40)<.1f) && (Mathf.Abs(p.z+184)<.1f||Mathf.Abs(p.z+192)<.1f)) t.position=p+Vector3.left*6;
   // Exterior marker belongs beside the building, never in the exposed chapel floor.
  }
  foreach(float d in new[]{184f,192f}) {
   Model(abbey,"Chapel/CW_ChapelEntranceArch",new Vector3(31,9,-d),new Vector3(1.2f,1.125f,1),0,true);
  }
  Model(abbey,"ChapelBroken/CW_ChapelBrokenWall6m",new Vector3(31,9,-198),new Vector3(1.1f,1.1f,1),0,true);
  Model(abbey,"Chapel/CW_ChapelLancetWall",new Vector3(41.5f,9,-198),Vector3.one,0,true);
  world.shelter=new Bounds(new Vector3(31,12.2f,-187.6f),new Vector3(5.6f,6.8f,6.8f));
  foreach(var t in collision.GetComponentsInChildren<Transform>())if(t.name=="Route waystone 175")t.position=new Vector3(21.8f,9.65f,-168);
  // Rubble follows broken wall feet in long tapered groups; openings remain clear.
  foreach(float d in new[]{169f,174f,191f,197f}) {
   var strip=Model(abbey,"AbbeyRubbleV2/CW_AbbeyRubbleStrip6m",new Vector3(23.65f,8.96f,-d),new Vector3(.8f,.65f,1.0f),90);
  }
  // Wall tops and floor remain spatially independent, with real shadow-casting thickness.
  var snow=GameObject.Find("Frost ascent and white pass").transform;
  foreach(var t in snow.Cast<Transform>().ToArray()) {
   float d=-t.position.z;
   if(d>=365 && d<390 && (t.name.Contains("Limestone")||t.name.Contains("LayeredRock")))Object.DestroyImmediate(t.gameObject);
  }
  // Asymmetric embedded ledges replace two identical perched rocks and thin pedestals.
  SnowLedge(snow,-23.5f,370.5f,new Vector3(1.55f,.90f,1.65f),22,3.1f);
  SnowLedge(snow,-25.2f,377.5f,new Vector3(1.9f,1.8f,1.55f),-26,5.0f);
  SnowLedge(snow,-28.2f,383.5f,new Vector3(2.1f,2.15f,1.8f),63,5.6f);
  SnowLedge(snow,-.8f,371.5f,new Vector3(1.18f,.78f,1.35f),-38,2.1f);
  SnowLedge(snow,1.8f,379,new Vector3(1.55f,1.1f,1.3f),37,3.2f);
  foreach(var t in snow.Cast<Transform>().ToArray()) {
   float d=-t.position.z;
   if(d>350 && d<400 && (t.name.Contains("AlpineFir"))) {var p=t.position;p.y=WorldLayout.Height(p.x,d)-.1f;t.position=p;}
  }
  EditorUtility.SetDirty(world);
 }
 static void SnowLedge(Transform parent,float x,float d,Vector3 scale,float yaw,float embed) {
  var pos=new Vector3(x,WorldLayout.Height(x,d)-embed,-d);
  Model(parent,"CW_HF_Limestone",pos,scale,yaw,true,true);
  Model(parent,"SnowCover/CW_HF_Limestone_SnowCover",pos,scale,yaw);
 }
}
}
