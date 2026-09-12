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
 public ParticleSystem rain,snow,spindrift,nearSnow,leaves,blizzardMist;
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
  Flash=FlashOverride>=0?FlashOverride:Mathf.Clamp01(Pulse(t,.10f,.09f)+.72f*Pulse(t,.34f,.10f)+.16f*Pulse(t,.57f,.17f))*WorldLayout.S(0,.65f,rainWeight);
  StrongFlash=FlashOverride>=0?StrongOverride:strong;
  Color sunColor=Color.Lerp(new Color(1,.93f,.77f),new Color(.72f,.80f,.89f),dark);
  sunColor=Color.Lerp(sunColor,new Color(.53f,.68f,.91f),night);
  float nightScale=Mathf.Lerp(1,.66f,night);
  Shader.SetGlobalVector("_WeatherFlashState",new Vector4(Flash,StrongFlash?1:0,Progress,night));
  // Thunder has no directional light source: the whole view flashes together.
  if(sun){sun.color=sunColor;sun.intensity=Mathf.Lerp(1.65f,.72f,dark)*Mathf.Lerp(1,.30f,night);sun.shadowStrength=Mathf.Lerp(.9f,.65f,dark)*Mathf.Lerp(1,.45f,night);}
  RenderSettings.ambientSkyColor=Color.Lerp(Color.Lerp(new Color(.55f,.65f,.75f),new Color(.38f,.47f,.55f),dark),new Color(.33f,.43f,.58f),night);
  RenderSettings.ambientEquatorColor=Color.Lerp(Color.Lerp(new Color(.37f,.43f,.38f),new Color(.25f,.31f,.35f),dark),new Color(.24f,.31f,.42f),night);
  RenderSettings.ambientGroundColor=Color.Lerp(Color.Lerp(new Color(.20f,.23f,.16f),new Color(.16f,.20f,.21f),dark),new Color(.15f,.20f,.27f),night);
  RenderSettings.ambientSkyColor*=nightScale;RenderSettings.ambientEquatorColor*=nightScale;RenderSettings.ambientGroundColor*=nightScale;
  RenderSettings.fog=true;RenderSettings.fogMode=FogMode.ExponentialSquared;
  var fog=Color.Lerp(Color.Lerp(new Color(.63f,.73f,.74f),new Color(.40f,.49f,.55f),dark),new Color(.16f,.23f,.33f),night);
  RenderSettings.fogColor=fog;
  RenderSettings.fogDensity=Mathf.Lerp(.0055f,.012f,dark)+night*.003f;
  if(skyMaterial&&skyMaterial.HasProperty("_SkyTint"))skyMaterial.SetColor("_SkyTint",RenderSettings.fogColor);
  if(grade){grade.postExposure.value=Mathf.Lerp(.30f,.15f,dark)-night+Flash*(StrongFlash?2.15f:1.65f);grade.saturation.value=-5-16*dark*(1-rainWeight)*(1-night);}
  Sheltered=shelter.Contains(player.transform.position+Vector3.up);
  if(reflection)reflection.enabled=Progress<50;
  if(ruinsReflection)ruinsReflection.enabled=Progress>158&&Progress<233;
  WeatherAt(rain,player.transform.position+Vector3.up*13,1700*rainWeight);
  float gust=.76f+.24f*Mathf.Sin(now*.61f+Mathf.Sin(now*.17f));
  WeatherAt(snow,player.transform.position+new Vector3(-8,11,0),5000*night*gust);
  WeatherAt(nearSnow,player.transform.position+new Vector3(-9,12,1),1200*night*gust);
  WeatherAt(spindrift,player.transform.position+new Vector3(-10,.9f,0),26*night*gust);
  WeatherAt(leaves,player.transform.position+new Vector3(-3,4,0),12*dark*(1-rainWeight)*(1-night));
  WeatherAt(blizzardMist,player.transform.position+new Vector3(-8,3,0),14*night*gust);
 }
 static void WeatherAt(ParticleSystem ps,Vector3 p,float rate){if(!ps)return;ps.transform.position=p;var emission=ps.emission;emission.rateOverTime=rate;}
 void OnGUI(){
  // Low-opacity uniform fill also lights dark silhouettes without a spatial hotspot.
  if(Flash>.0001f&&Event.current.type==EventType.Repaint){var old=GUI.color;GUI.color=new Color(.82f,.90f,1,Flash*(StrongFlash?.20f:.13f));GUI.DrawTexture(new Rect(0,0,Screen.width,Screen.height),Texture2D.whiteTexture);GUI.color=old;}
  if(titleStyle==null){titleStyle=new GUIStyle(GUI.skin.label){fontSize=15};helpStyle=new GUIStyle(GUI.skin.label){fontSize=13};}
  string title="V E S P E R   /   "+WorldLayout.Region(Progress),help="Click to travel    |    Drag to orbit    |    Wheel to zoom    |    Shift to run    |    R to return";
  titleStyle.normal.textColor=new Color(.03f,.05f,.06f,.85f);helpStyle.normal.textColor=titleStyle.normal.textColor;GUI.Label(new Rect(29,21,700,28),title,titleStyle);GUI.Label(new Rect(29,Screen.height-33,1200,24),help,helpStyle);
  titleStyle.normal.textColor=new Color(.92f,.95f,.90f,.95f);helpStyle.normal.textColor=new Color(.92f,.95f,.9f,.88f);GUI.Label(new Rect(28,20,700,28),title,titleStyle);GUI.Label(new Rect(28,Screen.height-34,1200,24),help,helpStyle);
 }
}
}
