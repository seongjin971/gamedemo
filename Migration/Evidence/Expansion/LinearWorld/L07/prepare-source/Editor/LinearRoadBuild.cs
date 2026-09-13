using System;
using System.IO;
using System.Linq;
using System.Text;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.AI;
using UnityEngine.Rendering;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEditor.Build.Reporting;
using UnityEngine.SceneManagement;

namespace Vesper.Expansion.LinearWorld.Editor {
// Additive road-only package. It never invokes the original scene or art generators.
public static class LinearRoadBuild {
 const string Root="Assets/Vesper/Expansion/LinearWorld";
 const string BaselineScene="Assets/Vesper/Scenes/Expansion/VesperLinearWorld_L06.unity";
 static string Revision=>LinearBuild.Arg("-roadRevision","L07");
 static string Evidence(string revision)=>Path.GetFullPath("../../Migration/Evidence/Expansion/LinearWorld/"+revision);
 static string ScenePath=>"Assets/Vesper/Scenes/Expansion/VesperLinearWorld_"+Revision+".unity";
 static string AssetPath(UnityEngine.Object o)=>o?AssetDatabase.GetAssetPath(o):"NULL";
 static string Hierarchy(Transform t)=>t.parent?Hierarchy(t.parent)+"/"+t.name:t.name;
 static string Pose(Transform t)=>Hierarchy(t)+"|"+t.position.ToString("F5")+"|"+t.rotation.ToString("F5")+"|"+t.lossyScale.ToString("F5")+"|"+t.gameObject.activeSelf+"|"+t.gameObject.layer;
 static T[] All<T>(Scene s) where T:Component=>s.GetRootGameObjects().SelectMany(g=>g.GetComponentsInChildren<T>(true)).ToArray();
 static bool Under(Transform t,Transform[] roots)=>roots.Any(r=>t==r||t.IsChildOf(r));
 static string VisualStamp(Scene s,Transform[] excluded)=>string.Join("\n",All<Renderer>(s).Where(r=>!Under(r.transform,excluded)).Select(r=>Pose(r.transform)+"|"+r.enabled+"|"+r.shadowCastingMode+"|"+string.Join(";",r.sharedMaterials.Select(AssetPath))).OrderBy(x=>x));
 static string CollisionStamp(Scene s)=>string.Join("\n",All<Collider>(s).Select(c=>Pose(c.transform)+"|"+c.GetType().FullName+"|"+c.enabled+"|"+c.isTrigger+"|"+c.bounds.ToString("F5")+"|"+(c is MeshCollider m?AssetPath(m.sharedMesh):JsonUtility.ToJson(c))).OrderBy(x=>x));
 [Serializable]class PrepareReport {public string revision,sourceScene;public int removedPathModules,colliders,audioSources;public bool outsideRenderersUnchanged,collidersUnchanged;public string[] routes;}
 static Texture2D ExistingTexture(string p){var t=AssetDatabase.LoadAssetAtPath<Texture2D>(p);if(!t)throw new Exception("Missing texture "+p);return t;}
 static Texture2D RoadTexture(string name){string p=Root+"/Art/RoadR01/"+name+".png";var importer=AssetImporter.GetAtPath(p) as TextureImporter;if(!importer)throw new Exception("Missing new road texture "+p);importer.wrapMode=TextureWrapMode.Repeat;importer.filterMode=FilterMode.Trilinear;importer.anisoLevel=8;importer.maxTextureSize=2048;importer.sRGBTexture=true;importer.textureCompression=TextureImporterCompression.CompressedHQ;importer.SaveAndReimport();return ExistingTexture(p);}
 public static void Prepare(){try{
  string folder=Root+"/Generated/"+Revision;Directory.CreateDirectory(Evidence(Revision));
  if(File.Exists(ScenePath)||Directory.Exists(folder))throw new Exception("Refuse existing road candidate "+Revision);
  Directory.CreateDirectory(folder);AssetDatabase.Refresh();
  var scene=EditorSceneManager.OpenScene(BaselineScene);EditorSceneManager.SaveScene(scene,ScenePath,false);
  var old=All<Transform>(scene).Where(t=>t.parent&&t.parent.name=="Authored linear landscape"&&Mathf.Abs(t.position.x)<.05f&&(t.name.StartsWith("L02Details/LinearPaving_")||t.name.StartsWith("L04Details/LinearIrregular_"))).ToArray();
  if(old.Length<30)throw new Exception("Unexpected baseline path module count "+old.Length);
  if(old.Any(t=>t.GetComponentsInChildren<Collider>(true).Length>0))throw new Exception("Road replacement would remove a collider");
  Physics.SyncTransforms();string beforeVisual=VisualStamp(scene,old),beforeCollision=CollisionStamp(scene);
  foreach(var t in old)UnityEngine.Object.DestroyImmediate(t.gameObject);
  // A unique shader asset locks each candidate's appearance even after later template edits.
  string template=File.ReadAllText(Root+"/RoadBlend.shader");string shaderPath=folder+"/RoadSurface.shader";
  File.WriteAllText(shaderPath,template.Replace("Vesper/Linear/RoadBlendTemplate","Vesper/Linear/Road/"+Revision));AssetDatabase.ImportAsset(shaderPath,ImportAssetOptions.ForceSynchronousImport);
  var shader=AssetDatabase.LoadAssetAtPath<Shader>(shaderPath);if(!shader)throw new Exception("Road shader missing");
  var mat=new Material(shader){name="Continuous earth stone mud and snow"};
  mat.SetTexture("_DirtMap",RoadTexture("DryTrail"));mat.SetTexture("_MudMap",RoadTexture("RainMud"));mat.SetTexture("_TrailStoneMap",RoadTexture("BuriedStone"));mat.SetTexture("_SlushMap",RoadTexture("SlushTrail"));
  const string art="Assets/Vesper/Expansion/ContinuousWorld/Art/";
  mat.SetTexture("_SnowMap",ExistingTexture(art+"Textures/SnowSurface.png"));mat.SetTexture("_PackedMap",ExistingTexture(art+"Textures/MaterialTexturesV2/PackedAlpineSnow.png"));
  AssetDatabase.CreateAsset(mat,folder+"/ContinuousRoad.mat");
  var road=new GameObject("Climate-blended walking surface");
  int serial=0;foreach(var segment in new[]{new Vector2(-14,17.95f),new Vector2(32.05f,314)})for(float d=segment.x;d<segment.y;d+=24)Ribbon(road.transform,d,Mathf.Min(d+24,segment.y),mat,folder,serial++);
  Physics.SyncTransforms();bool visuals=beforeVisual==VisualStamp(scene,new[]{road.transform}),colliders=beforeCollision==CollisionStamp(scene);
  if(!visuals||!colliders)throw new Exception("Preserved scenery/collision changed unexpectedly");
  var routes=new List<string>();var nav=new NavMeshPath();for(int i=1;i<WorldLayout.Bends.Length;i++){var a=WorldLayout.Point(WorldLayout.Bends[i-1].y);var b=WorldLayout.Point(WorldLayout.Bends[i].y);routes.Add((NavMesh.CalculatePath(a,b,NavMesh.AllAreas,nav)&&nav.status==NavMeshPathStatus.PathComplete?"PASS ":"FAIL ")+a+" -> "+b);}
  AssetDatabase.SaveAssets();EditorSceneManager.SaveScene(scene);
  File.WriteAllText(Evidence(Revision)+"/prepare.json",JsonUtility.ToJson(new PrepareReport{revision=Revision,sourceScene=BaselineScene,removedPathModules=old.Length,outsideRenderersUnchanged=visuals,collidersUnchanged=colliders,colliders=All<Collider>(scene).Length,audioSources=All<AudioSource>(scene).Length,routes=routes.ToArray()},true));
  EditorApplication.Exit(routes.Any(r=>r.StartsWith("FAIL"))?2:0);
 }catch(Exception e){Debug.LogException(e);EditorApplication.Exit(1);}}
 static void Ribbon(Transform parent,float start,float end,Material mat,string folder,int serial){
  const int across=24;int length=Mathf.CeilToInt((end-start)/.4f);var vertices=new List<Vector3>();var normals=new List<Vector3>();var colors=new List<Color>();var tris=new List<int>();
  for(int j=0;j<=length;j++)for(int i=0;i<=across;i++){
   float d=Mathf.Lerp(start,end,(float)j/length),x=Mathf.Lerp(-3.2f,3.2f,(float)i/across);vertices.Add(new Vector3(x,WorldLayout.Height(x,d)+.025f,-d));
   float dx=(WorldLayout.Height(x+.08f,d)-WorldLayout.Height(x-.08f,d))/.16f,dz=(WorldLayout.Height(x,d-.08f)-WorldLayout.Height(x,d+.08f))/.16f;normals.Add(new Vector3(-dx,1,-dz).normalized);
   colors.Add(new Color(0,WorldLayout.SnowCover(x,d),0,1));
   if(i<across&&j<length){int k=j*(across+1)+i;tris.AddRange(new[]{k,k+1,k+across+1,k+1,k+across+2,k+across+1});}
  }
  var mesh=new Mesh{name="Conforming trail "+serial,indexFormat=IndexFormat.UInt32};mesh.SetVertices(vertices);mesh.SetNormals(normals);mesh.SetColors(colors);mesh.SetTriangles(tris,0);mesh.RecalculateBounds();AssetDatabase.CreateAsset(mesh,folder+"/Trail-"+serial+".asset");
  var g=new GameObject("Continuous trail "+serial);g.transform.SetParent(parent,false);g.AddComponent<MeshFilter>().sharedMesh=mesh;var r=g.AddComponent<MeshRenderer>();r.sharedMaterial=mat;r.shadowCastingMode=ShadowCastingMode.Off;r.receiveShadows=true;
 }
 [Serializable]class BuildReportData{public string result,path,scene;public int errors,warnings;public double seconds;public string[] messages;}
 static void BuildScene(string revision,string scene){try{
  string dir=Evidence(revision);Directory.CreateDirectory(dir);string path="Builds/VesperLinearWorld_"+revision+"/VesperLinear.exe";if(File.Exists(path))throw new Exception("Refuse existing build "+path);
  var r=BuildPipeline.BuildPlayer(new BuildPlayerOptions{scenes=new[]{scene},locationPathName=path,target=BuildTarget.StandaloneWindows64,options=BuildOptions.StrictMode});
  File.WriteAllText(dir+"/build.json",JsonUtility.ToJson(new BuildReportData{result=r.summary.result.ToString(),path=path,scene=scene,errors=(int)r.summary.totalErrors,warnings=(int)r.summary.totalWarnings,seconds=r.summary.totalTime.TotalSeconds,messages=r.steps.SelectMany(s=>s.messages).Where(m=>m.type==LogType.Error||m.type==LogType.Warning).Select(m=>m.content).ToArray()},true));EditorApplication.Exit(r.summary.result==BuildResult.Succeeded?0:1);
 }catch(Exception e){Debug.LogException(e);EditorApplication.Exit(1);}}
 public static void Build()=>BuildScene(Revision,ScenePath);
 public static void BuildBaseline()=>BuildScene("RoadBaseline",BaselineScene);
}
}
