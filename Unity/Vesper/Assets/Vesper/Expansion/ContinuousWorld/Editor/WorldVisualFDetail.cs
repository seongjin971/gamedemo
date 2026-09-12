using System.IO;
using System.Linq;
using UnityEngine;
using UnityEditor;
using UnityEngine.Rendering.Universal;
namespace Vesper.Expansion.ContinuousWorld.Editor {
public static partial class WorldVisuals {
 static void ImportVisualFAssets() {
  var source=Path.GetFullPath("../../Migration/Source/Expansion/ContinuousWorld/VisualF");
  var dest=Art+"/EnvironmentKit/VisualF";Directory.CreateDirectory(dest);
  foreach(var folder in new[]{"FirVolume","DetailAssets"})foreach(var p in Directory.GetFiles(source+"/"+folder,"*.fbx")) {
   var target=dest+"/"+Path.GetFileName(p);if(!File.Exists(target))File.Copy(p,target);
   AssetDatabase.ImportAsset(target,ImportAssetOptions.ForceSynchronousImport);
  }
  var tex=source+"/LimestoneFineF.png";
  if(File.Exists(tex)) {var target=dest+"/LimestoneFineF.png";if(!File.Exists(target))File.Copy(tex,target);AssetDatabase.ImportAsset(target,ImportAssetOptions.ForceSynchronousImport);}
 }
 static void RefineVisualF(GameObject collision, WorldEnvironment world) {
  ImportVisualFAssets();
  var quality=Camera.main.GetUniversalAdditionalCameraData();quality.antialiasing=AntialiasingMode.SubpixelMorphologicalAntiAliasing;quality.antialiasingQuality=AntialiasingQuality.High;
  var fine=AssetDatabase.LoadAssetAtPath<Texture2D>(Art+"/EnvironmentKit/VisualF/LimestoneFineF.png");
  if(fine)fine=Texture(Art+"/EnvironmentKit/VisualF/LimestoneFineF.png");
  var abbey=GameObject.Find("Rainwood and roofless abbey").transform;
  // New large flagstones continue past the visible approach; no sudden rectangular carpet end.
  foreach(var t in abbey.Cast<Transform>().Where(t=>t.name.Contains("ChapelPaving")).ToArray())Object.DestroyImmediate(t.gameObject);
  int serial=0;
  for(float x=26;x<=38;x+=4)for(float d=168;d<=196;d+=4)
   Model(abbey,"VisualF/CW_BroadPaving_"+(1+(serial++%3)),new Vector3(x,9,-d),Vector3.one,(serial%2)*180);
  for(float d=154;d<=218;d+=4)foreach(float offset in new[]{-2f,2f}) {
   var go=Model(abbey,"VisualF/CW_BroadPaving_"+(1+(serial++%3)),WorldLayout.Point(d,offset)+Vector3.up*.008f,Vector3.one,0);
   ConformPaving(go,d,serial);
  }
  foreach(var m in materials.Values.ToArray()) {
   if(m.name.StartsWith("Wet_")) {m.shader=Shader.Find("Vesper/VisualF/WetStone");if(fine)m.SetTexture("_BaseMap",fine);m.SetColor("_BaseColor",m.name.Contains("Light")?new Color(.91f,.95f,.95f):new Color(.83f,.88f,.88f));m.SetFloat("_Wetness",.88f);m.SetFloat("_ReflectionStrength",.24f);}
   if(m.name.StartsWith("Abbey_CW_Chapel")&&fine&&!m.name.Contains("Mortar")) {m.SetTexture("_BaseMap",fine);m.SetTextureScale("_BaseMap",Vector2.one);m.SetTextureOffset("_BaseMap",Vector2.zero);m.color=m.name.Contains("Light")?new Color(.6f,.65f,.62f):new Color(.46f,.52f,.48f);}
   if(m.name.Contains("moss")||m.name=="Moss") {m.SetTexture("_BaseMap",Texture(Art+"/Textures/MossSurface.png"));m.SetTextureScale("_BaseMap",Vector2.one);m.SetTextureOffset("_BaseMap",Vector2.zero);m.color=new Color(.48f,.64f,.29f);}
   if(m.name=="Abbey fractured rubble") {if(fine)m.SetTexture("_BaseMap",fine);m.color=new Color(.51f,.56f,.51f);}
  }
  foreach(float d in new[]{171f,175f,191f,196f}) {
   var rubble=Model(abbey,"AbbeyRubbleV2/CW_AbbeyRubbleMound3m",new Vector3(23.6f,8.96f,-d),new Vector3(.9f,.75f,1.15f),d*17);
  }
  // Tie roof rafters to complete grounded frames. Raised framing is not floating architecture.
  foreach(var t in abbey.Cast<Transform>().Where(t=>t.name.Contains("BrokenSlateRoof")).ToArray())t.position+=Vector3.down*.08f;
  RefineRiverF(collision,world);
  var snow=GameObject.Find("Frost ascent and white pass").transform;
  var trees=snow.Cast<Transform>().Where(t=>t.name.StartsWith("FoliageFir/")).ToArray();int ti=0;
  foreach(var t in trees) {
   var p=t.position;float d=-p.z;
   // Replace whole branch cards in every snowy tree; original transforms set composition.
   if(d<292)continue;
   var scale=t.localScale;var yaw=t.eulerAngles.y;var capsule=t.GetComponent<CapsuleCollider>();
   foreach(var cap in snow.Cast<Transform>().Where(c=>c.name.Contains("AlpineFir_SnowCover")&&(c.position-p).sqrMagnitude<.002f).ToArray())Object.DestroyImmediate(cap.gameObject);
   var go=Model(snow,"VisualF/CW_FirVolume_"+(1+(ti++%2)),p,scale,yaw);
   if(capsule){go.layer=29;var c=go.AddComponent<CapsuleCollider>();c.center=capsule.center;c.radius=capsule.radius;c.height=capsule.height;}
   Object.DestroyImmediate(t.gameObject);
  }
  // Overlapping bedrock strata cover the stretched escarpment without a pedestal silhouette.
  for(int i=0;i<8;i++) {
   float d=353+i*4.9f,x=WorldLayout.Center(d)-14.8f-1.2f*Mathf.Sin(i*1.7f);
   SnowLedge(snow,x,d,new Vector3(1.45f,1.7f,1.35f),i*67+15,5.4f);
   if(i>2)SnowLedge(snow,x-4,d+1.8f,new Vector3(1.5f,1.55f,1.25f),i*43,4.1f);
  }
  // Dress transitional margins in unequal groups, leaving all central walking width free.
  for(int i=0;i<34;i++) {
   float d=101+i*3.8f,off=(i%2==0?-1:1)*(5.8f+(i%4)*.6f);
   if(d>153&&d<212)continue;
   Grounded(abbey,"CW_RiverGrass",d,off,.5f+(i%3)*.16f);
   if(i%3==0)Grounded(abbey,"CW_LayeredRock_A",d,off+Mathf.Sign(off)*1.5f,.24f+(i%5)*.055f);
  }
 }
 static void ConformPaving(GameObject go,float d,int serial) {
  foreach(var mf in go.GetComponentsInChildren<MeshFilter>()) {
   var mesh=Object.Instantiate(mf.sharedMesh);var v=mesh.vertices;
   for(int i=0;i<v.Length;i++) {var p=mf.transform.TransformPoint(v[i]);p.x+=WorldLayout.Center(-p.z)-WorldLayout.Center(d);p.y+=WorldLayout.Height(p.x,-p.z)-WorldLayout.Level(d);v[i]=mf.transform.InverseTransformPoint(p);}
   mesh.vertices=v;mesh.RecalculateNormals();mesh.RecalculateBounds();AssetDatabase.CreateAsset(mesh,output+"/BroadRoad-"+serial+".asset");mf.sharedMesh=mesh;
  }
 }
 static void RefineRiverF(GameObject collision, WorldEnvironment world) {
  var bank=GameObject.Find("Willowbank landscape").transform;float center=WorldLayout.Center(48.5f);
  foreach(var t in bank.Cast<Transform>().ToArray()) {
   var p=t.position;float d=-p.z;
   if(t.name.Contains("HF_Limestone")&&d>30&&d<65) {
    var scale=t.localScale;scale.y*=.60f;scale.x*=1.15f;scale.z*=1.12f;t.localScale=scale;
    if(d>40&&d<57)p.y=-1.15f;else p.y-=.2f;t.position=p;t.Rotate(0,(p.x>center?1:-1)*13,0);
   }
   if(t.name.Contains("GoldenReedBand"))Object.DestroyImmediate(t.gameObject);
  }
  foreach(var m in materials.Values)if(m.name.Contains("HF_Limestone"))m.SetFloat("_BumpScale",.38f);
  int n=0;
  for(float x=center-24;x<center+26;x+=2.7f)foreach(float side in new[]{-1f,1f}) {
   if(Mathf.Abs(x-center)<5.2f)continue;
   float d=(side<0?WorldLayout.NearShore(x):WorldLayout.FarShore(x))+(side<0?-.2f:.2f);
   var go=Model(bank,"VisualF/CW_ReedVolume",new Vector3(x,WorldLayout.Height(x,d)-.06f,-d),new Vector3(.73f,1.28f+(n%4)*.14f,.9f+(n%3)*.15f),n++*37);
  }
  // Low underwater boulders sit on a shallow shelf, distinct from tall shoreline formations.
  for(int i=0;i<28;i++) {
   float side=i%2==0?-1:1,x=center+side*(5.7f+(i/2%7)*2.3f);
   float d=40.8f+(i%7)*1.5f;if(!WorldLayout.River(x,d))continue;
   var go=Model(bank,"CW_RiverBoulder",new Vector3(x,-1.75f-(i%3)*.19f,-d),new Vector3(.50f+(i%3)*.16f,.34f,.58f+(i%4)*.12f),i*53);
  }
  var surface=GameObject.Find("One reflective river plane").GetComponent<Renderer>().sharedMaterial;surface.shader=Shader.Find("Vesper/VisualF/River");surface.SetColor("_ShallowColor",new Color(.20f,.48f,.46f));surface.SetColor("_DeepColor",new Color(.065f,.29f,.32f));
  // Fragmented paving beyond each bridge apron softens the manufactured rectangular end.
  foreach(float d in new[]{31.5f,65.5f})foreach(float off in new[]{-1.6f,1.6f}) {
   var go=Model(bank,"VisualF/CW_BroadPaving_"+(off<0?1:2),new Vector3(center+off,WorldLayout.Level(d)+.015f,-d),new Vector3(.72f,1,.8f),0);
   ConformPaving(go,d,800+(int)d+(off<0?0:100));
  }
 }
}
}
