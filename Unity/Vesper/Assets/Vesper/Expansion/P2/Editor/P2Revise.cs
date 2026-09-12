using UnityEngine;
using UnityEditor;
using UnityEditor.SceneManagement;
namespace Vesper.Expansion.P2.Editor {
public static class P2Revise {
 public static void Apply(){
  var scene=EditorSceneManager.OpenScene("Assets/Vesper/Scenes/Expansion/VesperP2.unity");
  const string root="Assets/Vesper/Expansion/P2/Generated/";
  var stone=AssetDatabase.LoadAssetAtPath<Material>(root+"Crossing slate.mat");
  var trim=AssetDatabase.LoadAssetAtPath<Material>(root+"Weathered coping.mat");
  var wood=AssetDatabase.LoadAssetAtPath<Material>(root+"Bridge timber.mat");
  var water=AssetDatabase.LoadAssetAtPath<Material>(root+"Blocked dark water.mat");
  var texture=new Texture2D(256,256,TextureFormat.RGBA32,true);texture.name="P2 mottled stone";texture.wrapMode=TextureWrapMode.Repeat;
  for(int y=0;y<256;y++)for(int x=0;x<256;x++){float n=.62f+.2f*Mathf.PerlinNoise(x*.043f,y*.043f)+.12f*Mathf.PerlinNoise(x*.23f,y*.23f);texture.SetPixel(x,y,new Color(n,n*.98f,n*.94f));}texture.Apply();AssetDatabase.CreateAsset(texture,root+"StoneGrain.asset");
  foreach(var m in new[]{stone,trim,wood,water}){m.SetFloat("_Smoothness",.12f);m.SetFloat("_SpecularHighlights",0);m.EnableKeyword("_SPECULARHIGHLIGHTS_OFF");m.SetFloat("_EnvironmentReflections",0);m.EnableKeyword("_ENVIRONMENTREFLECTIONS_OFF");EditorUtility.SetDirty(m);}
  stone.SetTexture("_BaseMap",texture);trim.SetTexture("_BaseMap",texture);wood.SetTexture("_BaseMap",texture);wood.SetTextureScale("_BaseMap",new Vector2(2,.15f));
  water.color=new Color(.045f,.11f,.14f);
  var world=Object.FindAnyObjectByType<P2World>();
  world.connectionGate=new Vector3(0,0,10.3f);
  // Shallow joints on the landing surfaces add scale without changing collision height.
  foreach(var landing in new[]{new Vector3(0,0,8.5f),new Vector3(0,1.6f,-8)}){
   for(int i=-3;i<=3;i++){var line=GameObject.CreatePrimitive(PrimitiveType.Cube);line.name="Landing stone joint";line.transform.SetParent(world.connection.transform,false);line.transform.position=landing+new Vector3(i,.003f,0);line.transform.localScale=new Vector3(.022f,.004f,4.7f);line.GetComponent<Renderer>().sharedMaterial=wood;Object.DestroyImmediate(line.GetComponent<Collider>());}
   for(int i=-2;i<=2;i++){var line=GameObject.CreatePrimitive(PrimitiveType.Cube);line.name="Landing course joint";line.transform.SetParent(world.connection.transform,false);line.transform.position=landing+new Vector3(0,.003f,i);line.transform.localScale=new Vector3(7.8f,.004f,.024f);line.GetComponent<Renderer>().sharedMaterial=wood;Object.DestroyImmediate(line.GetComponent<Collider>());}
  }
  AssetDatabase.SaveAssets();EditorSceneManager.SaveScene(scene);EditorApplication.Exit(0);
 }
}
}
