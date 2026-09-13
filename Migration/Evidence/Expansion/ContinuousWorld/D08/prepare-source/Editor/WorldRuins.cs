using System.Collections.Generic;
using System.Linq;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEditor;
namespace Vesper.Expansion.ContinuousWorld.Editor {
public static partial class WorldVisuals {
 public static void Ruins(GameObject collision,WorldEnvironment world){
  var root=new GameObject("Rainwood and roofless abbey");root.transform.SetParent(collision.transform,false);var p=root.transform;
  var floor=WorldBuild.Box(p,"Abbey continuous walkable foundation",new Vector3(32,8.85f,-182),new Vector3(16,.3f,32),Mat("Foundation",new Color(.3f,.34f,.35f)),28);floor.GetComponent<Renderer>().enabled=false;
  for(float x=26;x<=38;x+=4)for(float d=168;d<=196;d+=4)Model(p,"ChapelSurfaces/CW_ChapelPaving4m",new Vector3(x,9,-d),Vector3.one,0);
  for(float d=166;d<=202;d+=4)foreach(float offset in new[]{-2f,2f}){var paving=Model(p,"ChapelSurfaces/CW_ChapelPaving4m",WorldLayout.Point(d,offset)+Vector3.up*.005f,Vector3.one,0);WarpPaving(paving,d,offset);}
  Model(p,"ChapelBroken/CW_ChapelBrokenWall6m",new Vector3(26.5f,9,-170),Vector3.one,0,true);
  foreach(float d in new[]{175f,194f})Model(p,"ChapelBroken/CW_ChapelBrokenWall6m",new Vector3(24,9,-d),Vector3.one,90,true);
  foreach(var q in new[]{new Vector2(24,178),new Vector2(24,191),new Vector2(29,170)})Model(p,"ChapelBroken/CW_ChapelBrokenPier3m",new Vector3(q.x,9,-q.y),Vector3.one,0,true);
  foreach(float x in new[]{24f,40f})foreach(float d in new[]{176f,182f,188f,194f}){if(x==24&&d!=188&&d!=194)continue;Model(p,"Chapel/CW_ChapelLancetWall",new Vector3(x,9,-d),Vector3.one,90,true);}
  Model(p,"Chapel/CW_ChapelEntranceArch",new Vector3(32,9,-170),Vector3.one,0,true);
  Model(p,"Chapel/CW_ChapelLancetWall",new Vector3(37.5f,9,-170),Vector3.one,0,true);
  foreach(float x in new[]{27f,37f})Model(p,"Chapel/CW_ChapelLancetWall",new Vector3(x,9,-198),Vector3.one,0,true);
  foreach(float d in new[]{173f,179f,185f,191f,197f})foreach(float x in new[]{23.4f,40.6f}){if(x<30&&d<191)continue;Model(p,"CW_HF_GothicButtress_LOD1",new Vector3(x,9,-d),new Vector3(.46f,1.4f,.46f),x<30?90:270,true,true);}
  foreach(float d in new[]{180f,190f})Model(p,"ChapelSurfaces/CW_ChapelRubblePile3m",new Vector3(24,9,-d),new Vector3(.8f,.65f,.6f),90,true);
  // Fractured wall-toe debris stays outside the main lane and the genuine entry gap at d181..184.
  foreach(float d in new[]{174f,190f,196f})Model(p,"AbbeyRubbleV2/CW_AbbeyRubbleStrip6m",new Vector3(23.7f,9,-d),Vector3.one,90,true);
  Model(p,"AbbeyRubbleV2/CW_AbbeyRubbleStrip6m",new Vector3(26.2f,9,-169.4f),Vector3.one,0,true);
  foreach(float d in new[]{178f,191f})Model(p,"AbbeyRubbleV2/CW_AbbeyRubbleStrip6m",new Vector3(40.6f,9,-d),Vector3.one,90,true);
  foreach(var q in new[]{new Vector2(26,171),new Vector2(25.4f,187),new Vector2(39,197)})Model(p,"AbbeyRubbleV2/CW_AbbeyRubbleMound3m",new Vector3(q.x,9,-q.y),new Vector3(.9f,.85f,.8f),35,true);
  // The higher broken belfry makes the abbey readable from the approach.
  foreach(float x in new[]{38.5f,44.5f})Model(p,"Chapel/CW_ChapelLancetWall",new Vector3(x,15.8f,-198),new Vector3(1,1.15f,1),0,true);
  Model(p,"Chapel/CW_ChapelLancetWall",new Vector3(44.5f,9,-195),Vector3.one,90,true);
  Model(p,"CW_HF_GothicButtress",new Vector3(44.5f,9,-198),new Vector3(.75f,2.95f,.75f),0,true,true);
  foreach(var q in new[]{new Vector2(29,199),new Vector2(35,199),new Vector2(43,175),new Vector2(27,190),new Vector2(42,204)})Model(p,"ChapelSurfaces/CW_ChapelRubblePile3m",new Vector3(q.x,WorldLayout.Height(q.x,q.y),-q.y),Vector3.one,R(0,360),true);
  var roof=Model(p,"ChapelSurfaces/CW_ChapelBrokenSlateRoof6x8m",new Vector3(37,16,-188),Vector3.one,0,true);
  foreach(float x in new[]{34f,40f})foreach(float d in new[]{184f,192f})Model(p,"CW_HF_GothicButtress_LOD1",new Vector3(x,9,-d),new Vector3(.45f,1.4f,.45f),0,true,true);
  foreach(var renderer in roof.GetComponentsInChildren<Renderer>())renderer.sharedMaterials=renderer.sharedMaterials.Select(m=>RoofMaterial(m)).ToArray();
  roof.AddComponent<WorldRoofCutaway>().world=world;
  world.shelter=new Bounds(new Vector3(37,12.35f,-187.6f),new Vector3(5.6f,7.1f,6.8f));
  for(float d=107;d<241;d+=7.5f)foreach(float side in new[]{-1f,1f}){
   float offset=side*R(9,18),x=WorldLayout.Center(d)+offset;if(x>21&&x<49&&d>157&&d<211)continue;
   string tree=d>205?"FoliageFir/CW_CardedAlpineFir_LOD1":"FoliageBirch/CW_CardedRiverBirch_LOD1";float scale=R(.9f,1.4f);var t=Model(p,tree,new Vector3(x,WorldLayout.Height(x,d)-.04f,-d),Vector3.one*scale,R(0,360));var trunk=t.AddComponent<CapsuleCollider>();t.layer=29;trunk.center=new Vector3(0,1.7f,0);trunk.height=3.4f;trunk.radius=.23f;
   if(d>148&&d<213)Grounded(p,"CW_LayeredRock_A",d,side*R(16,23),R(.8f,1.3f),true);
  }
  for(int i=0;i<135;i++){float d=R(107,232),off=(i%2==0?-1:1)*R(4.8f,18),x=WorldLayout.Center(d)+off;if(x>23&&x<43&&d>164&&d<201)continue;Grounded(p,"CW_RiverGrass",d,off,R(.35f,.65f));}
  Puddles(p,world);SetupWeather(world,p);Torch(p,new Vector3(38.9f,11.1f,-188));Torch(p,new Vector3(29.8f,11.4f,-169.3f));
 }
 static Material RoofMaterial(Material source){
  string key=source.name+"_Cutaway";if(materials.TryGetValue(key,out var old))return old;var m=new Material(source){name=key};m.SetFloat("_Surface",1);m.SetFloat("_Blend",0);m.SetFloat("_SrcBlend",(float)BlendMode.SrcAlpha);m.SetFloat("_DstBlend",(float)BlendMode.OneMinusSrcAlpha);m.SetFloat("_ZWrite",0);m.EnableKeyword("_SURFACE_TYPE_TRANSPARENT");m.renderQueue=3000;AssetDatabase.CreateAsset(m,output+"/"+key+".mat");materials[key]=m;return m;
 }
 static void WarpPaving(GameObject go,float d,float offset){int serial=0;foreach(var mf in go.GetComponentsInChildren<MeshFilter>()){var mesh=Object.Instantiate(mf.sharedMesh);var vertices=mesh.vertices;for(int i=0;i<vertices.Length;i++){var p=mf.transform.TransformPoint(vertices[i]);p.x+=WorldLayout.Center(-p.z)-WorldLayout.Center(d);vertices[i]=mf.transform.InverseTransformPoint(p);}mesh.vertices=vertices;mesh.RecalculateNormals();mesh.RecalculateBounds();AssetDatabase.CreateAsset(mesh,output+"/AbbeyRoad-"+d+"-"+offset+"-"+(serial++)+".asset");mf.sharedMesh=mesh;}}
 static void Puddles(Transform parent,WorldEnvironment world){
  var mat=new Material(Shader.Find("Vesper/WorldWetStone")){name="Abbey standing rainwater"};mat.SetTexture("_BaseMap",stoneTexture);mat.SetColor("_BaseColor",new Color(.57f,.62f,.64f));mat.SetFloat("_Wetness",1);mat.SetFloat("_ReflectionStrength",.5f);mat.SetFloat("_Overlay",1);mat.renderQueue=3000;AssetDatabase.CreateAsset(mat,output+"/AbbeyPuddles.mat");
  foreach(var q in new[]{new Vector3(30,1.7f,175),new Vector3(35,2,180),new Vector3(29,.9f,185),new Vector3(32,1.3f,193),new Vector3(26,.8f,171)}){
   var verts=new List<Vector3>{new Vector3(q.x,9.025f,-q.z)};var tris=new List<int>();for(int i=0;i<16;i++){float a=i*Mathf.PI/8,r=q.y*R(.75f,1.2f);verts.Add(new Vector3(q.x+Mathf.Cos(a)*r,9.025f,-q.z+Mathf.Sin(a)*r*.7f));}for(int i=0;i<16;i++){tris.Add(0);tris.Add((i+1)%16+1);tris.Add(i+1);}SoftPuddle(parent,"Irregular rain puddle",verts,mat);
  }
  foreach(float d in new[]{168f,174f,180f,188f,197f}){float x=WorldLayout.Center(d)+(d==180?-1.4f:.8f);var verts=new List<Vector3>{new Vector3(x,9.025f,-d)};var tris=new List<int>();for(int i=0;i<24;i++){float a=i*Mathf.PI/12,r=1.1f*(1+.18f*Mathf.Sin(i*2.7f+d));verts.Add(new Vector3(x+Mathf.Cos(a)*r,9.025f,-d+Mathf.Sin(a)*r*.65f));}for(int i=0;i<24;i++){tris.Add(0);tris.Add((i+1)%24+1);tris.Add(i+1);}SoftPuddle(parent,"Rain film on open road",verts,mat);}
  var reflection=new GameObject("Abbey puddle reflection").AddComponent<VesperPlanarReflection>();reflection.sourceCamera=Camera.main;reflection.planeHeight=9.025f;reflection.textureSize=512;reflection.renderShadows=true;reflection.renderSky=true;reflection.reflectedSkybox=RenderSettings.skybox;reflection.reflectionMask=~(1<<31);world.ruinsReflection=reflection;
 }
 static void SoftPuddle(Transform parent,string name,List<Vector3> outline,Material mat){
  int n=outline.Count-1;var verts=new List<Vector3>{outline[0]};var colors=new List<Color>{new Color(1,1,1,.8f)};var tris=new List<int>();
  for(int i=0;i<n;i++){verts.Add(Vector3.Lerp(outline[0],outline[i+1],.68f));colors.Add(new Color(1,1,1,.58f));}
  for(int i=0;i<n;i++){verts.Add(outline[i+1]);colors.Add(new Color(1,1,1,0));}
  for(int i=0;i<n;i++){int a=i+1,b=(i+1)%n+1;tris.AddRange(new[]{0,b,a,a,b,b+n,a,b+n,a+n});}
  var go=WorldBuild.MeshObject(parent,name,verts,tris,mat,31,false,colors.ToArray());go.GetComponent<Renderer>().shadowCastingMode=ShadowCastingMode.Off;
 }
 static ParticleSystem Precipitation(Transform parent,string name,int kind){
  var go=new GameObject(name);go.transform.SetParent(parent,false);var ps=go.AddComponent<ParticleSystem>();ps.Stop(true,ParticleSystemStopBehavior.StopEmittingAndClear);var main=ps.main;main.loop=true;main.playOnAwake=true;main.simulationSpace=ParticleSystemSimulationSpace.World;main.maxParticles=4096;main.startLifetime=kind==0?2.4f:kind==1?7:.4f;main.startSpeed=0;main.startSize=kind==0?.025f:kind==1?.075f:.2f;main.startColor=new Color(.83f,.89f,.95f,kind==0?.25f:.6f);main.cullingMode=ParticleSystemCullingMode.AlwaysSimulate;
  var shape=ps.shape;shape.shapeType=ParticleSystemShapeType.Box;shape.scale=new Vector3(32,2,32);shape.enabled=kind!=2;var emission=ps.emission;emission.rateOverTime=0;
  var velocity=ps.velocityOverLifetime;velocity.enabled=kind!=2;velocity.space=ParticleSystemSimulationSpace.World;velocity.x=kind==0?1.8f:1.2f;velocity.y=kind==0?-18:-2;velocity.z=.5f;
  var collision=ps.collision;collision.enabled=kind!=2;collision.type=ParticleSystemCollisionType.World;collision.mode=ParticleSystemCollisionMode.Collision3D;collision.collidesWith=WorldMotor.SurfaceMask|WorldMotor.BlockMask;collision.quality=ParticleSystemCollisionQuality.Medium;collision.enableDynamicColliders=false;collision.lifetimeLoss=1;collision.maxCollisionShapes=256;
  var renderer=ps.GetComponent<ParticleSystemRenderer>();renderer.renderMode=kind==0?ParticleSystemRenderMode.Stretch:kind==2?ParticleSystemRenderMode.HorizontalBillboard:ParticleSystemRenderMode.Billboard;renderer.velocityScale=kind==0?.035f:0;renderer.lengthScale=kind==0?3:1;renderer.shadowCastingMode=ShadowCastingMode.Off;renderer.receiveShadows=false;var mat=new Material(Shader.Find("Vesper/WorldPrecipitation")){name=name};mat.SetFloat("_Kind",kind);AssetDatabase.CreateAsset(mat,output+"/"+name+".mat");renderer.sharedMaterial=mat;
  if(kind==2){var size=ps.sizeOverLifetime;size.enabled=true;size.size=new ParticleSystem.MinMaxCurve(1,AnimationCurve.Linear(0,.3f,1,1.5f));var color=ps.colorOverLifetime;color.enabled=true;var gradient=new Gradient();gradient.SetKeys(new[]{new GradientColorKey(Color.white,0),new GradientColorKey(Color.white,1)},new[]{new GradientAlphaKey(.8f,0),new GradientAlphaKey(0,1)});color.color=gradient;}
  return ps;
 }
 static void SetupWeather(WorldEnvironment world,Transform parent){
  var weather=world.gameObject.AddComponent<WorldWeather>();weather.world=world;world.rain=Precipitation(parent,"Rain streaks",0);weather.splashes=Precipitation(parent,"Rain ground rings",2);
  world.rain.GetComponent<ParticleSystemRenderer>().sharedMaterial.SetColor("_BaseColor",new Color(.73f,.82f,.91f,.58f));weather.splashes.GetComponent<ParticleSystemRenderer>().sharedMaterial.SetColor("_BaseColor",new Color(.76f,.85f,.93f,.65f));
  world.waterAudio=Ambience(parent,"River",new Vector3(WorldLayout.Center(48.5f),0,-48.5f),.9f);world.rainAudio=Ambience(parent,"Rain",Vector3.zero,0);world.windAudio=Ambience(parent,"PassWind",Vector3.zero,0);
  if(!Camera.main.GetComponent<AudioListener>())Camera.main.gameObject.AddComponent<AudioListener>();
 }
 static AudioSource Ambience(Transform parent,string name,Vector3 pos,float spatial){var go=new GameObject(name+" ambience");go.transform.SetParent(parent,false);go.transform.position=pos;var a=go.AddComponent<AudioSource>();a.clip=AssetDatabase.LoadAssetAtPath<AudioClip>(Art+"/Audio/"+name+".wav");a.loop=true;a.playOnAwake=true;a.spatialBlend=spatial;a.minDistance=10;a.maxDistance=75;a.rolloffMode=AudioRolloffMode.Linear;a.volume=.2f;return a;}
 static void Torch(Transform parent,Vector3 pos){
  var bracket=WorldBuild.Box(parent,"Abbey lamp ironwork",pos-Vector3.up*.3f,new Vector3(.12f,.7f,.12f),Mat("LampIron",new Color(.12f,.13f,.14f),.6f));bracket.GetComponent<Collider>().enabled=false;
  var flame=GameObject.CreatePrimitive(PrimitiveType.Quad);flame.name="Warm sheltered flame";flame.transform.SetParent(parent,false);flame.transform.position=pos;flame.transform.localScale=new Vector3(.35f,.65f,1);Object.DestroyImmediate(flame.GetComponent<Collider>());var mat=Mat("AbbeyFlame",new Color(1,.55f,.15f));mat.shader=Shader.Find("Vesper/AtmosphereFlame");mat.SetTexture("_BaseMap",AssetDatabase.LoadAssetAtPath<Texture2D>("Assets/Vesper/AtmosphereV2/Textures/FlameV17.png"));mat.SetColor("_BaseColor",new Color(3,1.35f,.3f,1));flame.GetComponent<Renderer>().sharedMaterial=mat;var light=flame.AddComponent<Light>();light.type=LightType.Point;light.color=new Color(1,.55f,.22f);light.intensity=3;light.range=6;light.shadows=LightShadows.None;
 }
}
}
