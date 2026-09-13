using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEditor;
namespace Vesper.Expansion.LinearWorld.Editor {
public static partial class WorldVisuals {
 static ParticleSystem Precipitation(Transform parent,string name,int kind){
  var go=new GameObject(name);go.transform.SetParent(parent,false);var ps=go.AddComponent<ParticleSystem>();ps.Stop(true,ParticleSystemStopBehavior.StopEmittingAndClear);var main=ps.main;main.loop=true;main.playOnAwake=true;main.simulationSpace=ParticleSystemSimulationSpace.World;main.maxParticles=4096;main.startLifetime=kind==0?2.4f:kind==1?7:.4f;main.startSpeed=0;main.startSize=kind==0?.025f:kind==1?.075f:.2f;main.startColor=new Color(.83f,.89f,.95f,kind==0?.25f:.6f);main.cullingMode=ParticleSystemCullingMode.AlwaysSimulate;
  var shape=ps.shape;shape.shapeType=ParticleSystemShapeType.Box;shape.scale=new Vector3(32,2,32);shape.enabled=kind!=2;var emission=ps.emission;emission.rateOverTime=0;
  var velocity=ps.velocityOverLifetime;velocity.enabled=kind!=2;velocity.space=ParticleSystemSimulationSpace.World;velocity.x=kind==0?1.8f:1.2f;velocity.y=kind==0?-18:-2;velocity.z=.5f;
  var collision=ps.collision;collision.enabled=kind!=2;collision.type=ParticleSystemCollisionType.World;collision.mode=ParticleSystemCollisionMode.Collision3D;collision.collidesWith=WorldMotor.SurfaceMask|WorldMotor.BlockMask;collision.quality=ParticleSystemCollisionQuality.Medium;collision.enableDynamicColliders=false;collision.lifetimeLoss=1;collision.maxCollisionShapes=256;
  var renderer=ps.GetComponent<ParticleSystemRenderer>();renderer.renderMode=kind==0?ParticleSystemRenderMode.Stretch:kind==2?ParticleSystemRenderMode.HorizontalBillboard:ParticleSystemRenderMode.Billboard;renderer.velocityScale=kind==0?.035f:0;renderer.lengthScale=kind==0?3:1;renderer.shadowCastingMode=ShadowCastingMode.Off;renderer.receiveShadows=false;var mat=new Material(Shader.Find("Vesper/Linear/Precipitation")){name=name};mat.SetFloat("_Kind",kind);AssetDatabase.CreateAsset(mat,output+"/"+name+".mat");renderer.sharedMaterial=mat;
  if(kind==2){var size=ps.sizeOverLifetime;size.enabled=true;size.size=new ParticleSystem.MinMaxCurve(1,AnimationCurve.Linear(0,.3f,1,1.5f));var color=ps.colorOverLifetime;color.enabled=true;var gradient=new Gradient();gradient.SetKeys(new[]{new GradientColorKey(Color.white,0),new GradientColorKey(Color.white,1)},new[]{new GradientAlphaKey(.8f,0),new GradientAlphaKey(0,1)});color.color=gradient;}
  return ps;
 }
 static void SetupWeather(WorldEnvironment world,Transform parent){
  var weather=world.gameObject.AddComponent<WorldWeather>();weather.world=world;world.rain=Precipitation(parent,"Rain streaks",0);weather.splashes=Precipitation(parent,"Rain ground rings",2);
  world.rain.GetComponent<ParticleSystemRenderer>().sharedMaterial.SetColor("_BaseColor",new Color(.73f,.82f,.91f,.58f));weather.splashes.GetComponent<ParticleSystemRenderer>().sharedMaterial.SetColor("_BaseColor",new Color(.76f,.85f,.93f,.9f));
  world.waterAudio=Ambience(parent,"River",new Vector3(WorldLayout.Center(25),0,-25),.9f);world.rainAudio=Ambience(parent,"Rain",Vector3.zero,0);world.windAudio=Ambience(parent,"PassWind",Vector3.zero,0);
  if(!Camera.main.GetComponent<AudioListener>())Camera.main.gameObject.AddComponent<AudioListener>();
 }
 static AudioSource Ambience(Transform parent,string name,Vector3 pos,float spatial){var go=new GameObject(name+" ambience");go.transform.SetParent(parent,false);go.transform.position=pos;var a=go.AddComponent<AudioSource>();a.clip=AssetDatabase.LoadAssetAtPath<AudioClip>(Art+"/Audio/"+name+".wav");a.loop=true;a.playOnAwake=true;a.spatialBlend=spatial;a.minDistance=10;a.maxDistance=75;a.rolloffMode=AudioRolloffMode.Linear;a.volume=.2f;return a;}
 static void Torch(Transform parent,Vector3 pos){
  var bracket=LinearBuild.Box(parent,"Abbey lamp ironwork",pos-Vector3.up*.3f,new Vector3(.12f,.7f,.12f),Mat("LampIron",new Color(.12f,.13f,.14f),.6f));bracket.GetComponent<Collider>().enabled=false;
  var flame=GameObject.CreatePrimitive(PrimitiveType.Quad);flame.name="Warm sheltered flame";flame.transform.SetParent(parent,false);flame.transform.position=pos;flame.transform.localScale=new Vector3(.35f,.65f,1);Object.DestroyImmediate(flame.GetComponent<Collider>());var mat=Mat("AbbeyFlame",new Color(1,.55f,.15f));mat.shader=Shader.Find("Vesper/AtmosphereFlame");mat.SetTexture("_BaseMap",AssetDatabase.LoadAssetAtPath<Texture2D>("Assets/Vesper/AtmosphereV2/Textures/FlameV17.png"));mat.SetColor("_BaseColor",new Color(3,1.35f,.3f,1));flame.GetComponent<Renderer>().sharedMaterial=mat;var light=flame.AddComponent<Light>();light.type=LightType.Point;light.color=new Color(1,.55f,.22f);light.intensity=3;light.range=6;light.shadows=LightShadows.None;
 }
}
}
