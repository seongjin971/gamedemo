using UnityEngine;
using UnityEngine.Rendering.Universal;
using Vesper.Expansion.WeatherW10;
namespace Vesper.Expansion.WeatherW10 {
// Scene-local addition. The delivered W06 environment and all previous scenes stay unchanged.
[DefaultExecutionOrder(50)]
public sealed class WeatherW07Flash:MonoBehaviour {
 public WorldEnvironment world;
 public float normalExtraExposure=1.10f,strongExtraExposure=1.20f;
 ColorAdjustments grade;
 void Start(){if(world&&world.volume)world.volume.profile.TryGet(out grade);}
 void LateUpdate(){
  // WorldEnvironment writes its original baseline every Update. Never accumulate exposure.
  if(grade&&world)grade.postExposure.value+=world.Flash*(world.StrongFlash?strongExtraExposure:normalExtraExposure);
 }
}
}
