using System.Collections.Generic;
using UnityEngine;
using UnityEditor;
namespace Vesper.Expansion.ContinuousWorld.Editor {
public static partial class WorldVisuals {
 public static void SnowPass(GameObject collision,WorldEnvironment world){
  var root=new GameObject("Frost ascent and white pass");root.transform.SetParent(collision.transform,false);var p=root.transform;
  BuildSnowLayout(p);
  world.snow=Precipitation(p,"Snow flurries",1);var noise=world.snow.noise;noise.enabled=true;noise.strength=.45f;noise.frequency=.22f;noise.scrollSpeed=.18f;noise.quality=ParticleSystemNoiseQuality.Low;
  var render=world.snow.GetComponent<ParticleSystemRenderer>();render.sharedMaterial.SetColor("_BaseColor",new Color(.85f,.92f,1,.9f));
  Physics.SyncTransforms();var unsafeRocks=new HashSet<GameObject>();for(float d=235;d<=380;d+=.5f)foreach(float off in new[]{-2.2f,0,2.2f}){var pos=WorldLayout.Point(d,off);foreach(var hit in Physics.OverlapCapsule(pos+Vector3.up*.4f,pos+Vector3.up*1.4f,.25f,WorldMotor.BlockMask,QueryTriggerInteraction.Ignore)){var t=hit.transform;while(t.parent&&t.parent!=p)t=t.parent;if(t.parent==p&&t.name.Contains("Limestone"))unsafeRocks.Add(t.gameObject);}}
  foreach(var go in unsafeRocks){var pos=go.transform.position;foreach(var t in p.GetComponentsInChildren<Transform>())if(t.parent==p&&t.name.Contains("SnowCover")&&(t.position-pos).sqrMagnitude<.001f)Object.DestroyImmediate(t.gameObject);Debug.Log("WORLD SNOW CLEARANCE removed new rock from lane "+pos);Object.DestroyImmediate(go);}Physics.SyncTransforms();EditorUtility.SetDirty(world);
 }
}
}
