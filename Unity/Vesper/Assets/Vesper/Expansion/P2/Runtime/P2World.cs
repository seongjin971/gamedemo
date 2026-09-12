using System.Collections;
using UnityEngine;
namespace Vesper.Expansion.P2 {
[DefaultExecutionOrder(-80)]
public sealed class P2World:MonoBehaviour {
 public static P2World Instance{get;private set;}
 public GameObject courtyard,connection; public P2Motor player;public P2Camera cameraControl;
 public Vector3 courtyardSpawn=new Vector3(-2.25f,0,7.5f),returnSpawn=new Vector3(-5,0,8.7f),connectionSpawn=new Vector3(0,0,9);
 public Vector3 courtyardGate=new Vector3(-5,0,10.3f),connectionGate=new Vector3(0,0,10.8f);
 public bool Busy{get;private set;} public int Zone{get;private set;}public int Transitions{get;private set;}
 float fade,gateCooldown;Color fog,ambient;float fogDensity; Material sky;
 void Awake(){Instance=this;fog=RenderSettings.fogColor;fogDensity=RenderSettings.fogDensity;ambient=RenderSettings.ambientLight;sky=RenderSettings.skybox;connection.SetActive(false);courtyard.SetActive(true);player.home=courtyardSpawn;}
 IEnumerator Start(){cameraControl.Enter(courtyardSpawn,false);gateCooldown=Time.time+1;yield return null;foreach(var a in player.GetComponentsInChildren<Vesper.Expansion.AdventurerAmbient>())a.Apply();}
 void Update(){if(!Busy && Time.time>gateCooldown && Vector3.Distance(player.transform.position,Zone==0?courtyardGate:connectionGate)<.65f)StartCoroutine(Switch());}
 IEnumerator Switch(){
  Busy=true;for(float t=0;t<.22f;t+=Time.unscaledDeltaTime){fade=t/.22f;yield return null;}fade=1;
  (Zone==0?courtyard:connection).SetActive(false);
  // Reflection OnDisable destroys its camera/texture and clears global availability.
  yield return null;
  Zone=1-Zone;(Zone==0?courtyard:connection).SetActive(true);
  RenderSettings.skybox=sky;RenderSettings.fogColor=Zone==0?fog:new Color(.045f,.062f,.084f);RenderSettings.fogDensity=Zone==0?fogDensity:.013f;RenderSettings.ambientLight=ambient;
  player.home=Zone==0?returnSpawn:connectionSpawn;player.ResetPosition();
  Busy=false;cameraControl.Enter(player.home,Zone==1);Busy=true;
  foreach(var a in player.GetComponentsInChildren<Vesper.Expansion.AdventurerAmbient>())a.Apply();
  Physics.SyncTransforms();Transitions++;gateCooldown=Time.time+1;
  for(float t=0;t<.22f;t+=Time.unscaledDeltaTime){fade=1-t/.22f;yield return null;}fade=0;Busy=false;
 }
 void OnGUI(){
  var old=GUI.color;
  GUI.color=new Color(.8f,.88f,.9f,.9f);
  GUI.Label(new Rect(22,18,720,28),Zone==0?"VESPER  /  COURTYARD   •   Follow the amber arch to the crossing":"VESPER  /  THE CROSSING   •   Ramp, bridge and upper landing");
  GUI.Label(new Rect(22,Screen.height-36,900,24),"Click to move    Hold SHIFT to run    Drag to orbit    Wheel to zoom    R to reset this entrance");
  if(fade>0){GUI.color=new Color(0,0,0,fade);GUI.DrawTexture(new Rect(0,0,Screen.width,Screen.height),Texture2D.whiteTexture);}GUI.color=old;
 }
 void OnDestroy(){if(Instance==this)Instance=null;}
}
}
