using System;
using System.Collections.Generic;
using System.Linq;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;
using UnityEditor;
namespace Vesper.Expansion.LinearWorld.Editor {
public static partial class WorldVisuals {
 static int stoneSerial;
 static float S(float a,float b,float v)=>Mathf.SmoothStep(0,1,Mathf.InverseLerp(a,b,v));
 public static void Compose(GameObject collision,WorldEnvironment world,string generated){
  output=generated;materials.Clear();random=new System.Random(90261);stoneSerial=0;
  atlas=Texture(Art+"/Textures/WorldSurfaceAtlas.png");snowTexture=Texture(Art+"/Textures/SnowSurface.png");
  stoneTexture=Texture(LinearBuild.Root+"/Art/EnvironmentKit/VisualF/LimestoneFineF.png");
  var camera=Camera.main.GetUniversalAdditionalCameraData();camera.renderPostProcessing=true;camera.requiresDepthTexture=true;camera.requiresColorTexture=true;camera.antialiasing=AntialiasingMode.SubpixelMorphologicalAntiAliasing;camera.antialiasingQuality=AntialiasingQuality.High;
  GroundMaterial(collision);var root=new GameObject("Authored linear landscape");root.transform.SetParent(collision.transform,false);var p=root.transform;
  River(p,world);Path(p);Abbey(p,world);Vegetation(p);SetupWeather(world,p);
  world.snow=Precipitation(p,"Snow flurries",1);var noise=world.snow.noise;noise.enabled=true;noise.strength=.45f;noise.frequency=.22f;noise.scrollSpeed=.18f;
  foreach(var m in materials.Values.ToArray()){
   if(m.name.StartsWith("Wet_")){m.shader=Shader.Find("Vesper/Linear/WetStone");m.SetTexture("_BaseMap",stoneTexture);m.SetColor("_BaseColor",new Color(.76f,.79f,.77f));m.SetFloat("_Wetness",.87f);m.SetFloat("_ReflectionStrength",.18f);}
   if(m.name.StartsWith("Abbey_CW_Chapel")){m.shader=Shader.Find("Vesper/Linear/WetStone");m.SetTexture("_BaseMap",stoneTexture);m.SetTextureScale("_BaseMap",Vector2.one);m.SetTextureOffset("_BaseMap",Vector2.zero);m.color=new Color(.75f,.78f,.73f);m.SetFloat("_Wetness",.35f);}
   if(m.name.StartsWith("CW_BridgeStone")){m.shader=Shader.Find("Vesper/Linear/WetStone");m.SetFloat("_Wetness",0);m.SetFloat("_ReflectionStrength",0);}
   if(m.name.Contains("moss")||m.name=="Moss"){m.SetTexture("_BaseMap",Texture(Art+"/Textures/MossSurface.png"));m.SetTextureScale("_BaseMap",Vector2.one);m.SetTextureOffset("_BaseMap",Vector2.zero);m.color=new Color(.51f,.66f,.31f);}
  }
  EditorUtility.SetDirty(world);
 }
 static void GroundMaterial(GameObject root){
  foreach(var r in root.GetComponentsInChildren<MeshRenderer>().Where(r=>r.name.StartsWith("Linear terrain"))){
   var mat=r.sharedMaterial;mat.shader=Shader.Find("Vesper/Linear/Ground");mat.SetTexture("_BaseMap",atlas);mat.SetTexture("_SnowMap",snowTexture);mat.SetTexture("_PackedMap",Texture(Art+"/Textures/MaterialTexturesV2/PackedAlpineSnow.png"));mat.SetTexture("_StoneMap",stoneTexture);mat.SetFloat("_DetailScale",.23f);mat.SetFloat("_NormalStrength",.21f);
   var mesh=r.GetComponent<MeshFilter>().sharedMesh;var v=mesh.vertices;var normals=mesh.normals;var colors=new Color[v.Length];
   for(int i=0;i<v.Length;i++){float d=-v[i].z,off=Mathf.Abs(v[i].x);float path=1-S(1.7f,3.3f,off);float frost=WorldLayout.SnowCover(v[i].x,d);float snow=frost*S(.35f,.95f,normals[i].y);snow*=Mathf.Lerp(1,.85f,path);colors[i]=new Color(path,snow,Mathf.Clamp01((1-normals[i].y)*3.2f),WorldLayout.Weights(d).y);}
   mesh.colors=colors;EditorUtility.SetDirty(mesh);
  }
 }
 static Vector3 G(float x,float d,float embed=0)=>new Vector3(x,WorldLayout.Height(x,d)-embed,-d);
 static void Rock(Transform p,float x,float d,float width,float height,float depth,float yaw,bool snowy=false){
  var pos=G(x,d,height*2.7f);var scale=new Vector3(width,height,depth);
  var r=Model(p,"CW_HF_Limestone",pos,scale,yaw,true,true);
  if(snowy)Model(p,"SnowCover/CW_HF_Limestone_SnowCover",pos,scale,yaw);
 }
 static void River(Transform p,WorldEnvironment world){
  Model(p,"BridgeHeroV3/CW_StoneBridgeHeroV3_14m",new Vector3(0,WorldLayout.Level(25),-25),new Vector3(.70f,1,1),0);
  var mat=new Material(Shader.Find("Vesper/Linear/River"));mat.SetColor("_ShallowColor",new Color(.16f,.43f,.43f));mat.SetColor("_DeepColor",new Color(.04f,.24f,.29f));mat.SetFloat("_ReflectionStrength",.68f);AssetDatabase.CreateAsset(mat,output+"/RiverSurface.mat");
  LinearBuild.MeshObject(p,"Linear river surface",new List<Vector3>{new Vector3(-48,WorldLayout.WaterHeight,-13),new Vector3(48,WorldLayout.WaterHeight,-13),new Vector3(48,WorldLayout.WaterHeight,-38),new Vector3(-48,WorldLayout.WaterHeight,-38)},new List<int>{0,1,2,0,2,3},mat,31,false);
  var reflect=new GameObject("Linear river reflection").AddComponent<VesperPlanarReflection>();reflect.sourceCamera=Camera.main;reflect.planeHeight=WorldLayout.WaterHeight;reflect.textureSize=768;reflect.renderShadows=true;reflect.renderSky=true;reflect.reflectedSkybox=RenderSettings.skybox;reflect.reflectionMask=~(1<<31);world.reflection=reflect;
  int i=0;for(float x=-31;x<=31;x+=2.8f){if(Mathf.Abs(x)<3.8f)continue;foreach(float side in new[]{-1f,1f}){
   float d=(side<0?WorldLayout.NearShore(x):WorldLayout.FarShore(x))+side*.45f;
   Model(p,"VisualF/CW_ReedVolume",G(x,d,.1f),new Vector3(R(.65f,1.0f),R(.95f,1.40f),R(.6f,.95f)),R(0,360));
   if(i++%2==0)Rock(p,x,d+side*1.2f,R(.6f,1.1f),R(.18f,.35f),R(.5f,.9f),R(0,360));
   if(i%3==0){float wd=d-side*1.7f;Model(p,"CW_RiverBoulder",new Vector3(x,-1.2f,-wd),new Vector3(.7f,.35f,.8f),R(0,360));}
  }}
  Rock(p,-5.8f,17.2f,.85f,.30f,1.0f,24);Rock(p,6.2f,33.7f,1.05f,.42f,.85f,116);
  Tree(p,7.7f,35,1.65f,false,false,0);Tree(p,-9.3f,13,1.5f,false,false,0);
  for(int k=0;k<200;k++){float x=R(-18,18);if(Mathf.Abs(x)<2.9f)continue;float d=(k%2==0?WorldLayout.NearShore(x)-R(.9f,4):WorldLayout.FarShore(x)+R(.9f,4));Model(p,"CW_RiverGrass",G(x,d,.08f),new Vector3(R(.25f,.65f),R(.3f,.75f),R(.25f,.7f)),R(0,360));}
 }
 static void Paving(Transform p,float d,float scale,float wet,bool scattered=false){
  var go=Model(p,"L02Details/"+(scattered?"LinearFieldstone_":"LinearPaving_")+(1+stoneSerial%3),WorldLayout.Point(d)+Vector3.up*.015f,new Vector3(scale,1,scale),stoneSerial%2*180);
  foreach(var mf in go.GetComponentsInChildren<MeshFilter>()){
   var mesh=UnityEngine.Object.Instantiate(mf.sharedMesh);var v=mesh.vertices;
   for(int i=0;i<v.Length;i++){var w=mf.transform.TransformPoint(v[i]);w.y+=WorldLayout.Height(w.x,-w.z)-WorldLayout.Level(d);v[i]=mf.transform.InverseTransformPoint(w);}
   mesh.vertices=v;mesh.RecalculateNormals();mesh.RecalculateBounds();
   // Remove the square underlay. Actual continuous terrain supports the stone joints.
   var renderer=mf.GetComponent<Renderer>();for(int m=0;m<renderer.sharedMaterials.Length;m++)if(renderer.sharedMaterials[m].name.Contains("Mortar"))mesh.SetTriangles(new int[0],m);
   AssetDatabase.CreateAsset(mesh,output+"/PathStone-"+(stoneSerial++)+".asset");mf.sharedMesh=mesh;
   var mats=renderer.sharedMaterials;for(int k=0;k<mats.Length;k++)if(mats[k].name.StartsWith("Wet_")){
    string key=wet>.7f?"Linear rain path":wet>.2f?"Linear damp path":"Linear dry path";
    if(!materials.TryGetValue(key,out var replacement)){replacement=new Material(Shader.Find("Vesper/Linear/WetStone")){name=key};replacement.SetTexture("_BaseMap",stoneTexture);replacement.SetColor("_BaseColor",wet>.2f?new Color(.80f,.83f,.81f):new Color(.86f,.83f,.73f));replacement.SetFloat("_Wetness",wet);replacement.SetFloat("_ReflectionStrength",.18f);AssetDatabase.CreateAsset(replacement,output+"/"+key+".mat");materials[key]=replacement;}
    mats[k]=replacement;
   }renderer.sharedMaterials=mats;
  }
 }
 static void Path(Transform p){
  for(float d=2;d<=300;d+=3.7f){if(d>16&&d<34)continue;float wet=WorldLayout.Weights(d).y;
   bool continuous=d<48||(d>124&&d<179);
   if(d>287)continue;Paving(p,d,continuous?.97f:R(.85f,1.04f),wet,!continuous);
  }
 }
 static void Abbey(Transform p,WorldEnvironment world){
  float y=WorldLayout.Level(150);
  Model(p,"Chapel/CW_ChapelEntranceArch",new Vector3(4.6f,y,-149),new Vector3(.80f,.80f,.75f),90,true);
  Model(p,"ChapelBroken/CW_ChapelBrokenWall6m",new Vector3(4.6f,y,-155),new Vector3(.75f,.78f,.78f),90,true);
  Model(p,"Chapel/CW_ChapelLancetWall",new Vector3(11,y,-150),new Vector3(.90f,.9f,.85f),90,true);
  Model(p,"ChapelBroken/CW_ChapelBrokenWall6m",new Vector3(8,y,-156.5f),new Vector3(1,.9f,.9f),0,true);
  Model(p,"ChapelBroken/CW_ChapelBrokenPier3m",new Vector3(5,y,-143.5f),new Vector3(.8f,1,.8f),0,true);
  foreach(float d in new[]{146f,150f,154f})Model(p,"L02Details/LinearPaving_"+(d==150?2:1),new Vector3(7.7f,y,-d),new Vector3(.85f,1,.95f),0);
  foreach(var q in new[]{new Vector2(4.1f,154),new Vector2(5.6f,157),new Vector2(11.2f,148),new Vector2(7.5f,143.3f)})Model(p,"AbbeyRubbleV2/CW_AbbeyRubbleMound3m",G(q.x,q.y,.08f),new Vector3(.6f,.65f,.85f),R(0,360),true);
  var roof=Model(p,"ChapelSurfaces/CW_ChapelBrokenSlateRoof6x8m",new Vector3(7,y+4.75f,-147.5f),new Vector3(.65f,.7f,.5f),0,true);roof.AddComponent<WorldRoofCutaway>().world=world;
  world.shelter=new Bounds(new Vector3(7,y+2.1f,-147.5f),new Vector3(3.1f,4.4f,3.4f));
  foreach(float d in new[]{146f,149f})Model(p,"ChapelBroken/CW_ChapelBrokenPier3m",new Vector3(9,y,-d),new Vector3(.6f,1.5f,.6f),0,true);
  Torch(p,new Vector3(4.05f,y+2.0f,-147.4f));
  var reflect=new GameObject("Linear abbey reflection").AddComponent<VesperPlanarReflection>();reflect.sourceCamera=Camera.main;reflect.planeHeight=y+.035f;reflect.textureSize=512;reflect.renderShadows=true;reflect.renderSky=true;reflect.reflectedSkybox=RenderSettings.skybox;reflect.reflectionMask=~(1<<31);world.ruinsReflection=reflect;
 }
 static bool ChapelFootprint(float x,float d)=>x>2.8f&&x<14&&d>138&&d<165;
 static void Tree(Transform p,float x,float d,float scale,bool fir,bool snow,float yaw){
  if(ChapelFootprint(x,d)||WorldLayout.River(x,d))return;
  string file=fir?(snow?"VisualF/CW_FirVolume_"+(random.Next(2)+1):"FoliageFir/CW_CardedAlpineFir"):"FoliageBirch/CW_CardedRiverBirch";
  var t=Model(p,file,G(x,d,.10f),new Vector3(scale*R(.9f,1.1f),scale,scale),yaw);
  var c=t.AddComponent<CapsuleCollider>();t.layer=29;c.center=Vector3.up*1.4f;c.height=2.8f;c.radius=.23f;
  if(fir&&snow&&d<248){float cover=WorldLayout.SnowCover(x,d);foreach(var renderer in t.GetComponentsInChildren<Renderer>())if(renderer.name.Contains("Snow"))renderer.enabled=cover>.35f;}
 }
 static void Vegetation(Transform p){
  for(float d=-8;d<318;d+=6.3f)foreach(float side in new[]{-1f,1f}){
   if(d>10&&d<42)continue;
   float td=d+R(-1.8f,1.8f),off=side*R(5.2f,9.3f);bool fir=td>235||(td>190&&random.NextDouble()<(td-190)/50);
   Tree(p,off,td,fir?R(.8f,1.22f):R(1.05f,1.62f),fir,fir&&td>205,R(0,360));
   if(random.NextDouble()<.70)Tree(p,off+side*R(3.5f,6),td+R(-2,2),R(.9f,1.45f),fir,fir&&td>218,R(0,360));
   if(random.NextDouble()<.38&&!ChapelFootprint(off,td))Rock(p,off+side*2,td+2,R(.55f,1.0f),td>240?R(.45f,.8f):R(.25f,.6f),R(.6f,1.1f),R(0,360),td>218);
  }
  for(int i=0;i<4400;i++){
   float d=R(-9,262),x=(i%2==0?-1:1)*R(2.15f,13);if(WorldLayout.River(x,d)||ChapelFootprint(x,d)||d>10&&d<41)continue;
   if(d>208&&random.NextDouble()<S(205,260,d))continue;
   float clump=.5f+.5f*Mathf.Sin(d*.51f+x*.68f);if(clump<.27f)continue;
   Model(p,"L02Details/LinearGrass_"+(i%2+1),G(x,d,.035f),new Vector3(R(.9f,1.7f),R(.7f,1.3f),R(.9f,1.7f)),R(0,360));
  }
  for(float d=43;d<287;d+=7.5f)foreach(float side in new[]{-1f,1f}){float x=side*R(3.4f,5.2f),td=d+R(-2,2);if(!ChapelFootprint(x,td))Rock(p,x,td,R(.23f,.45f),R(.09f,.19f),R(.25f,.5f),R(0,360),td>214);}
  foreach(var q in new[]{new Vector3(-5.8f,274,.83f),new Vector3(-7.5f,282,1.1f),new Vector3(7.8f,270,.68f),new Vector3(6.5f,283,.72f)})Rock(p,q.x,q.y,1.05f,q.z,1.25f,R(0,360),true);
 }
}
}
