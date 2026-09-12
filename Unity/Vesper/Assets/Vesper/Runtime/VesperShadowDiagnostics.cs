using System;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;

namespace Vesper {
public static class VesperShadowDiagnostics {
 public static void Apply(){
  var args=Environment.GetCommandLineArgs();
  if(Array.IndexOf(args,"-vesperUnpartitionedFireCasters")>=0){
   foreach(var renderer in UnityEngine.Object.FindObjectsByType<MeshRenderer>())if(renderer.name.StartsWith("Exact local fire shadow "))renderer.enabled=renderer.name.StartsWith("Exact local fire shadow combined ");
   Debug.Log("VESPER_DIAGNOSTIC_UNPARTITIONED_FIRE_CASTERS");
  }
  if(Array.IndexOf(args,"-vesperFullFireCasters")<0)return;
  foreach(var renderer in UnityEngine.Object.FindObjectsByType<MeshRenderer>()){
   if(renderer.name.StartsWith("Exact local fire shadow "))renderer.enabled=false;
   else renderer.renderingLayerMask=1;
  }
  foreach(var lamp in UnityEngine.Object.FindObjectsByType<Light>())if(lamp.name=="Brazier")lamp.GetUniversalAdditionalLightData().customShadowLayers=false;
  Debug.Log("VESPER_DIAGNOSTIC_FULL_FIRE_CASTERS");
 }
}
}
