using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;
namespace Vesper.Expansion.WeatherWorld {
[DefaultExecutionOrder(-20)]
public sealed class WorldEnvironment:MonoBehaviour {
 public WorldMotor player; public Light sun; public Material skyMaterial; public Volume volume;
 public Vector3 Weights{get;private set;} public float Progress=>player?-player.transform.position.z:0;
 public bool Sheltered{get;private set;}
 public Bounds shelter;
 public ParticleSystem rain,snow,spindrift,nearSnow;
 public AudioSource waterAudio,rainAudio,windAudio;
 public VesperPlanarReflection reflection,ruinsReflection;
 public float FlashOverride=-1; public bool StrongOverride;
 public float Flash{get;private set;} public bool StrongFlash{get;private set;}
 public int FlashEvents{get;private set;} public int StrongEvents{get;private set;}
 ColorAdjustments grade;GUIStyle titleStyle,helpStyle;
 float nextFlash=6,flashStart=-100;bool strong;System.Random storm=new System.Random(76119);
 void Awake(){Application.runInBackground=true;if(volume&&volume.profile)volume.profile.TryGet(out grade);}
 static float Pulse(float t,float onset,float width)=>Mathf.Exp(-Mathf.Pow((t-onset)/width,2));
 public void PreviewFlash(bool strongEvent){flashStart=Time.time;strong=strongEvent;nextFlash=Time.time+25;}
 void Update(){
  if(!player)return;
  Weights=WorldLayout.Weights(Progress);float dark=WorldLayout.Darkness(Progress),night=Weights.z,rainWeight=Weights.y;
  float now=Time.time;
  if(FlashOverride<0&&rainWeight>.35f&&now>nextFlash){flashStart=now;strong=FlashEvents%5==4;FlashEvents++;if(strong)StrongEvents++;nextFlash=now+8+(float)storm.NextDouble()*9;}
  float t=now-flashStart;
  Flash=FlashOverride>=0?FlashOverride:Mathf.Clamp01(Pulse(t,.10f,.07f)+.58f*Pulse(t,.31f,.10f)+.23f*Pulse(t,.55f,.21f))*WorldLayout.S(0,.65f,rainWeight);
  StrongFlash=FlashOverride>=0?StrongOverride:strong;
  float distant=StrongFlash?0:Flash,broad=StrongFlash?Flash:0;
  Color sunColor=Color.Lerp(new Color(1,.93f,.77f),new Color(.72f,.80f,.89f),dark);
  sunColor=Color.Lerp(sunColor,new Color(.53f,.68f,.91f),night);
  if(sun){sun.color=Color.Lerp(sunColor,new Color(.72f,.84f,1),Flash*.55f);sun.intensity=Mathf.Lerp(1.65f,.72f,dark)+distant*.24f+broad*1.15f;sun.shadowStrength=Mathf.Lerp(.9f,.65f,dark);}
  RenderSettings.ambientSkyColor=Color.Lerp(Color.Lerp(new Color(.55f,.65f,.75f),new Color(.38f,.47f,.55f),dark),new Color(.33f,.43f,.58f),night)+new Color(.13f,.18f,.26f)*(distant*.36f+broad);
  RenderSettings.ambientEquatorColor=Color.Lerp(Color.Lerp(new Color(.37f,.43f,.38f),new Color(.25f,.31f,.35f),dark),new Color(.24f,.31f,.42f),night)+new Color(.09f,.14f,.21f)*(distant*.18f+broad);
  RenderSettings.ambientGroundColor=Color.Lerp(Color.Lerp(new Color(.20f,.23f,.16f),new Color(.16f,.20f,.21f),dark),new Color(.15f,.20f,.27f),night);
  RenderSettings.fog=true;RenderSettings.fogMode=FogMode.ExponentialSquared;
  var fog=Color.Lerp(Color.Lerp(new Color(.63f,.73f,.74f),new Color(.40f,.49f,.55f),dark),new Color(.28f,.38f,.52f),night);
  RenderSettings.fogColor=fog+new Color(.30f,.38f,.50f)*(distant+broad*.8f);
  RenderSettings.fogDensity=Mathf.Lerp(.0055f,.012f,dark)+night*.003f;
  if(skyMaterial&&skyMaterial.HasProperty("_SkyTint"))skyMaterial.SetColor("_SkyTint",RenderSettings.fogColor);
  if(grade)grade.postExposure.value=Mathf.Lerp(.30f,.15f,dark);
  Sheltered=shelter.Contains(player.transform.position+Vector3.up);
  if(reflection)reflection.enabled=Progress<WorldLayout.FromSource(65);
  if(ruinsReflection)ruinsReflection.enabled=Progress>158&&Progress<233;
  WeatherAt(rain,player.transform.position+Vector3.up*13,1700*rainWeight);
  float gust=.76f+.24f*Mathf.Sin(now*.61f+Mathf.Sin(now*.17f));
  WeatherAt(snow,player.transform.position+new Vector3(-11,11,0),650*night*gust);
  WeatherAt(nearSnow,player.transform.position+new Vector3(-12,7,1),95*night*gust);
  WeatherAt(spindrift,player.transform.position+new Vector3(-10,.9f,0),9*night*gust);
 }
 static void WeatherAt(ParticleSystem ps,Vector3 p,float rate){if(!ps)return;ps.transform.position=p;var emission=ps.emission;emission.rateOverTime=rate;}
 void OnGUI(){
  if(titleStyle==null){titleStyle=new GUIStyle(GUI.skin.label){fontSize=15};helpStyle=new GUIStyle(GUI.skin.label){fontSize=13};}
  string title="V E S P E R   /   "+WorldLayout.Region(Progress),help="Click to travel    |    Drag to orbit    |    Wheel to zoom    |    Shift to run    |    R to return";
  titleStyle.normal.textColor=new Color(.03f,.05f,.06f,.85f);helpStyle.normal.textColor=titleStyle.normal.textColor;GUI.Label(new Rect(29,21,700,28),title,titleStyle);GUI.Label(new Rect(29,Screen.height-33,1200,24),help,helpStyle);
  titleStyle.normal.textColor=new Color(.92f,.95f,.90f,.95f);helpStyle.normal.textColor=new Color(.92f,.95f,.9f,.88f);GUI.Label(new Rect(28,20,700,28),title,titleStyle);GUI.Label(new Rect(28,Screen.height-34,1200,24),help,helpStyle);
 }
}
}
