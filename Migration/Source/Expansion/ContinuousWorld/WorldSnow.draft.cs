using System.Collections.Generic;
using UnityEngine;
using UnityEditor;
namespace Vesper.Expansion.ContinuousWorld.Editor {
public static partial class WorldVisuals {
 public static void SnowPass(GameObject collision,WorldEnvironment world){
  var root=new GameObject("Frost ascent and white pass");root.transform.SetParent(collision.transform,false);var p=root.transform;
  for(float d=236;d<383;d+=10.5f)foreach(float side in new[]{-1f,1f}){
   float offset=side*R(12,22),x=WorldLayout.Center(d)+offset;var pos=new Vector3(x,WorldLayout.Height(x,d)-1.1f,-d);var scale=new Vector3(R(1.3f,2.1f),R(.75f,1.5f),R(1.1f,1.7f));float yaw=R(0,360);bool snow=d>263&&(d>289||side>0);
   Model(p,"CW_HF_Limestone_LOD1",pos,scale,yaw,true,true);if(snow)Model(p,"SnowCover/CW_HF_Limestone_SnowCover_LOD1",pos,scale,yaw);
  }
  for(float d=242;d<375;d+=7.3f)foreach(float side in new[]{-1f,1f}){
   if(d>353&&side<0)continue;float off=side*R(8.5f,15),x=WorldLayout.Center(d)+off;float scale=R(.85f,1.3f);var pos=new Vector3(x,WorldLayout.Height(x,d)-.05f,-d);float yaw=R(0,360);
   var tree=Model(p,"FoliageFir/CW_CardedAlpineFir_LOD1",pos,Vector3.one*scale,yaw);tree.layer=29;var trunk=tree.AddComponent<CapsuleCollider>();trunk.center=Vector3.up*1.8f;trunk.height=3.6f;trunk.radius=.24f;
   if(d>278)Model(p,"SnowCover/CW_CardedAlpineFir_SnowCover_LOD1",pos,Vector3.one*scale,yaw);
  }
  foreach(float d in new[]{253f,270f,286f,307f,328f,349f,370f})foreach(float side in new[]{-1f,1f}){
   float x=WorldLayout.Center(d)+side*R(7.5f,10.5f);var pos=new Vector3(x,WorldLayout.Height(x,d)-.35f,-d);var scale=new Vector3(.85f,.65f,1.1f);float yaw=R(0,360);Model(p,"CW_LayeredRock_A",pos,scale,yaw,true);if(d>278)Model(p,"SnowCover/CW_LayeredRock_A_SnowCover_LOD1",pos,scale,yaw);
  }
  // A pair of settled fractured shoulders frames the view without closing the return path.
  foreach(float side in new[]{-1f,1f}){float x=WorldLayout.Center(375)+side*10;var pos=new Vector3(x,WorldLayout.Height(x,377)-2,-377);var scale=new Vector3(2.4f,1.25f,1.8f);float yaw=side<0?30:210;Model(p,"CW_HF_Limestone",pos,scale,yaw,true,true);Model(p,"SnowCover/CW_HF_Limestone_SnowCover",pos,scale,yaw);}
  // Distant shoulders remain geometry in the same scene, with no trigger-based activation.
  foreach(var q in new[]{new Vector3(-55,424,6),new Vector3(31,435,8),new Vector3(65,411,5)}){var pos=new Vector3(q.x,WorldLayout.Height(q.x,q.y)-8,-q.y);var scale=new Vector3(q.z,q.z*1.2f,q.z);Model(p,"CW_HF_Limestone_LOD1",pos,scale,25,false,true);Model(p,"SnowCover/CW_HF_Limestone_SnowCover_LOD1",pos,scale,25);}
  world.snow=Precipitation(p,"Snow flurries",1);var noise=world.snow.noise;noise.enabled=true;noise.strength=.45f;noise.frequency=.22f;noise.scrollSpeed=.18f;noise.quality=ParticleSystemNoiseQuality.Low;
  var render=world.snow.GetComponent<ParticleSystemRenderer>();render.sharedMaterial.SetColor("_BaseColor",new Color(.85f,.92f,1,.9f));
  Physics.SyncTransforms();var unsafeRocks=new HashSet<GameObject>();for(float d=235;d<=380;d+=.5f)foreach(float off in new[]{-2.2f,0,2.2f}){var pos=WorldLayout.Point(d,off);foreach(var hit in Physics.OverlapCapsule(pos+Vector3.up*.4f,pos+Vector3.up*1.4f,.25f,WorldMotor.BlockMask,QueryTriggerInteraction.Ignore)){var t=hit.transform;while(t.parent&&t.parent!=p)t=t.parent;if(t.parent==p&&t.name.Contains("Limestone"))unsafeRocks.Add(t.gameObject);}}
  foreach(var go in unsafeRocks){var pos=go.transform.position;foreach(var t in p.GetComponentsInChildren<Transform>())if(t.parent==p&&t.name.Contains("SnowCover")&&(t.position-pos).sqrMagnitude<.001f)Object.DestroyImmediate(t.gameObject);Debug.Log("WORLD SNOW CLEARANCE removed new rock from lane "+pos);Object.DestroyImmediate(go);}Physics.SyncTransforms();EditorUtility.SetDirty(world);
 }
}
}
