using System;
using System.Collections;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;

// Opt-in same-player A/B. This never writes renderer data or project settings.
public sealed class VesperDepthPrimingDiagnostic : MonoBehaviour {
 static UniversalRenderer appliedRenderer;
 static DepthPrimingMode requested;
 static string Option(){var args=Environment.GetCommandLineArgs();int index=Array.IndexOf(args,"-vesperDepthPriming");return index>=0&&index+1<args.Length?args[index+1]:"";}
 public static string Status(){var asset=GraphicsSettings.currentRenderPipeline as UniversalRenderPipelineAsset;return asset&&asset.GetRenderer(0) is UniversalRenderer renderer?renderer.depthPrimingMode.ToString():"Unavailable";}
 public static void Apply(){
  string option=Option();if(option.Length==0)return;
  if(option!="on"&&option!="off")throw new ArgumentException("Expected -vesperDepthPriming on or off");
  var asset=GraphicsSettings.currentRenderPipeline as UniversalRenderPipelineAsset;
  if(!asset||!(asset.GetRenderer(0) is UniversalRenderer main)||!(asset.GetRenderer(1) is UniversalRenderer reflection))throw new InvalidOperationException("Expected separate main and reflection universal renderers");
  if(reflection.depthPrimingMode!=DepthPrimingMode.Disabled)throw new InvalidOperationException("Reflection priming must remain disabled for comparison");
  requested=option=="on"?DepthPrimingMode.Forced:DepthPrimingMode.Disabled;
  main.depthPrimingMode=requested;appliedRenderer=main;
  Debug.Log("VESPER_DEPTH_PRIMING_APPLIED main="+main.depthPrimingMode+" reflection="+reflection.depthPrimingMode);
 }
 [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.AfterSceneLoad)]static void Initialize(){
  if(Option().Length==0)return;Apply();new GameObject("Depth priming QA observer").AddComponent<VesperDepthPrimingDiagnostic>();
 }
 IEnumerator Start(){
  yield return new WaitForSeconds(2);
  var asset=(UniversalRenderPipelineAsset)GraphicsSettings.currentRenderPipeline;
  if(!ReferenceEquals(appliedRenderer,asset.GetRenderer(0))||appliedRenderer.depthPrimingMode!=requested)Debug.LogError("Depth priming renderer changed during warmup");
  else Debug.Log("VESPER_DEPTH_PRIMING_WARMUP_VERIFIED "+requested);
  Destroy(gameObject);
 }
}
