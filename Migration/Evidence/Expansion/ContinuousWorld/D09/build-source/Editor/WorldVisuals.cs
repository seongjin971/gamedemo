using System;
using System.IO;
using System.Linq;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;
using UnityEditor;

namespace Vesper.Expansion.ContinuousWorld.Editor {
public static partial class WorldVisuals {
 const string Art=WorldBuild.Root+"/Art";
 static string output;static Texture2D atlas,snowTexture,stoneTexture;static System.Random random;
 static readonly Dictionary<string,Material> materials=new Dictionary<string,Material>();
 static float R(float a,float b)=>Mathf.Lerp(a,b,(float)random.NextDouble());
 public static Texture2D Texture(string path,bool normal=false,bool linear=false,TextureWrapMode wrap=TextureWrapMode.Repeat){
  var importer=AssetImporter.GetAtPath(path) as TextureImporter;if(importer!=null){bool changed=importer.textureType!=(normal?TextureImporterType.NormalMap:TextureImporterType.Default)||importer.sRGBTexture==linear||importer.maxTextureSize!=2048||importer.anisoLevel!=8||!importer.mipmapEnabled||importer.wrapMode!=wrap;
   importer.textureType=normal?TextureImporterType.NormalMap:TextureImporterType.Default;importer.sRGBTexture=!linear&&!normal;importer.maxTextureSize=2048;importer.anisoLevel=8;importer.mipmapEnabled=true;importer.wrapMode=wrap;if(changed)importer.SaveAndReimport();}
  return AssetDatabase.LoadAssetAtPath<Texture2D>(path);
 }
 static Material Mat(string name,Color tint,float smooth=.2f,Vector2? quadrant=null){
  if(materials.TryGetValue(name,out var prior))return prior;var m=new Material(Shader.Find("Universal Render Pipeline/Lit")){name=name,color=tint,enableInstancing=true};m.SetFloat("_Smoothness",smooth);
  if(quadrant.HasValue){m.SetTexture("_BaseMap",atlas);m.SetTextureScale("_BaseMap",new Vector2(.496f,.496f));m.SetTextureOffset("_BaseMap",quadrant.Value+Vector2.one*.002f);}
  if(name.Contains("Leaf")||name.Contains("Grass")||name.Contains("Reed")||name.Contains("Pine"))m.SetFloat("_Cull",0);
  AssetDatabase.CreateAsset(m,output+"/"+name+".mat");materials[name]=m;return m;
 }
 static Material HFMaterial(string model){
  if(materials.TryGetValue(model,out var existing))return existing;
  string dir=Art+"/HiggsfieldAssets/"+model+"/";var m=Mat(model,new Color(.96f,.95f,.89f));
  var albedo=Texture(dir+model+"_Texture0.png");var normal=Texture(dir+model+"_Texture1.png",true,true);var metal=Texture(dir+model+"_MetallicSmoothness0.png",false,true);
  m.SetTexture("_BaseMap",albedo);m.SetTexture("_BumpMap",normal);m.SetFloat("_BumpScale",.7f);m.EnableKeyword("_NORMALMAP");m.SetTexture("_MetallicGlossMap",metal);m.EnableKeyword("_METALLICSPECGLOSSMAP");m.SetFloat("_Smoothness",.45f);return m;
 }
 static Material Foliage(bool birch){
  string key=birch?"BirchLeaves":"FirNeedles";if(materials.TryGetValue(key,out var existing))return existing;
  string path=Art+"/Textures/"+(birch?"BirchBranches.png":"FirBranches.png");var tex=Texture(path);var importer=AssetImporter.GetAtPath(path) as TextureImporter;if(importer&&!importer.alphaIsTransparency){importer.alphaIsTransparency=true;importer.SaveAndReimport();}
  var m=Mat(key, birch?new Color(.48f,.59f,.44f):new Color(.66f,.8f,.74f));m.shader=Shader.Find("Vesper/WorldFoliage");m.SetTexture("_BaseMap",tex);m.SetFloat("_Cutoff",birch?.4f:.35f);m.SetFloat("_Cull",0);m.SetFloat("_Wind",.035f);m.EnableKeyword("_ALPHATEST_ON");m.renderQueue=2450;return m;
 }
 static Material Slot(string name){
  if(name.Contains("ChapelMoss")){var moss=Mat("Abbey damp moss",new Color(.64f,.70f,.49f),.14f);moss.SetTexture("_BaseMap",Texture(Art+"/Textures/MossSurface.png"));return moss;}
  if(name.Contains("ChapelRubbleStone")){var rubble=Mat("Abbey fractured rubble",new Color(.66f,.70f,.68f),.38f);rubble.SetTexture("_BaseMap",stoneTexture);return rubble;}
  if(name.Contains("ChapelPaving")){var wet=Mat("Wet_"+name,new Color(1.05f,1.05f,1.05f),.8f);wet.SetTexture("_BaseMap",Texture(Art+"/Textures/MaterialTexturesV2/WetAbbeyLimestone.png",false,false,TextureWrapMode.Mirror));wet.shader=Shader.Find("Vesper/WorldWetStone");wet.SetFloat("_Wetness",.8f);wet.SetFloat("_ReflectionStrength",.10f);return wet;}
  if(name.Contains("BridgeMortar"))return Mat("BridgeJointShadow",new Color(.21f,.22f,.20f),.12f);
  if(name.Contains("BridgeStone")){var stone=Mat(name,name.Contains("Light")?new Color(.91f,.90f,.83f):new Color(.85f,.85f,.80f),.18f);stone.SetTexture("_BaseMap",stoneTexture);return stone;}
  if(name.Contains("ChapelJointShadow"))return Mat("AbbeyMortar",new Color(.19f,.23f,.23f),.25f,new Vector2(.5f,.5f));
  if(name.Contains("GoldenReedLight"))return Mat(name,new Color(.94f,.77f,.42f),.08f);
  if(name.Contains("GoldenReedStem"))return Mat(name,new Color(.76f,.59f,.29f),.08f);
  if(name.Contains("DryReedLeaf"))return Mat(name,new Color(.65f,.52f,.27f),.08f);
  if(name.Contains("RoofSlate"))return Mat(name,new Color(.24f,.30f,.34f),.72f,new Vector2(.5f,.5f));
  if(name.Contains("RoofTimber"))return Mat(name,new Color(.23f,.18f,.13f),.32f,new Vector2(0,0));
  if(name.Contains("Chapel")||name.Contains("Paving"))return Mat("Abbey_"+name,new Color(.59f,.64f,.63f),.62f,new Vector2(.5f,.5f));
  if(name.Contains("BirchLeaves"))return Foliage(true);
  if(name.Contains("FirNeedles"))return Foliage(false);
  if(name.Contains("WhiteBirchBark")){var m=Mat("WhiteBirch",new Color(.82f,.82f,.76f),.1f);m.SetTexture("_BaseMap",Texture(Art+"/EnvironmentKit/FoliageBirch/BirchBark.png"));return m;}
  if(name.Contains("BirchTwigs"))return Mat("BirchTwigs",new Color(.22f,.17f,.12f),.07f);
  if(name.Contains("FirBark")){var m=Mat("FirBark",new Color(.64f,.62f,.56f),.1f);m.SetTexture("_BaseMap",atlas);return m;}
  if(name.Contains("Crevice"))return Mat("DarkStone",new Color(.38f,.40f,.37f),.1f,new Vector2(.5f,.5f));
  if(name.Contains("Moss"))return Mat("Moss",new Color(.29f,.40f,.21f),.12f,new Vector2(0,.5f));
  if(name.Contains("Bark"))return Mat("Bark",new Color(.6f,.60f,.53f),.12f,new Vector2(0,0));
  if(name.Contains("Birch"))return Mat("BirchBark",new Color(.92f,.90f,.81f),.12f,new Vector2(0,0));
  if(name.Contains("LeafLight"))return Mat("LeafLight",new Color(.36f,.46f,.20f),.18f);
  if(name.Contains("Leaf"))return Mat("Leaf",new Color(.25f,.38f,.13f),.18f);
  if(name.Contains("Pine"))return Mat("Pine",new Color(.17f,.28f,.21f),.12f);
  if(name.Contains("Snow")){var snow=Mat("Snow",new Color(.86f,.89f,.91f),.14f);snow.SetTexture("_BaseMap",snowTexture);return snow;}
  if(name.Contains("Seed"))return Mat("Seed",new Color(.28f,.18f,.095f),.1f);
  if(name.Contains("ReedDry"))return Mat("ReedDry",new Color(.59f,.54f,.30f),.1f);
  if(name.Contains("Reed"))return Mat("Reed",new Color(.34f,.42f,.18f),.1f);
  if(name.Contains("Grass"))return Mat("Grass",new Color(.31f,.39f,.16f),.1f);
  return Mat("Limestone",new Color(.84f,.83f,.77f),.25f,new Vector2(.5f,.5f));
 }
 static GameObject Model(Transform parent,string file,Vector3 pos,Vector3 scale,float yaw,bool blocker=false,bool hf=false){
  string path=hf?Art+"/HiggsfieldAssets/"+file.Replace("_LOD1","")+"/"+file+".fbx":Art+"/EnvironmentKit/"+file+".fbx";
  var asset=AssetDatabase.LoadAssetAtPath<GameObject>(path);if(!asset){Debug.LogWarning("Missing optional model "+path);return null;}
  var wrapper=new GameObject(file);wrapper.transform.SetParent(parent,false);wrapper.transform.position=pos;wrapper.transform.rotation=Quaternion.Euler(0,yaw,0);wrapper.transform.localScale=scale;
  var go=(GameObject)PrefabUtility.InstantiatePrefab(asset);go.transform.SetParent(wrapper.transform,false);
  foreach(var renderer in go.GetComponentsInChildren<Renderer>()){renderer.sharedMaterials=renderer.sharedMaterials.Select(m=>hf?HFMaterial(file.Replace("_LOD1","")):Slot(m?m.name:"Stone")).ToArray();renderer.shadowCastingMode=ShadowCastingMode.On;}
  if(blocker)foreach(var mf in go.GetComponentsInChildren<MeshFilter>()){mf.gameObject.layer=29;mf.gameObject.AddComponent<MeshCollider>().sharedMesh=mf.sharedMesh;}
  return wrapper;
 }
 static void Grounded(Transform p,string file,float d,float offset,float scale,bool blocker=false,bool hf=false){float x=WorldLayout.Center(d)+offset,y=WorldLayout.Height(x,d);Model(p,file,new Vector3(x,y-.07f,-d),new Vector3(scale,scale,scale),R(0,360),blocker,hf);}
 static void ReshapeStone(GameObject go,bool arch){int serial=0;foreach(var mf in go.GetComponentsInChildren<MeshFilter>()){var mesh=UnityEngine.Object.Instantiate(mf.sharedMesh);var vertices=mesh.vertices;for(int i=0;i<vertices.Length;i++){var p=mf.transform.TransformPoint(vertices[i]);if(arch){float relative=p.y-go.transform.position.y;if(relative<0)p.y=go.transform.position.y+relative*1.5f;}else p.y+=WorldLayout.BridgeRise(-p.z);vertices[i]=mf.transform.InverseTransformPoint(p);}mesh.vertices=vertices;mesh.RecalculateNormals();mesh.RecalculateBounds();AssetDatabase.CreateAsset(mesh,output+"/"+(arch?"RaisedBridge":"SlopedApproach")+go.transform.position.z.ToString("F1",System.Globalization.CultureInfo.InvariantCulture)+"-"+(serial++)+".asset");mf.sharedMesh=mesh;}}
 public static void Waterside(GameObject collision,WorldEnvironment world,string generated){
  output=generated;materials.Clear();random=new System.Random(11873);atlas=Texture(Art+"/Textures/WorldSurfaceAtlas.png");snowTexture=Texture(Art+"/Textures/SnowSurface.png",false,false,TextureWrapMode.Mirror);stoneTexture=Texture(Art+"/Textures/LimestoneSurface.png",false,false,TextureWrapMode.Mirror);
  var detail=new GameObject("Willowbank landscape");detail.transform.SetParent(collision.transform,false);
  foreach(var renderer in collision.GetComponentsInChildren<MeshRenderer>())if(renderer.name.StartsWith("Continuous terrain")){
   var material=renderer.sharedMaterial;material.shader=Shader.Find("Vesper/WorldGround");material.SetTexture("_BaseMap",atlas);material.SetTexture("_SnowMap",snowTexture);material.SetTexture("_PackedMap",Texture(Art+"/Textures/MaterialTexturesV2/PackedAlpineSnow.png",false,false,TextureWrapMode.Mirror));material.SetTexture("_StoneMap",stoneTexture);material.SetColor("_BaseColor",Color.white);material.SetFloat("_DetailScale",.26f);material.SetFloat("_NormalStrength",.23f);
   var mesh=renderer.GetComponent<MeshFilter>().sharedMesh;var v=mesh.vertices;var normals=mesh.normals;var colors=new Color[v.Length];
   for(int i=0;i<v.Length;i++){float d=-v[i].z;var w=WorldLayout.Weights(d);float dist=Mathf.Abs(v[i].x-WorldLayout.Center(d));if(d>34&&d<67)dist=Mathf.Min(dist,Mathf.Abs(v[i].x-WorldLayout.Center(48.5f)));
    float path=1-Mathf.SmoothStep(0,1,Mathf.InverseLerp(Mathf.Lerp(2.5f,1.5f,w.z),Mathf.Lerp(5,3.3f,w.z),dist));float slope=1-normals[i].y;
    colors[i]=new Color(path,w.z*Mathf.SmoothStep(0,1,Mathf.InverseLerp(.25f,.90f,normals[i].y)),Mathf.Clamp01(slope*4),w.y);}
   mesh.colors=colors;EditorUtility.SetDirty(mesh);
  }
  var deck=GameObject.Find("Walkable bridge deck");if(deck)deck.GetComponent<Renderer>().enabled=false;
  foreach(var r in collision.GetComponentsInChildren<MeshRenderer>())if(r.name=="Bridge parapet")r.enabled=false;
  var center=WorldLayout.Center(48.5f);var bridgeVisual=Model(detail.transform,"BridgeHeroV3/CW_StoneBridgeHeroV3_14m",new Vector3(center,WorldLayout.Level(48.5f),-48.5f),Vector3.one,0);ReshapeStone(bridgeVisual,true);
  foreach(float d in new[]{37.5f,59.5f}){var approach=Model(detail.transform,"BridgeHeroV2/CW_BridgeApproach6x8m",new Vector3(center,.90f,-d),Vector3.one,0);ReshapeStone(approach,false);}
  var oldWater=GameObject.Find("Deep river - not walkable");if(oldWater)oldWater.GetComponent<Renderer>().enabled=false;
  var surface=new Material(Shader.Find("Vesper/ContinuousRiver"));surface.SetColor("_ShallowColor",new Color(.15f,.43f,.50f));surface.SetColor("_DeepColor",new Color(.055f,.24f,.29f));AssetDatabase.CreateAsset(surface,output+"/RiverSurface.mat");
  WorldBuild.MeshObject(detail.transform,"One reflective river plane",new List<Vector3>{new Vector3(-90,-.95f,-34),new Vector3(90,-.95f,-34),new Vector3(90,-.95f,-66),new Vector3(-90,-.95f,-66)},new List<int>{0,1,2,0,2,3},surface,31,false);
  var camera=Camera.main;var data=camera.GetUniversalAdditionalCameraData();data.requiresDepthTexture=true;data.requiresColorTexture=true;
  var reflection=new GameObject("Single river reflection").AddComponent<VesperPlanarReflection>();reflection.sourceCamera=camera;reflection.planeHeight=-.95f;reflection.textureSize=768;reflection.renderShadows=true;reflection.renderSky=true;reflection.reflectedSkybox=RenderSettings.skybox;reflection.reflectionMask=~(1<<31);world.reflection=reflection;
  // Geometric clusters leave the full bridge approaches and primary walking lane open.
  for(int i=0;i<24;i++){
   float x=-48+i*4.2f;foreach(float side in new[]{-1f,1f}){float d=side<0?WorldLayout.NearShore(x)-2:WorldLayout.FarShore(x)+2;float away=Mathf.Abs(x-center);if(away<5.2f)continue;
    float y=WorldLayout.Height(x,d);bool heroBank=side>0&&(Mathf.Abs(x-(center+6.5f))<6||Mathf.Abs(x-(center-8.5f))<5);if(!heroBank)Model(detail.transform,"CW_HF_Limestone_LOD1",new Vector3(x,y-1.4f,-d),new Vector3(R(.85f,1.2f),R(.28f,.5f),R(.75f,1.2f)),R(0,360),true,true);
    if(i%3==0)Model(detail.transform,"CW_RiverBoulder",new Vector3(x,-1.5f,-(d+(side<0?3.7f:-3.7f))),new Vector3(.8f,.6f,.8f),R(0,360));
    float rd=side<0?WorldLayout.NearShore(x)+.35f:WorldLayout.FarShore(x)-.35f;Model(detail.transform,away<18?"ReedBand/CW_GoldenReedBand4m":"ReedBand/CW_GoldenReedBand4m_LOD1",new Vector3(x,WorldLayout.Height(x,rd)-.05f,-rd),new Vector3(1,R(1.35f,1.7f),1),R(-12,12));
   }
  }
  foreach(var point in new[]{new Vector2(34,-9),new Vector2(61,9),new Vector2(61,-13),new Vector2(25,12)}){float x=WorldLayout.Center(point.x)+point.y;Model(detail.transform,"CW_HF_Limestone",new Vector3(x,WorldLayout.Height(x,point.x)-.8f,-point.x),new Vector3(1,.48f,.85f),R(0,360),true,true);}
  foreach(var q in new[]{new Vector3(8.5f,55,.65f),new Vector3(-5.5f,55,.85f),new Vector3(-6.3f,37.5f,.65f),new Vector3(9,38,.5f)})Model(detail.transform,"CW_HF_Limestone",new Vector3(center+q.x,-.65f,-q.y),new Vector3(q.x==-5.5f?.9f:q.x>0?.95f:1.35f,q.z,q.x==-5.5f?.75f:q.x>0?.85f:1.2f),R(0,360),true,true);
  Model(detail.transform,"CW_HF_Limestone",new Vector3(center-9.5f,-.65f,-55),new Vector3(1.2f,.65f,1),205,true,true);
  foreach(var q in new[]{new Vector2(-8.5f,53.5f),new Vector2(-6.3f,39.8f)})Model(detail.transform,"ReedBand/CW_GoldenReedBand4m",new Vector3(center+q.x,-.73f,-q.y),new Vector3(1,1.7f,1),15);
  for(float d=5;d<145;d+=7){
   foreach(float side in new[]{-1f,1f}){
    if(d>25&&d<67)continue;
    float offset=side*R(8,15),treeD=d+R(-2,2),treeScale=R(.85f,1.15f);Grounded(detail.transform,"FoliageBirch/CW_CardedRiverBirch_LOD1",treeD,offset,treeScale);
    // Only the visible trunk blocks walking; broad foliage does not create a giant collision box.
    float tx=WorldLayout.Center(treeD)+offset,ty=WorldLayout.Height(tx,treeD);var trunk=new GameObject("Tree trunk");trunk.layer=29;trunk.transform.SetParent(collision.transform,false);trunk.transform.position=new Vector3(tx,ty+1.2f*treeScale,-treeD);var capsule=trunk.AddComponent<CapsuleCollider>();capsule.height=2.4f*treeScale;capsule.radius=.23f*treeScale;
    if(((int)d)%3==0)Grounded(detail.transform,"CW_HF_Limestone_LOD1",d,side*R(11,20),R(.45f,.8f),true,true);
   }
  }
  for(int i=0;i<450;i++){float d=R(-8,147),offset=(random.Next(2)==0?-1:1)*R(4.7f,20);if(d>25&&d<67)continue;Grounded(detail.transform,"CW_RiverGrass",d,offset,R(.65f,1.25f));}
  foreach(float d in new[]{25f,85f,130f,175f,230f,275f,330f,375f}){var old=GameObject.Find("Route waystone "+d);if(old){old.GetComponent<Renderer>().enabled=false;Model(detail.transform,"CW_StoneWaymarker",old.transform.position-Vector3.up*.65f,Vector3.one*.58f,0);}}
  var test=GameObject.Find("Blocked test outcrop");if(test){test.GetComponent<Renderer>().enabled=false;Model(detail.transform,"CW_LayeredRock_A",test.transform.position-Vector3.up*1.08f,new Vector3(.42f,.85f,.55f),0);}
  float heroX=center-8f,heroD=53.5f;Physics.SyncTransforms();float heroY=.8f;if(Physics.Raycast(new Vector3(heroX,12,-heroD),Vector3.down,out var rootHit,14,WorldMotor.BlockMask|WorldMotor.SurfaceMask))heroY=Mathf.Max(.8f,rootHit.point.y-.08f);var hero=Model(detail.transform,"FoliageBirch/CW_CardedRiverBirch",new Vector3(heroX,heroY,-heroD),new Vector3(1.5f,1.05f,1.5f),45);var heroTrunk=hero.AddComponent<CapsuleCollider>();hero.layer=29;heroTrunk.center=Vector3.up*1.2f;heroTrunk.height=2.4f;heroTrunk.radius=.25f;
  // Scenic rocks must not occupy the authored walking corridor, including its bridge doglegs.
  Physics.SyncTransforms();var obstructions=new HashSet<GameObject>();
  for(float d=0;d<=145;d+=.5f)foreach(float offset in new[]{-2.2f,0,2.2f}){float px=d>=43&&d<=55?center:WorldLayout.Center(d);var p=new Vector3(px+offset,WorldLayout.Level(d),-d);foreach(var hit in Physics.OverlapCapsule(p+Vector3.up*.4f,p+Vector3.up*1.4f,.25f,WorldMotor.BlockMask,QueryTriggerInteraction.Ignore)){var t=hit.transform;while(t.parent&&t.parent!=detail.transform)t=t.parent;if(t.parent==detail.transform&&t.name.Contains("HF_Limestone"))obstructions.Add(t.gameObject);}}
  foreach(var rock in obstructions){Debug.Log("WORLD CLEARANCE removed new scenic rock at "+rock.transform.position+" from primary lane");UnityEngine.Object.DestroyImmediate(rock);}Physics.SyncTransforms();
  EditorUtility.SetDirty(world);
 }
}
}
