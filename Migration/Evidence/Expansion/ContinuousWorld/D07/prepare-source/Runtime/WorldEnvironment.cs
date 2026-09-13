using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;
namespace Vesper.Expansion.ContinuousWorld {
[DefaultExecutionOrder(-20)]
public sealed class WorldEnvironment:MonoBehaviour {
 public WorldMotor player; public Light sun; public Material skyMaterial; public Volume volume;
 public Vector3 Weights{get;private set;} public float Progress=>player?-player.transform.position.z:0;
 public bool Sheltered{get;private set;}
 public Bounds shelter=new Bounds(new Vector3(12,12,-182),new Vector3(7,6,8));
 public ParticleSystem rain,snow; public AudioSource waterAudio,rainAudio,windAudio;public VesperPlanarReflection reflection,ruinsReflection;
 ColorAdjustments grade;
 GUIStyle titleStyle,helpStyle;
 void Awake(){Application.runInBackground=true;if(volume&&volume.profile)volume.profile.TryGet(out grade);}
 void Update(){
  Weights=WorldLayout.Weights(Progress);float a=Weights.x,b=Weights.y,c=Weights.z;
  if(sun){sun.color=new Color(1,.93f,.77f)*a+new Color(.72f,.80f,.89f)*b+new Color(.80f,.87f,1)*c;sun.intensity=1.65f*a+.85f*b+1.05f*c;}
  if(sun)sun.shadowStrength=.9f*a+.65f*b+.75f*c;
  RenderSettings.ambientSkyColor=new Color(.55f,.65f,.75f)*a+new Color(.38f,.47f,.55f)*b+new Color(.57f,.67f,.79f)*c;
  RenderSettings.ambientEquatorColor=new Color(.37f,.43f,.38f)*a+new Color(.25f,.31f,.35f)*b+new Color(.42f,.48f,.58f)*c;
  RenderSettings.ambientGroundColor=new Color(.20f,.23f,.16f)*a+new Color(.16f,.20f,.21f)*b+new Color(.30f,.35f,.42f)*c;
  RenderSettings.fog=true;RenderSettings.fogMode=FogMode.ExponentialSquared;
  RenderSettings.fogColor=new Color(.63f,.73f,.74f)*a+new Color(.40f,.49f,.55f)*b+new Color(.66f,.74f,.81f)*c;
  RenderSettings.fogDensity=.0055f*a+.012f*b+.010f*c;
  if(skyMaterial&&skyMaterial.HasProperty("_Tint"))skyMaterial.SetColor("_Tint",RenderSettings.fogColor);
  if(skyMaterial&&skyMaterial.HasProperty("_SkyTint"))skyMaterial.SetColor("_SkyTint",RenderSettings.fogColor);
  if(grade)grade.postExposure.value=.30f*a+.15f*b+.05f*c;
  Sheltered=player&&shelter.Contains(player.transform.position+Vector3.up);
  if(reflection)reflection.enabled=Progress<103;
  if(ruinsReflection)ruinsReflection.enabled=Progress>135&&Progress<225;
  if(rain){rain.transform.position=player.transform.position+Vector3.up*13;var emission=rain.emission;emission.rateOverTime=1700*b;}
  if(snow){snow.transform.position=player.transform.position+Vector3.up*11;var emission=snow.emission;emission.rateOverTime=220*c;}
  if(waterAudio)waterAudio.volume=.35f*a;if(rainAudio)rainAudio.volume=.40f*b*(Sheltered?.4f:1);if(windAudio)windAudio.volume=.12f+.25f*c;
 }
 void OnGUI(){
  if(titleStyle==null){titleStyle=new GUIStyle(GUI.skin.label){fontSize=15};helpStyle=new GUIStyle(GUI.skin.label){fontSize=13};}
  var old=GUI.color;GUI.color=Color.white;string title="V E S P E R   /   "+WorldLayout.Region(Progress);string help="Click to travel    |    Drag to orbit    |    Wheel to zoom    |    Shift to run    |    R to return";
  titleStyle.normal.textColor=new Color(.03f,.05f,.06f,.85f);helpStyle.normal.textColor=titleStyle.normal.textColor;GUI.Label(new Rect(29,21,600,28),title,titleStyle);GUI.Label(new Rect(29,Screen.height-33,1200,24),help,helpStyle);
  titleStyle.normal.textColor=new Color(.92f,.95f,.90f,.95f);helpStyle.normal.textColor=new Color(.92f,.95f,.9f,.88f);GUI.Label(new Rect(28,20,600,28),title,titleStyle);GUI.Label(new Rect(28,Screen.height-34,1200,24),help,helpStyle);GUI.color=old;
 }
}
}
