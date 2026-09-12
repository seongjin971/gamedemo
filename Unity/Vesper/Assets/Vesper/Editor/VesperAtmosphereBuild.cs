using System;
using System.IO;
using System.Linq;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;
using UnityEditor;
using UnityEditor.SceneManagement;

namespace Vesper.Editor {
public static class VesperAtmosphereBuild {
 public const string Root="Assets/Vesper/AtmosphereV2", Scene="Assets/Vesper/Scenes/VesperAtmosphereV2.unity";
 public static void Folder(string p){if(AssetDatabase.IsValidFolder(p))return;int i=p.LastIndexOf('/');Folder(p.Substring(0,i));AssetDatabase.CreateFolder(p.Substring(0,i),p.Substring(i+1));}
 public static T Save<T>(T asset,string path) where T:UnityEngine.Object {var old=AssetDatabase.LoadAssetAtPath<T>(path);if(old){if(asset is Material sourceMat && old is Material oldMat){oldMat.shader=sourceMat.shader;oldMat.CopyPropertiesFromMaterial(sourceMat);}else if(asset is Mesh sourceMesh && old is Mesh oldMesh){oldMesh.Clear();oldMesh.indexFormat=sourceMesh.indexFormat;oldMesh.vertices=sourceMesh.vertices;oldMesh.normals=sourceMesh.normals;oldMesh.uv=sourceMesh.uv;oldMesh.colors=sourceMesh.colors;oldMesh.tangents=sourceMesh.tangents;oldMesh.triangles=sourceMesh.triangles;oldMesh.RecalculateBounds();}else EditorUtility.CopySerialized(asset,old);UnityEngine.Object.DestroyImmediate(asset);EditorUtility.SetDirty(old);return old;}AssetDatabase.CreateAsset(asset,path);return asset;}
 [MenuItem("VESPER/Atmosphere V2/Rebuild candidate from preserved slice")]
 public static void Build(){
  Folder(Root);Folder(Root+"/Materials");Folder(Root+"/Settings");Folder(Root+"/Textures");
  string detailPath=Root+"/Textures/rock_05_diff_2k.png";if(!File.Exists(detailPath))throw new FileNotFoundException("Missing versioned mineral texture",detailPath);AssetDatabase.ImportAsset(detailPath);var ti=(TextureImporter)AssetImporter.GetAtPath(detailPath);ti.sRGBTexture=true;ti.wrapMode=TextureWrapMode.Repeat;ti.anisoLevel=8;ti.textureCompression=TextureImporterCompression.Uncompressed;ti.SaveAndReimport();
  string normalPath=Root+"/Textures/rock_05_nor_gl_2k.png",roughPath=Root+"/Textures/rock_05_rough_2k.png";
  string aoPath=Root+"/Textures/rock_05_ao_2k.png";
  foreach(string map in new[]{normalPath,roughPath,aoPath}){AssetDatabase.ImportAsset(map);var importer=(TextureImporter)AssetImporter.GetAtPath(map);importer.textureType=map==normalPath?TextureImporterType.NormalMap:TextureImporterType.Default;importer.sRGBTexture=false;importer.wrapMode=TextureWrapMode.Repeat;importer.anisoLevel=8;importer.maxTextureSize=2048;importer.textureCompression=TextureImporterCompression.Uncompressed;importer.SaveAndReimport();}
  string wetPath=Root+"/Textures/courtyard-wet-mask.png";AssetDatabase.ImportAsset(wetPath);var wi=(TextureImporter)AssetImporter.GetAtPath(wetPath);wi.sRGBTexture=false;wi.wrapMode=TextureWrapMode.Clamp;wi.textureCompression=TextureImporterCompression.Uncompressed;wi.SaveAndReimport();
  var scene=EditorSceneManager.OpenScene("Assets/Vesper/Scenes/VesperMigrationSlice.unity");
  var materials=new Dictionary<Material,Material>();
  foreach(var r in UnityEngine.Object.FindObjectsByType<Renderer>()){
   r.sharedMaterials=r.sharedMaterials.Select(source=>{
    if(materials.TryGetValue(source,out var reused))return reused;
    var m=new Material(source);string path=AssetDatabase.GetAssetPath(source);string name=Path.GetFileNameWithoutExtension(path);
    if(m.shader.name=="Vesper/WetStone"){
     m.shader=Shader.Find("Vesper/AtmosphereStone");
     if(m.GetTexture("_BaseMap")&&m.GetTexture("_BaseMap").name.Contains("stone")){
      m.SetFloat("_Photographic",1);m.SetTexture("_DetailNormal",AssetDatabase.LoadAssetAtPath<Texture2D>(normalPath));m.SetTexture("_RoughnessMap",AssetDatabase.LoadAssetAtPath<Texture2D>(roughPath));m.SetTexture("_WetMask",AssetDatabase.LoadAssetAtPath<Texture2D>(wetPath));m.SetTexture("_DetailMap",AssetDatabase.LoadAssetAtPath<Texture2D>(detailPath));var tint=m.GetColor("_BaseColor");m.SetColor("_BaseColor",tint*.70f);m.SetFloat("_ReflectionStrength",1.55f);m.SetFloat("_ReflectionHeightRange",.22f);m.SetFloat("_ReflectionDistortion",.0022f);
      m.SetTexture("_StoneAO",AssetDatabase.LoadAssetAtPath<Texture2D>(aoPath));m.SetFloat("_BumpScale",m.GetFloat("_BumpScale")*.82f);m.SetFloat("_RainWetness",.35f);m.SetFloat("_ReflectionStrength",0);
     }else{m.SetFloat("_Wind",1);m.SetTexture("_DetailMap",Texture2D.grayTexture);m.SetFloat("_Cull",0);}
    }
    if(name=="CityBackdrop"){m.shader=Shader.Find("Vesper/AtmosphereBackdrop");m.renderQueue=1000;m.SetColor("_BaseColor",new Color(.30f,.57f,.706f));}
    if(m.shader.name=="Vesper/Flame"){m.shader=Shader.Find("Vesper/AtmosphereFlame");m.SetColor("_BaseColor",new Color(5.5f,5.5f,4.5f,1));m.SetTexture("_BaseMap",ImportMeasuredTexture("../../Migration/Source/AtmosphereV2/FlameV17/flame-v17.png","FlameV17.png",false,true));m.SetFloat("_RadianceScale",1.044874f);m.SetFloat("_Upright",1);m.SetFloat("_SourceRadiance",1);}
    if(m.GetTexture("_BaseMap")&&m.GetTexture("_BaseMap").name.Contains("bark")){m.SetColor("_BaseColor",m.GetColor("_BaseColor")*1.3f);m.SetFloat("_BumpScale",.95f);}
    if(name=="1ba07011-f8c4-4d07-9550-6d031350c67f"){m.SetColor("_BaseColor",m.GetColor("_BaseColor")*.75f);m.SetFloat("_WaterLayer",1);m.SetFloat("_ReflectionStrength",0);}
    if(name=="f07c4b31-f38a-44bb-bd4f-1a92d5329f38")m.SetColor("_BaseColor",new Color(.36f,.385f,.41f));
    if(name=="08b6ee59-7da1-4fb0-bd5d-a752d5b8fa60")m.SetColor("_BaseColor",new Color(.318f,.33f,.342f));
    if(name=="660185b7-431d-49af-8a8c-aa2391b84c1a"){m.SetColor("_BaseColor",m.GetColor("_BaseColor")*1.45f);m.SetFloat("_Smoothness",.18f);}
    if(name=="fdd18605-e620-408c-bc78-fe88a967e48a"){m.SetFloat("_Metallic",.15f);m.SetFloat("_Smoothness",.20f);m.SetColor("_BaseColor",m.GetColor("_BaseColor")*.3f);}
    if(m.shader.name=="Vesper/AtmosphereStone"){if(m.GetFloat("_Photographic")>.5f)m.EnableKeyword("_PHOTOGRAPHIC_STONE");else m.DisableKeyword("_PHOTOGRAPHIC_STONE");if(m.GetFloat("_WaterLayer")>.5f)m.EnableKeyword("_SEPARATE_WATER");else m.DisableKeyword("_SEPARATE_WATER");}
    m=Save(m,Root+"/Materials/"+name+".mat");materials[source]=m;return m;
   }).ToArray();
   if(r.sharedMaterial&&r.sharedMaterial.HasProperty("_Distant")&&r.sharedMaterial.GetFloat("_Distant")>.5f){r.gameObject.layer=30;r.sharedMaterial.renderQueue=2950;}
  }
  // Native ambient and sun energy are tuned separately from fire and reflection.
  RenderSettings.ambientSkyColor=new Color(.18f,.265f,.35f);RenderSettings.ambientEquatorColor=new Color(.065f,.105f,.145f);RenderSettings.ambientGroundColor=new Color(.019f,.024f,.03f);
  RenderSettings.fogColor=new Color(.125f,.212f,.267f);RenderSettings.fogDensity=.0048f;RenderSettings.fog=false;
  var moon=GameObject.Find("Moon").GetComponent<Light>();moon.intensity=1.6f;moon.shadowStrength=.90f;
  GameObject.Find("Tree key").GetComponent<Light>().intensity=12;GameObject.Find("Tree key").GetComponent<Light>().color=new Color(.82f,.73f,.61f);
  foreach(var l in UnityEngine.Object.FindObjectsByType<Light>())if(l.name=="Brazier"){
   l.shadows=LightShadows.Soft;l.shadowBias=.025f;l.shadowNormalBias=.15f;
   var data=l.GetUniversalAdditionalLightData();data.usePipelineSettings=false;data.softShadowQuality=SoftShadowQuality.Low;
   var lightSettings=new SerializedObject(data);lightSettings.FindProperty("m_AdditionalLightsShadowResolutionTier").intValue=1;lightSettings.ApplyModifiedPropertiesWithoutUndo();
   l.intensity=l.transform.position.x>0?10.5f:14.5f;l.color=new Color(1,.565f,.18f);l.range=4.8f;l.transform.position+=Vector3.up*.22f;
   Lamp("Brazier stone bounce",new Vector3(l.transform.position.x,.9f,l.transform.position.z+.55f),new Color(1,.65f,.34f),.75f,2.8f);
  }
  ConfigurePipeline();
  var reflection=UnityEngine.Object.FindAnyObjectByType<VesperPlanarReflection>();reflection.reflectionMask=~((1<<29)|(1<<30)|(1<<31));reflection.textureSize=1024;reflection.renderShadows=false;reflection.renderSky=true;reflection.rendererIndex=1;
  var volume=UnityEngine.Object.FindAnyObjectByType<Volume>();var profile=ScriptableObject.CreateInstance<VolumeProfile>();
  foreach(var c in volume.sharedProfile.components){var copy=Save(UnityEngine.Object.Instantiate(c),Root+"/Settings/"+c.GetType().Name+".asset");profile.components.Add(copy);}
  volume.sharedProfile=Save(profile,Root+"/Settings/NightGrade.asset");
  profile=volume.sharedProfile;if(profile.TryGet<Bloom>(out var bloom)){bloom.intensity.value=.34f;bloom.scatter.value=.66f;bloom.threshold.value=1.1f;EditorUtility.SetDirty(bloom);}
  // Warm relic lighting was absent from the first native bridge.
  Lamp("Relic glow",new Vector3(-2.8f,5.62f,-8.1f),new Color(1,.667f,.26f),3.5f,4.2f);
  Lamp("Portal bounce",new Vector3(-2.8f,7.8f,-7.3f),new Color(1,.604f,.212f),4.5f,5.2f);
  BuildEffects();BuildSky();BuildStandingWater();LoadArchitecture();RestoreFoundations();InstallTree();InstallStone();InstallPaving();InstallStairs();InstallFacade();InstallContact();InstallKnight();foreach(var mesh in architecture.Concat(facadeCourses))UnityEngine.Object.DestroyImmediate(mesh);Debug.Log("VESPER_FACADE_COURSES "+facadeCourseCount);
  var camera=Camera.main;var oldControl=camera.GetComponent<VesperCamera>();var player=oldControl.player;UnityEngine.Object.DestroyImmediate(oldControl);var control=camera.gameObject.AddComponent<VesperOrbitCamera>();control.player=player;
  camera.orthographicSize=control.homeSize;var focus=control.homeTarget;camera.transform.position=focus+new Vector3(-Mathf.Sin(.46f)*Mathf.Cos(.72f),Mathf.Sin(.72f),Mathf.Cos(.46f)*Mathf.Cos(.72f))*42;camera.transform.LookAt(focus);
  VesperLocalShadowBuild.Build();
  EditorSceneManager.SaveScene(scene,Scene);AssetDatabase.SaveAssets();
  Debug.Log("VESPER_ATMOSPHERE_BUILD_PASS "+Scene);
 }
 static void Lamp(string name,Vector3 pos,Color color,float intensity,float range){var l=new GameObject(name).AddComponent<Light>();l.type=LightType.Point;l.transform.position=pos;l.color=color;l.intensity=intensity;l.range=range;}
 static void BuildStandingWater(){
  var material=new Material(Shader.Find("Vesper/StandingWater"));material.SetTexture("_WetMask",AssetDatabase.LoadAssetAtPath<Texture2D>(Root+"/Textures/courtyard-wet-mask.png"));material=Save(material,Root+"/Materials/StandingWater.mat");
  var go=GameObject.CreatePrimitive(PrimitiveType.Quad);go.name="Continuous shallow courtyard water";UnityEngine.Object.DestroyImmediate(go.GetComponent<Collider>());go.transform.position=new Vector3(-1.2f,-.004f,5);go.transform.rotation=Quaternion.Euler(90,0,0);go.transform.localScale=new Vector3(18,26,1);go.layer=31;var r=go.GetComponent<MeshRenderer>();r.sharedMaterial=material;r.shadowCastingMode=ShadowCastingMode.Off;r.receiveShadows=false;
 }
 static void BuildPools(){
  var material=new Material(Shader.Find("Vesper/ShallowWater"));material.SetTexture("_Mineral",AssetDatabase.LoadAssetAtPath<Texture2D>(Root+"/Textures/stratified-stone.png"));material=Save(material,Root+"/Materials/ShallowWater.mat");
  var patches=new[]{new Vector4(1.4f,3.5f,2.8f,4.8f),new Vector4(-6.6f,3.2f,2.2f,4.0f),new Vector4(1.2f,11,3.8f,3.1f),new Vector4(-4.7f,12.5f,2.9f,3.6f),new Vector4(5.1f,6.4f,2.8f,2.1f)};
  foreach(var p in patches){var go=GameObject.CreatePrimitive(PrimitiveType.Quad);go.name="Shallow courtyard pool";UnityEngine.Object.DestroyImmediate(go.GetComponent<Collider>());go.transform.position=new Vector3(p.x,-.022f,p.y);go.transform.rotation=Quaternion.Euler(90,0,0);go.transform.localScale=new Vector3(p.z,p.w,1);go.layer=31;var renderer=go.GetComponent<MeshRenderer>();renderer.sharedMaterial=material;renderer.shadowCastingMode=ShadowCastingMode.Off;renderer.receiveShadows=false;}
 }
 static void ConfigurePipeline(){
  var source=AssetDatabase.LoadAssetAtPath<UniversalRenderPipelineAsset>("Assets/Vesper/Settings/VesperURP.asset");
  var pipelineAsset=UnityEngine.Object.Instantiate(source);pipelineAsset.name="AtmosphereURP";var pipeline=Save(pipelineAsset,Root+"/Settings/AtmosphereURP.asset");
  var renderer=UnityEngine.Object.Instantiate(AssetDatabase.LoadAssetAtPath<UniversalRendererData>("Assets/Vesper/Settings/VesperRenderer.asset"));renderer.rendererFeatures.Clear();renderer=Save(renderer,Root+"/Settings/ReflectionRenderer.asset");
  var serialized=new SerializedObject(pipeline);serialized.FindProperty("m_SoftShadowsSupported").boolValue=true;var list=serialized.FindProperty("m_RendererDataList");list.arraySize=2;list.GetArrayElementAtIndex(1).objectReferenceValue=renderer;serialized.ApplyModifiedPropertiesWithoutUndo();
  pipeline.supportsCameraOpaqueTexture=false;GraphicsSettings.defaultRenderPipeline=pipeline;QualitySettings.renderPipeline=pipeline;EditorUtility.SetDirty(pipeline);
 }
 static LineRenderer Ring(Transform parent,string name,float radius,Material mat){
  var go=new GameObject(name);go.transform.SetParent(parent,false);var l=go.AddComponent<LineRenderer>();l.useWorldSpace=false;l.loop=true;l.positionCount=192;l.widthMultiplier=.018f;l.numCornerVertices=2;l.sharedMaterial=mat;l.shadowCastingMode=ShadowCastingMode.Off;
  var points=new Vector3[192];for(int i=0;i<192;i++){float a=i*Mathf.PI*2/192;points[i]=new Vector3(Mathf.Cos(a)*radius,Mathf.Sin(a)*radius,0);}l.SetPositions(points);
  var soft=new GameObject("Local line glow");soft.transform.SetParent(go.transform,false);var glow=soft.AddComponent<LineRenderer>();glow.useWorldSpace=false;glow.loop=true;glow.positionCount=192;glow.widthMultiplier=.12f;glow.numCornerVertices=2;glow.sharedMaterial=AssetDatabase.LoadAssetAtPath<Material>(Root+"/Materials/RuneGlow.mat");glow.shadowCastingMode=ShadowCastingMode.Off;glow.SetPositions(points);
  return l;
 }
 static void BuildEffects(){
  var root=new GameObject("Native atmosphere and sacred rings");var motion=root.AddComponent<VesperAtmosphereMotion>();
  var softRune=new Material(Shader.Find("Vesper/RuneGlow"));softRune.SetColor("_BaseColor",new Color(1.6f,.65f,.15f,.22f));Save(softRune,Root+"/Materials/RuneGlow.mat");
  var rune=new Material(Shader.Find("Universal Render Pipeline/Unlit"));rune.SetColor("_BaseColor",new Color(4.0f,2.05f,.58f));rune=Save(rune,Root+"/Materials/Rune.mat");
  var halo=new GameObject("Restored ring assembly");halo.transform.SetParent(root.transform);halo.transform.position=new Vector3(-2.8f,5.62f,-8.1f);motion.halo=halo.transform;
  motion.rings=new[]{Ring(halo.transform,"Outer ring",.94f,rune).transform,Ring(halo.transform,"Inner ring",.69f,rune).transform,Ring(halo.transform,"Orbit A",.88f,rune).transform,Ring(halo.transform,"Orbit B",.88f,rune).transform};
  motion.rings[2].localRotation=Quaternion.Euler(0,1.1f*Mathf.Rad2Deg,0);motion.rings[3].localRotation=Quaternion.Euler(.92f*Mathf.Rad2Deg,0,0);
  var baseRing=Ring(root.transform,"Pedestal circle",.56f,rune);baseRing.transform.position=new Vector3(-2.8f,3.943f,-8.1f);baseRing.transform.rotation=Quaternion.Euler(90,0,0);
  motion.flames=UnityEngine.Object.FindObjectsByType<VesperBillboard>().Where(b=>b.GetComponent<Renderer>()?.sharedMaterial?.shader.name=="Vesper/AtmosphereFlame").Select(b=>b.transform).ToArray();
  // The upright texture's luminous lower margin now starts at the coal bed,
  // instead of leaning the camera-facing sheet through the bowl geometry.
  foreach(var flame in motion.flames)flame.position+=Vector3.up*.11f;
  var mist=new Material(Shader.Find("Vesper/ValleyMist"));mist.SetColor("_BaseColor",new Color(.020f,.055f,.087f,.11f));mist=Save(mist,Root+"/Materials/ValleyMist.mat");
  for(int i=0;i<10;i++)Mist(root.transform,mist,new Vector3(Mathf.Sin(i*7)*14,-3-i*1.5f,-15+i*5),new Vector2(55,15));
  for(int i=0;i<3;i++)Mist(root.transform,mist,new Vector3(5-i*2,-4,-13-i*12),new Vector2(70,17));
  var baseMist=new Material(mist);baseMist.SetColor("_BaseColor",new Color(.020f,.055f,.088f,.30f));baseMist=Save(baseMist,Root+"/Materials/FoundationMist.mat");
  Mist(root.transform,baseMist,new Vector3(17,-8,-8),new Vector2(24,16));Mist(root.transform,baseMist,new Vector3(-18,-10,2),new Vector2(26,20));Mist(root.transform,baseMist,new Vector3(15,-5,-9),new Vector2(24,12));
  var emberMat=new Material(Shader.Find("Universal Render Pipeline/Particles/Unlit"));emberMat.SetColor("_BaseColor",new Color(3,1.3f,.25f));emberMat.SetFloat("_Surface",1);emberMat.SetFloat("_Blend",2);emberMat.SetFloat("_SrcBlend",(float)BlendMode.SrcAlpha);emberMat.SetFloat("_DstBlend",(float)BlendMode.One);emberMat.SetFloat("_ZWrite",0);emberMat.EnableKeyword("_SURFACE_TYPE_TRANSPARENT");emberMat.renderQueue=3000;emberMat=Save(emberMat,Root+"/Materials/Ember.mat");
  foreach(float x in new[]{1.65f,-6.9f}){var go=new GameObject("Rising cinders");go.transform.SetParent(root.transform);go.transform.position=new Vector3(x,1.7f,-1.45f);var ps=go.AddComponent<ParticleSystem>();ps.Stop(true,ParticleSystemStopBehavior.StopEmittingAndClear);var main=ps.main;main.duration=8;main.loop=true;main.startLifetime=new ParticleSystem.MinMaxCurve(1.5f,3.3f);main.startSpeed=new ParticleSystem.MinMaxCurve(.55f,1.1f);main.startSize=new ParticleSystem.MinMaxCurve(.013f,.030f);main.startColor=new Color(1,.7f,.3f,.85f);main.simulationSpace=ParticleSystemSimulationSpace.World;main.maxParticles=90;main.prewarm=true;var emission=ps.emission;emission.rateOverTime=16;var shape=ps.shape;shape.shapeType=ParticleSystemShapeType.Cone;shape.angle=7;shape.radius=.23f;shape.rotation=new Vector3(-90,0,0);var velocity=ps.velocityOverLifetime;velocity.enabled=true;velocity.x=new ParticleSystem.MinMaxCurve(.12f);velocity.y=new ParticleSystem.MinMaxCurve(.35f);velocity.z=new ParticleSystem.MinMaxCurve(0);var color=ps.colorOverLifetime;color.enabled=true;var g=new Gradient();g.SetKeys(new[]{new GradientColorKey(Color.white,0),new GradientColorKey(new Color(1,.3f,.04f),1)},new[]{new GradientAlphaKey(0,0),new GradientAlphaKey(1,.15f),new GradientAlphaKey(0,1)});color.color=g;var pr=go.GetComponent<ParticleSystemRenderer>();pr.sharedMaterial=emberMat;pr.renderMode=ParticleSystemRenderMode.Stretch;pr.lengthScale=.8f;pr.velocityScale=.02f;ps.randomSeed=(uint)(x>0?123:456);ps.useAutoRandomSeed=false;ps.Play();}
 }
 static void Mist(Transform parent,Material mat,Vector3 pos,Vector2 size){var go=GameObject.CreatePrimitive(PrimitiveType.Quad);go.name="Drifting depth mist";UnityEngine.Object.DestroyImmediate(go.GetComponent<Collider>());go.transform.SetParent(parent);go.transform.position=pos;go.transform.localScale=new Vector3(size.x,size.y,1);go.layer=30;var r=go.GetComponent<MeshRenderer>();r.sharedMaterial=mat;r.shadowCastingMode=ShadowCastingMode.Off;r.receiveShadows=false;}
 static Mesh ReadNativeMesh(string path,string name){return NativeMesh(JsonUtility.FromJson<Geo>(File.ReadAllText(path)),name);}
 static Mesh NativeMesh(Geo g,string name,bool strictWinding=true){
  int count=g.positions.Length/3;var m=new Mesh{name=name,indexFormat=IndexFormat.UInt32};var p=new Vector3[count];var n=new Vector3[count];var uv=new Vector2[count];for(int i=0;i<count;i++){p[i]=new Vector3(g.positions[i*3],g.positions[i*3+1],g.positions[i*3+2]);n[i]=new Vector3(g.normals[i*3],g.normals[i*3+1],g.normals[i*3+2]);uv[i]=new Vector2(g.uv[i*2],g.uv[i*2+1]);}int normalOutliers=0;for(int t=0;t<g.indices.Length;t+=3){int a=g.indices[t],b=g.indices[t+1],c=g.indices[t+2];if(Vector3.Dot(Vector3.Cross(p[b]-p[a],p[c]-p[a]),n[a]+n[b]+n[c])< -1e-10f)normalOutliers++;}if(normalOutliers>0){if(strictWinding)throw new Exception("Native face winding disagrees with normals: "+name+" count "+normalOutliers);Debug.Log("VESPER_PRESERVED_KNIGHT_NORMAL_OUTLIERS "+name+" "+normalOutliers);}
  m.vertices=p;m.normals=n;m.uv=uv;if(g.colors!=null&&g.colors.Length==count*4){var colors=new Color[count];for(int i=0;i<count;i++)colors[i]=new Color(g.colors[i*4],g.colors[i*4+1],g.colors[i*4+2],g.colors[i*4+3]);m.colors=colors;}m.triangles=g.indices;m.RecalculateBounds();m.RecalculateTangents();return m;
 }
 [Serializable]class KnightPart:Geo{public string gameObjectName;}
 [Serializable]class KnightPack{public KnightPart[] objects;}
 static void InstallKnight(){
  const string folder="../../Migration/Source/AtmosphereV2/KnightV7/";
  int replaced=0;
  foreach(string file in new[]{"knight-v7-unity-meshes.json","helmet-v6-unity-mesh.json"}){
   string source=folder+file;if(!File.Exists(source))throw new FileNotFoundException("Required KnightV7 candidate missing",source);
   var pack=JsonUtility.FromJson<KnightPack>(File.ReadAllText(source));
   foreach(var part in pack.objects){
    var go=GameObject.Find(part.gameObjectName);if(!go)throw new Exception("Missing knight part "+part.gameObjectName);
    // V6 repairs the two degenerate shoulder pole caps. All eight exports now
    // pass strict winding checks; preserve their existing parents and materials.
    go.GetComponent<MeshFilter>().sharedMesh=Save(NativeMesh(part,part.gameObjectName),Root+"/Meshes/Knight-"+part.gameObjectName+".asset");replaced++;
   }
  }
  Debug.Log("VESPER_KNIGHT_V7_PARTS_REPLACED "+replaced);
 }
 static Mesh[] architecture,facadeCourses;static int facadeCourseCount;
 static void LoadArchitecture(){
  string path="../../Migration/Source/AtmosphereV2/MasonryV12/";
  architecture=Enumerable.Range(0,6).Select(i=>ReadNativeMesh(path+"masonry-v12-"+i+".json","Upright fractured masonry V12 "+i)).ToArray();
  facadeCourses=Enumerable.Range(0,2).Select(i=>ReadNativeMesh(path+"facade-v12-"+i+".json","Unequal facade course V12 "+i)).ToArray();facadeCourseCount=0;
 }
 static void AddColoredMesh(Mesh source,Vector3 position,Quaternion rotation,Vector3 scale,Color color,List<Mesh> temp,List<CombineInstance> instances){
  var m=UnityEngine.Object.Instantiate(source);m.colors=Enumerable.Repeat(color,m.vertexCount).ToArray();temp.Add(m);instances.Add(new CombineInstance{mesh=m,transform=Matrix4x4.TRS(position,rotation,scale)});
 }
 static void AppendStone(Instance i,Mesh source,bool floor,bool trim,int seed,List<Mesh> temp,List<CombineInstance> instances,Mesh localOverride=null){
  var position=new Vector3(-i.position[0],i.position[1],i.position[2]);var rotation=new Quaternion(i.quaternion[0],-i.quaternion[1],-i.quaternion[2],i.quaternion[3]);var scale=new Vector3(i.scale[0],i.scale[1],i.scale[2]);var color=new Color(i.color[0],i.color[1],i.color[2],1);
  if(trim&&position.y<.1f&&seed%3==0)return;
  // The source flight used a second uniform lip in front of every tread.
  // Retain selected worn lips and break the others into unequal short remnants.
  if(floor&&position.y>.2f&&position.y<3.1f&&scale.y<.06f&&scale.z<.09f){
   if(seed%3==0)return;
   if(seed%3==1){scale.x*=.62f;position.x+=.08f*Mathf.Sin(seed*2.3f);}
  }
  if(floor&&position.y<.2f){
   scale.x*=1.075f;scale.z*=1.075f;
   if(seed%3==0&&Mathf.Abs(position.x)<7.8f&&position.z>0){scale.x*=.93f;position.x+=Mathf.Sin(seed*7.31f)*.035f;position.z+=Mathf.Cos(seed*3.7f)*.018f;rotation*=Quaternion.Euler(0,Mathf.Sin(seed)*1.8f,0);}
  }
  bool vertical=!floor&&scale.y>3&&scale.x<1.8f&&scale.z<1.8f&&Mathf.Abs((rotation*Vector3.up).y)>.95f;
  if(vertical){
   int count=Mathf.CeilToInt(scale.y/.48f);var weights=new float[count];float total=0;
   for(int row=0;row<count;row++){weights[row]=.76f+.48f*(.5f+.5f*Mathf.Sin(seed*2.17f+row*3.79f));total+=weights[row];}
   float bottom=-scale.y*.5f;
   for(int row=0;row<count;row++){
    float step=scale.y*weights[row]/total;float center=bottom+step*.5f;bottom+=step;
    var p=position+rotation*new Vector3(Mathf.Sin(seed+row*4.1f)*.009f,center,Mathf.Cos(seed*1.9f+row*2.6f)*.008f);
    if(p.y+step*.5f< -12)continue;
    var sc=new Vector3(scale.x*(1+Mathf.Sin(row*5.3f+seed)*.018f),step-.012f,scale.z*(1+Mathf.Cos(row*3.7f+seed)*.018f));
    var courseColor=color*(.96f+.06f*Mathf.Abs(Mathf.Sin(row*3.2f+seed)));
    bool split=(row+seed)%3==0&&Mathf.Max(sc.x,sc.z)>.85f;
    if(split){
     bool alongX=sc.x>=sc.z;float width=alongX?sc.x:sc.z;float first=width*(.40f+.17f*(.5f+.5f*Mathf.Sin(seed+row)));float second=width-first;const float gap=.015f;
     var a=sc;var b=sc;if(alongX){a.x=first-gap*.5f;b.x=second-gap*.5f;}else{a.z=first-gap*.5f;b.z=second-gap*.5f;}
     var axis=alongX?Vector3.right:Vector3.forward;
     AddColoredMesh(facadeCourses[(row+seed)%2],p+rotation*(axis*(-width*.5f+first*.5f)),rotation,a,courseColor,temp,instances);
     AddColoredMesh(facadeCourses[(row+seed+1)%2],p+rotation*(axis*(width*.5f-second*.5f)),rotation,b,courseColor*.98f,temp,instances);facadeCourseCount+=2;
    }else{AddColoredMesh(facadeCourses[(row+seed)%2],p,rotation,sc,courseColor,temp,instances);facadeCourseCount++;}
   }return;
  }
  if(!floor&&Mathf.Min(scale.x,Mathf.Min(scale.y,scale.z))>.12f&&Mathf.Max(scale.x,Mathf.Max(scale.y,scale.z))<2.8f)source=architecture[seed%6];
  if(localOverride)source=localOverride;
  AddColoredMesh(source,position,rotation,scale,color,temp,instances);
 }
 [Serializable]class StairRemoval:Instance { public string nodeId,geometry,materialId,kind;public int instanceIndex; }
 [Serializable]class StairManifest { public string bridge_sha256;public StairRemoval[] instances; }
 [Serializable]class ContactManifest {public string bridge_sha256;public StairRemoval[] instances,retained_instances;}
 static HashSet<Instance> ReadContactRemovals(Bridge bridge){
  var manifest=JsonUtility.FromJson<ContactManifest>(File.ReadAllText("../../Migration/Source/AtmosphereV2/ContactV14/rubble-removal-manifest.json"));
  using(var hash=System.Security.Cryptography.SHA256.Create())if(BitConverter.ToString(hash.ComputeHash(File.ReadAllBytes("Assets/Vesper/Import/unity-scene.json"))).Replace("-","").ToLowerInvariant()!=manifest.bridge_sha256)throw new Exception("Contact bridge drift");
  var removals=new HashSet<Instance>();var all=new HashSet<Instance>();
  foreach(var row in manifest.instances.Concat(manifest.retained_instances)){
   var node=bridge.nodes.Single(n=>n.id==row.nodeId);
   if(node.geometry!=row.geometry||node.materials[0]!=row.materialId||row.instanceIndex<0||row.instanceIndex>=node.instances.Length)throw new Exception("Contact source identity drift");
   var original=node.instances[row.instanceIndex];
   if(!original.position.SequenceEqual(row.position)||!original.quaternion.SequenceEqual(row.quaternion)||!original.scale.SequenceEqual(row.scale)||!original.color.SequenceEqual(row.color)||!all.Add(original))throw new Exception("Contact source transform/color/duplicate drift");
   if(Array.IndexOf(manifest.instances,row)>=0)removals.Add(original);
  }
  if(removals.Count!=50||manifest.retained_instances.Length!=49||all.Count!=99)throw new Exception("Contact removal count drift");return removals;
 }
 [Serializable]class LocalFracture:Instance {public string nodeId,geometry,materialId,replacement;public int instanceIndex,sourceVariant;}
 [Serializable]class LocalFractures {public string bridge_sha256;public LocalFracture[] overrides;}
 static Dictionary<Instance,Mesh> ReadLocalFractures(Bridge bridge){
  var result=new Dictionary<Instance,Mesh>();
  foreach(var package in new[]{new[]{"MasonryV13","architecture-overrides.json"},new[]{"MasonryV16","hero-overrides.json"}}){
  string folder="../../Migration/Source/AtmosphereV2/"+package[0]+"/";
  var manifest=JsonUtility.FromJson<LocalFractures>(File.ReadAllText(folder+package[1]));
  using(var hash=System.Security.Cryptography.SHA256.Create())if(BitConverter.ToString(hash.ComputeHash(File.ReadAllBytes("Assets/Vesper/Import/unity-scene.json"))).Replace("-","").ToLowerInvariant()!=manifest.bridge_sha256)throw new Exception("Local fracture bridge drift");
  if(manifest.overrides.Length!=8)throw new Exception("Expected eight fractures in "+package[0]);
  foreach(var row in manifest.overrides){var node=bridge.nodes.Single(n=>n.id==row.nodeId);var original=node.instances[row.instanceIndex];
   if(node.geometry!=row.geometry||node.materials[0]!=row.materialId||!original.position.SequenceEqual(row.position)||!original.quaternion.SequenceEqual(row.quaternion)||!original.scale.SequenceEqual(row.scale)||!original.color.SequenceEqual(row.color))throw new Exception("Local fracture instance drift");
   int selectedIndex=Array.IndexOf(node.instances.Where(i=>i.position[0]>=-10&&i.position[0]<=10&&i.position[2]>=-13&&i.position[2]<=22&&i.position[1]>=-3&&i.position[1]<=15).ToArray(),original);
   if(selectedIndex<0||(selectedIndex+(selectedIndex/100)*7)%6!=row.sourceVariant)throw new Exception("Local fracture V12 variant drift");
   result.Add(original,ReadNativeMesh(folder+row.replacement,"Selective masonry fracture "+package[0]));
  }}if(result.Count!=16)throw new Exception("Expected sixteen distinct local fractures");return result;
 }
 static HashSet<Instance> ReadFacadeRemovals(Bridge bridge){
  var manifest=JsonUtility.FromJson<StairManifest>(File.ReadAllText("../../Migration/Source/AtmosphereV2/MasonryV16/facade-removal-manifest.json"));
  using(var hash=System.Security.Cryptography.SHA256.Create())if(BitConverter.ToString(hash.ComputeHash(File.ReadAllBytes("Assets/Vesper/Import/unity-scene.json"))).Replace("-","").ToLowerInvariant()!=manifest.bridge_sha256)throw new Exception("Facade bridge drift");
  var result=new HashSet<Instance>();
  foreach(var row in manifest.instances){var node=bridge.nodes.Single(n=>n.id==row.nodeId);
   if(node.geometry!=row.geometry||node.materials[0]!=row.materialId||row.instanceIndex<0||row.instanceIndex>=node.instances.Length)throw new Exception("Facade source identity drift");
   var original=node.instances[row.instanceIndex];
   if(!original.position.SequenceEqual(row.position)||!original.quaternion.SequenceEqual(row.quaternion)||!original.scale.SequenceEqual(row.scale)||!original.color.SequenceEqual(row.color)||!result.Add(original))throw new Exception("Facade transform/color/duplicate drift");
  }if(result.Count!=63)throw new Exception("Expected63 facade skin removals");return result;
 }
 static HashSet<Instance> ReadStairRemovals(Bridge bridge){
  var manifest=JsonUtility.FromJson<StairManifest>(File.ReadAllText("../../Migration/Source/AtmosphereV2/MasonryV11/stair-removal-manifest.json"));
  using(var hash=System.Security.Cryptography.SHA256.Create()){
   string actual=BitConverter.ToString(hash.ComputeHash(File.ReadAllBytes("Assets/Vesper/Import/unity-scene.json"))).Replace("-","").ToLowerInvariant();
   if(actual!=manifest.bridge_sha256)throw new Exception("Stair replacement bridge hash mismatch");
  }
  var removals=new HashSet<Instance>();
  foreach(var row in manifest.instances){
   var node=bridge.nodes.Single(n=>n.id==row.nodeId);
   if(node.geometry!=row.geometry||node.materials[0]!=row.materialId||row.instanceIndex<0||row.instanceIndex>=node.instances.Length)throw new Exception("Stair replacement source identity drift");
   var original=node.instances[row.instanceIndex];
   if(!original.position.SequenceEqual(row.position)||!original.quaternion.SequenceEqual(row.quaternion)||!original.scale.SequenceEqual(row.scale)||!original.color.SequenceEqual(row.color)||!removals.Add(original))throw new Exception("Stair replacement transform/color/duplicate drift");
  }
  if(removals.Count!=278||manifest.instances.Count(r=>r.kind=="riser")!=90||manifest.instances.Count(r=>r.kind=="tread")!=90||manifest.instances.Count(r=>r.kind=="lip")!=98)throw new Exception("Stair replacement count drift");
  return removals;
 }
 static void InstallStone(){
  var bridge=JsonUtility.FromJson<Bridge>(File.ReadAllText("Assets/Vesper/Import/unity-scene.json"));var removals=ReadStairRemovals(bridge);var contactRemovals=ReadContactRemovals(bridge);var facadeRemovals=ReadFacadeRemovals(bridge);var fractures=ReadLocalFractures(bridge);var filters=UnityEngine.Object.FindObjectsByType<MeshFilter>();int replaced=0,groundRemoved=0,stairRemoved=0,fractureCount=0,contactRemoved=0,facadeRemoved=0;
  foreach(var node in bridge.nodes){string input="../../Migration/Source/AtmosphereV2/StoneV7/runtime/"+node.geometry+".json";if(node.distant||node.instances.Length==0||!File.Exists(input))continue;
   var source=ReadNativeMesh(input,"Worn stone V7");var selected=node.instances.Where(i=>i.position[0]>=-10&&i.position[0]<=10&&i.position[2]>=-13&&i.position[2]<=22&&i.position[1]>=-3&&i.position[1]<=15).ToArray();bool floor=node.materials[0]=="1ba07011-f8c4-4d07-9550-6d031350c67f",trim=node.materials[0]=="f07c4b31-f38a-44bb-bd4f-1a92d5329f38";int chunk=0;
   foreach(var group in selected.Select((i,index)=>new{i,index}).GroupBy(x=>x.index/100)){
    var filter=filters.FirstOrDefault(f=>AssetDatabase.GetAssetPath(f.sharedMesh).EndsWith("batch-"+node.id+"-"+chunk+".asset"));if(!filter){chunk++;continue;}
    var temp=new List<Mesh>();var instances=new List<CombineInstance>();foreach(var item in group){if(facadeRemovals.Contains(item.i)){facadeRemoved++;continue;}if(contactRemovals.Contains(item.i)){contactRemoved++;continue;}if(removals.Contains(item.i)){stairRemoved++;continue;}if(floor&&item.i.position[1]<.2f){groundRemoved++;continue;}fractures.TryGetValue(item.i,out var local);if(local)fractureCount++;AppendStone(item.i,source,floor,trim,item.index+chunk*7,temp,instances,local);}
    var merged=new Mesh{indexFormat=IndexFormat.UInt32,name="Varied masonry and worn floor"};if(instances.Count>0)merged.CombineMeshes(instances.ToArray());filter.sharedMesh=Save(merged,Root+"/Meshes/batch-"+node.id+"-"+chunk+".asset");if(floor)filter.gameObject.layer=29;foreach(var mesh in temp)UnityEngine.Object.DestroyImmediate(mesh);chunk++;replaced++;
   }UnityEngine.Object.DestroyImmediate(source);
  }if(facadeRemoved!=54)throw new Exception("Visible facade skin removal drift: "+facadeRemoved);Debug.Log("VESPER_FACADE_SKINS_VISIBLE_REMOVED "+facadeRemoved);foreach(var mesh in fractures.Values)UnityEngine.Object.DestroyImmediate(mesh);if(contactRemoved!=50)throw new Exception("Contact removal application drift: "+contactRemoved);Debug.Log("VESPER_CONTACT_OFFCUTS_REMOVED "+contactRemoved);if(fractureCount!=16)throw new Exception("Local fracture application drift: "+fractureCount);Debug.Log("VESPER_LOCAL_FRACTURES "+fractureCount);if(groundRemoved!=430)throw new Exception("Ground replacement selection drift: "+groundRemoved);if(stairRemoved!=278)throw new Exception("Stair replacement selection drift: "+stairRemoved);Debug.Log("VESPER_STAIR_PARTS_REMOVED "+stairRemoved);Debug.Log("VESPER_GROUND_REMOVED "+groundRemoved);Debug.Log("VESPER_STONE_BATCHES_REPLACED "+replaced);
 }
 static void InstallContact(){
  foreach(string part in new[]{"rubble","deposits"}){
   var mesh=Save(ReadNativeMesh("../../Migration/Source/AtmosphereV2/ContactV14/contact-v14-"+part+".json","Root and parapet contact "+part),Root+"/Meshes/ContactV14-"+part+".asset");
   var material=new Material(AssetDatabase.LoadAssetAtPath<Material>(Root+"/Materials/08b6ee59-7da1-4fb0-bd5d-a752d5b8fa60.mat"));
   material.SetFloat("_WaterLayer",0);material.DisableKeyword("_SEPARATE_WATER");material.SetFloat("_ReflectionStrength",0);material.SetFloat("_Wetness",part=="deposits"?.18f:.35f);material.SetFloat("_RainWetness",part=="deposits"?0:.35f);OpaqueStone(material);
   material=Save(material,Root+"/Materials/ContactV14-"+part+".mat");
   var go=new GameObject("Authored contact "+part+" V14");go.AddComponent<MeshFilter>().sharedMesh=mesh;go.AddComponent<MeshRenderer>().sharedMaterial=material;
   Debug.Log("VESPER_CONTACT_V14_"+part.ToUpperInvariant()+"_TRIANGLES "+mesh.triangles.Length/3);
  }
 }
 static void InstallFacade(){
  var mesh=Save(ReadNativeMesh("../../Migration/Source/AtmosphereV2/MasonryV16/facade-v16-mesh.json","Interlocking facade bond V16"),Root+"/Meshes/FacadeV16.asset");
  var material=new Material(AssetDatabase.LoadAssetAtPath<Material>(Root+"/Materials/08b6ee59-7da1-4fb0-bd5d-a752d5b8fa60.mat"));
  material.SetFloat("_WaterLayer",0);material.DisableKeyword("_SEPARATE_WATER");material.SetFloat("_ReflectionStrength",0);OpaqueStone(material);
  material=Save(material,Root+"/Materials/FacadeV16.mat");
  var go=new GameObject("Interlocking facade bond V16");go.AddComponent<MeshFilter>().sharedMesh=mesh;go.AddComponent<MeshRenderer>().sharedMaterial=material;
  Debug.Log("VESPER_FACADE_V16_TRIANGLES "+mesh.triangles.Length/3);
 }
 static void OpaqueStone(Material material){material.SetFloat("_SrcBlend",(float)BlendMode.One);material.SetFloat("_DstBlend",(float)BlendMode.Zero);}
 static void InstallStairs(){
  var mesh=Save(ReadNativeMesh("../../Migration/Source/AtmosphereV2/MasonryV16/stairs-v16-mesh.json","Layered fracture stair stones V16"),Root+"/Meshes/StairsV16.asset");
  var material=new Material(AssetDatabase.LoadAssetAtPath<Material>(Root+"/Materials/08b6ee59-7da1-4fb0-bd5d-a752d5b8fa60.mat"));
  material.name="Integrated stair stone";material.SetColor("_BaseColor",new Color(.35f,.38f,.40f,1));material.SetFloat("_Wetness",.35f);material.SetFloat("_WaterLayer",0);material.DisableKeyword("_SEPARATE_WATER");material.SetFloat("_ReflectionStrength",0);
  OpaqueStone(material);material=Save(material,Root+"/Materials/StairsV16.mat");
  var go=new GameObject("Layered fracture stair stones V16");go.AddComponent<MeshFilter>().sharedMesh=mesh;go.AddComponent<MeshRenderer>().sharedMaterial=material;
  Debug.Log("VESPER_STAIRS_V16_TRIANGLES "+mesh.triangles.Length/3);
 }
 static void InstallPaving(){
  const string source="../../Migration/Source/AtmosphereV2/PavingV11/";
  var mesh=Save(ReadNativeMesh("../../Migration/Source/AtmosphereV2/PavingV17/paving-v17-mesh.json","Expanded lithic fracture paving V17"),Root+"/Meshes/PavingV17.asset");
  var material=new Material(AssetDatabase.LoadAssetAtPath<Material>(Root+"/Materials/1ba07011-f8c4-4d07-9550-6d031350c67f.mat"));material.name="Photogrammetric courtyard stonebed";
  material.SetTexture("_DetailMap",ImportMeasuredTexture(source+"maps/Tiles130_4K-PNG_Color.png","PavingV11-color.png",false,true));
  material.SetTexture("_DetailNormal",ImportMeasuredTexture(source+"maps/Tiles130_4K-PNG_NormalGL.png","PavingV11-normal.png",true,false));
  material.SetTexture("_MicroNormal",AssetDatabase.LoadAssetAtPath<Texture2D>(Root+"/Textures/rock_05_nor_gl_2k.png"));
  material.SetTexture("_MicroRoughness",AssetDatabase.LoadAssetAtPath<Texture2D>(Root+"/Textures/rock_05_rough_2k.png"));
  material.SetTexture("_MineralColor",AssetDatabase.LoadAssetAtPath<Texture2D>(Root+"/Textures/rock_05_diff_2k.png"));
  material.SetFloat("_MineralScale",1f/2.4f);material.SetFloat("_MineralColorStrength",.65f);material.SetVector("_MineralNormalCenter",new Vector4(.116f,.120f,0,0));
  material.SetTexture("_RoughnessMap",ImportMeasuredTexture(source+"maps/Tiles130_4K-PNG_Roughness.png","PavingV11-roughness.png",false,false));
  material.SetTexture("_StoneAO",ImportMeasuredTexture(source+"maps/Tiles130_4K-PNG_AmbientOcclusion.png","PavingV11-ao.png",false,false));
  material.EnableKeyword("_AUTHORED_STONE_UV");material.EnableKeyword("_PHOTOGRAPHIC_STONE");material.EnableKeyword("_SEPARATE_WATER");material.SetFloat("_Photographic",1);material.SetFloat("_WaterLayer",1);material.SetFloat("_BumpScale",1);material.SetFloat("_PatinaStrength",0);material.SetFloat("_ReflectionStrength",0);material.SetFloat("_RainWetness",0);
  material.SetColor("_BaseColor",material.GetColor("_BaseColor")*.78f);
  OpaqueStone(material);material=Save(material,Root+"/Materials/PavingV17.mat");
  var go=new GameObject("Expanded lithic fracture courtyard paving V17");go.layer=29;
  go.AddComponent<MeshFilter>().sharedMesh=mesh;
  go.AddComponent<MeshRenderer>().sharedMaterial=material;
  Debug.Log("VESPER_PAVING_V17_TRIANGLES "+mesh.triangles.Length/3);
 }
 static void InstallTree(){
  const string source="../../Migration/Source/AtmosphereV2/TreeV11/";
  var mesh=Save(ReadNativeMesh("../../Migration/Source/AtmosphereV2/TreeV16/tree-v16-mesh.json","Buried root envelopes and tapered forks V16"),Root+"/Meshes/TreeV16.asset");
  var material=new Material(Shader.Find("Universal Render Pipeline/Lit"));material.name="TreeV11 measured PBR";
  material.SetTexture("_BaseMap",ImportMeasuredTexture(source+"texture-0-base_color.png","TreeV11-color.png",false,true));
  material.SetTexture("_BumpMap",ImportMeasuredTexture(source+"texture-0-normal.png","TreeV11-normal.png",true,false));
  material.SetTexture("_MetallicGlossMap",PackTreeSmoothness(source+"texture-0-roughness.png"));
  material.SetColor("_BaseColor",new Color(.80f,.80f,.80f,1));material.SetFloat("_Metallic",0);material.SetFloat("_Smoothness",.28f);material.SetFloat("_BumpScale",1);
  material.EnableKeyword("_NORMALMAP");material.EnableKeyword("_METALLICSPECGLOSSMAP");material=Save(material,Root+"/Materials/TreeV11.mat");
  var go=GameObject.Find("Sculpted_bark_roots_and_fine_branches");go.GetComponent<MeshFilter>().sharedMesh=mesh;go.GetComponent<MeshRenderer>().sharedMaterial=material;
  // Keep the inherited tree parent placement/scale. Face the broad crown toward
  // the middle of the supported camera arc; strict side collapse is documented.
  go.transform.localRotation=Quaternion.Euler(0,-20,0);
  VesperNavigationBuild.InstallRootBoundary(go,mesh);
  foreach(string part in new[]{"covers","soil"}){
   var contact=Save(ReadNativeMesh("../../Migration/Source/AtmosphereV2/TreeV16/tree-v16-"+part+".json","TreeV16 root entry "+part),Root+"/Meshes/TreeV16-"+part+".asset");
   var surface=new Material(AssetDatabase.LoadAssetAtPath<Material>(Root+"/Materials/08b6ee59-7da1-4fb0-bd5d-a752d5b8fa60.mat"));
   surface.SetFloat("_WaterLayer",0);surface.DisableKeyword("_SEPARATE_WATER");surface.SetFloat("_ReflectionStrength",0);surface.SetFloat("_Wetness",part=="soil"?.18f:.35f);surface.SetFloat("_RainWetness",part=="soil"?0:.35f);OpaqueStone(surface);
   surface=Save(surface,Root+"/Materials/TreeV16-"+part+".mat");
   var entry=new GameObject("TreeV16 root entry "+part);entry.AddComponent<MeshFilter>().sharedMesh=contact;entry.AddComponent<MeshRenderer>().sharedMaterial=surface;
   Debug.Log("VESPER_TREE_V16_"+part.ToUpperInvariant()+"_TRIANGLES "+contact.triangles.Length/3);
  }
  Debug.Log("VESPER_TREE_V16_TRIANGLES "+mesh.triangles.Length/3);
 }
 static Texture2D ImportMeasuredTexture(string source,string filename,bool normal,bool srgb,int size=4096){
  string destination=Root+"/Textures/"+filename;
  if(!File.Exists(source))throw new FileNotFoundException("Required measured asset map missing",source);
  File.Copy(source,destination,true);AssetDatabase.ImportAsset(destination,ImportAssetOptions.ForceUpdate);
  var importer=(TextureImporter)AssetImporter.GetAtPath(destination);importer.textureType=normal?TextureImporterType.NormalMap:TextureImporterType.Default;
  importer.sRGBTexture=srgb;importer.wrapMode=TextureWrapMode.Repeat;importer.anisoLevel=8;importer.maxTextureSize=size;importer.textureCompression=TextureImporterCompression.Uncompressed;importer.SaveAndReimport();
  return AssetDatabase.LoadAssetAtPath<Texture2D>(destination);
 }
 // Generated PBR textures remain unchanged in Source. This derivative only packs
 // linear roughness into the alpha convention required by URP/Lit.
 static Texture2D PackTreeSmoothness(string source){
  var input=new Texture2D(2,2,TextureFormat.RGBA32,false,true);if(!ImageConversion.LoadImage(input,File.ReadAllBytes(source),false))throw new Exception("Tree roughness PNG decode failed");
  var pixels=input.GetPixels32();for(int i=0;i<pixels.Length;i++)pixels[i]=new Color32(0,0,0,(byte)(255-pixels[i].r));
  var packed=new Texture2D(input.width,input.height,TextureFormat.RGBA32,false,true);packed.SetPixels32(pixels);packed.Apply();string path=Root+"/Textures/TreeV11-metal-smooth.png";File.WriteAllBytes(path,ImageConversion.EncodeToPNG(packed));UnityEngine.Object.DestroyImmediate(input);UnityEngine.Object.DestroyImmediate(packed);
  AssetDatabase.ImportAsset(path,ImportAssetOptions.ForceUpdate);var importer=(TextureImporter)AssetImporter.GetAtPath(path);importer.sRGBTexture=false;importer.maxTextureSize=4096;importer.textureCompression=TextureImporterCompression.Uncompressed;importer.SaveAndReimport();return AssetDatabase.LoadAssetAtPath<Texture2D>(path);
 }
 static void RestoreFoundations(){
  Folder(Root+"/Meshes");var bridge=JsonUtility.FromJson<Bridge>(File.ReadAllText("Assets/Vesper/Import/unity-scene.json"));var facadeRemovals=ReadFacadeRemovals(bridge);int count=0,facadeRemoved=0;
  foreach(var n in bridge.nodes){if(n.distant||n.instances.Length==0)continue;var omitted=n.instances.Where(i=>!(i.position[0]>=-10&&i.position[0]<=10&&i.position[2]>=-13&&i.position[2]<=22&&i.position[1]>=-3&&i.position[1]<=15)).ToArray();if(omitted.Length==0)continue;
   var source=AssetDatabase.LoadAssetAtPath<Mesh>("Assets/Vesper/Generated/Meshes/"+n.geometry+".asset");var temp=new List<Mesh>();var instances=new List<CombineInstance>();for(int k=0;k<omitted.Length;k++){if(facadeRemovals.Contains(omitted[k])){facadeRemoved++;continue;}AppendStone(omitted[k],source,false,false,k,temp,instances);}
   var combined=new Mesh{indexFormat=IndexFormat.UInt32};combined.CombineMeshes(instances.ToArray());combined=Save(combined,Root+"/Meshes/Foundation-"+n.id+".asset");foreach(var m in temp)UnityEngine.Object.DestroyImmediate(m);var go=new GameObject("Restored deep foundation "+n.id);go.AddComponent<MeshFilter>().sharedMesh=combined;var r=go.AddComponent<MeshRenderer>();r.sharedMaterial=AssetDatabase.LoadAssetAtPath<Material>(Root+"/Materials/"+n.materials[0]+".mat");r.shadowCastingMode=ShadowCastingMode.Off;count+=omitted.Length;
  }if(facadeRemoved!=9)throw new Exception("Deep facade skin removal drift: "+facadeRemoved);Debug.Log("VESPER_FACADE_SKINS_DEEP_REMOVED "+facadeRemoved);Debug.Log("VESPER_RESTORED_FOUNDATION_SELECTIONS "+count);
 }
 static void BuildSky(){
  string path=Root+"/Textures/moon-cloud-environment.png";AssetDatabase.ImportAsset(path);var importer=(TextureImporter)AssetImporter.GetAtPath(path);importer.sRGBTexture=true;importer.isReadable=true;importer.wrapMode=TextureWrapMode.Repeat;importer.textureCompression=TextureImporterCompression.Uncompressed;importer.SaveAndReimport();
  var panorama=AssetDatabase.LoadAssetAtPath<Texture2D>(path);const int size=256;
  var cube=new Cubemap(size,TextureFormat.RGBAHalf,true);cube.name="Photographic moon cloud environment";
  for(int face=0;face<6;face++){var pixels=new Color[size*size];for(int y=0;y<size;y++)for(int x=0;x<size;x++){
   float u=(x+.5f)*2/size-1,v=(y+.5f)*2/size-1;
   Vector3 d=face==0?new Vector3(1,-v,-u):face==1?new Vector3(-1,-v,u):face==2?new Vector3(u,1,v):face==3?new Vector3(u,-1,-v):face==4?new Vector3(u,-v,1):new Vector3(-u,-v,-1);d.Normalize();
   float longitude=Mathf.Atan2(d.z,d.x)/(Mathf.PI*2)+.5f,latitude=Mathf.Asin(d.y)/Mathf.PI+.5f;
   Color c=panorama.GetPixelBilinear(longitude,latitude).linear*1.5f;float gray=c.grayscale;c=Color.Lerp(c,new Color(gray,gray,gray),.45f);c.a=1;pixels[y*size+x]=c;
  }cube.SetPixels(pixels,(CubemapFace)face);}cube.Apply(true,false);cube=Save(cube,Root+"/Settings/MoonCloudEnvironmentV2.asset");RenderSettings.defaultReflectionMode=DefaultReflectionMode.Custom;var ambient=new Cubemap(size,TextureFormat.RGBAHalf,true);ambient.name="Overcast stone illumination";
  for(int face=0;face<6;face++){var pixels=cube.GetPixels((CubemapFace)face);for(int k=0;k<pixels.Length;k++){float light=Mathf.Min(.4f,pixels[k].grayscale);pixels[k]=new Color(.028f+light*.018f,.05f+light*.026f,.073f+light*.034f,1);}ambient.SetPixels(pixels,(CubemapFace)face);}ambient.Apply(true,false);
  RenderSettings.customReflectionTexture=Save(ambient,Root+"/Settings/OvercastStoneEnvironment.asset");RenderSettings.reflectionIntensity=1;
  var sky=new Material(Shader.Find("Vesper/ReflectionSky"));sky.SetTexture("_Tex",cube);RenderSettings.skybox=Save(sky,Root+"/Materials/CloudReflectionSky.mat");
  var waterSky=new Material(Shader.Find("Vesper/ReflectionSky"));waterSky.SetTexture("_Tex",RenderSettings.customReflectionTexture);waterSky.SetFloat("_DirectEnvironment",1);
  UnityEngine.Object.FindAnyObjectByType<VesperPlanarReflection>().reflectedSkybox=Save(waterSky,Root+"/Materials/SharedOvercastReflectionSky.mat");
 }
 public static void BuildAndCapture(){Build();VesperAtmosphereCapture.Run();}
}
}
