using System;
using System.IO;
using System.Linq;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;
using UnityEditor;

namespace Vesper.Expansion.LinearWorld.Editor {
public static partial class WorldVisuals {
 const string Art="Assets/Vesper/Expansion/ContinuousWorld/Art";
 static string output;static Texture2D atlas,snowTexture,stoneTexture;static System.Random random;
 static readonly Dictionary<string,Material> materials=new Dictionary<string,Material>();
 static float R(float a,float b)=>Mathf.Lerp(a,b,(float)random.NextDouble());
 public static Texture2D Texture(string path,bool normal=false,bool linear=false,TextureWrapMode wrap=TextureWrapMode.Repeat){return AssetDatabase.LoadAssetAtPath<Texture2D>(path);}
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
  string path=Art+"/Textures/"+(birch?"BirchBranches.png":"FirBranches.png");var tex=Texture(path);
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
  if(file.StartsWith("VisualF/"))path=LinearBuild.Root+"/Art/EnvironmentKit/"+file+".fbx";var asset=AssetDatabase.LoadAssetAtPath<GameObject>(path);if(!asset){throw new Exception("Missing required model "+path);}
  var wrapper=new GameObject(file);wrapper.transform.SetParent(parent,false);wrapper.transform.position=pos;wrapper.transform.rotation=Quaternion.Euler(0,yaw,0);wrapper.transform.localScale=scale;
  var go=(GameObject)PrefabUtility.InstantiatePrefab(asset);go.transform.SetParent(wrapper.transform,false);
  foreach(var renderer in go.GetComponentsInChildren<Renderer>()){renderer.sharedMaterials=renderer.sharedMaterials.Select(m=>hf?HFMaterial(file.Replace("_LOD1","")):Slot(m?m.name:"Stone")).ToArray();renderer.shadowCastingMode=ShadowCastingMode.On;}
  if(blocker)foreach(var mf in go.GetComponentsInChildren<MeshFilter>()){mf.gameObject.layer=29;mf.gameObject.AddComponent<MeshCollider>().sharedMesh=mf.sharedMesh;}
  return wrapper;
 }

}
}
