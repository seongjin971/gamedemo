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
[Serializable] public class Bridge { public int version; public string player; public View camera; public string[] geometryIds; public Mat[] materials; public Node[] nodes; }
[Serializable] public class View { public float[] position, quaternion, target; public float orthoHeight; public int width,height; }
[Serializable] public class Mat { public string id,name,type,map,normalMap; public float[] color,emissive,normalScale; public float roughness,metalness,opacity,clearcoat,emissiveIntensity; public bool transparent,distant,vertexColors; public int side; }
[Serializable] public class Node { public string id,parent,name,type,geometry; public bool distant,visible,castShadow; public float[] position,quaternion,scale; public string[] materials; public Instance[] instances; }
[Serializable] public class Instance { public float[] position,quaternion,scale,color; }
[Serializable] public class Geo { public string id,name; public float[] positions,normals,uv,colors; public int[] indices; public Group[] groups; }
[Serializable] public class Group { public int start,count,materialIndex; }

public static class VesperImport {
    const string Root="Assets/Vesper", Generated=Root+"/Generated", Source=Root+"/Import";
    static Vector3 P(float[] v)=>new Vector3(-v[0],v[1],v[2]);
    static Vector3 V(float[] v)=>new Vector3(v[0],v[1],v[2]);
    static Quaternion Q(float[] v)=>new Quaternion(v[0],-v[1],-v[2],v[3]);
    static Color C(float[] v)=>new Color(v[0],v[1],v[2],1);
    static void Folder(string p){if(AssetDatabase.IsValidFolder(p))return;var i=p.LastIndexOf('/');Folder(p.Substring(0,i));AssetDatabase.CreateFolder(p.Substring(0,i),p.Substring(i+1));}
    static void Asset(UnityEngine.Object o,string p){var existing=AssetDatabase.LoadMainAssetAtPath(p);if(existing==null){AssetDatabase.CreateAsset(o,p);return;}
      // Explicit native setters refresh GPU resources as well as serialized data,
      // so same-process captures cannot show the previous mesh/material contents.
      if(o is Mesh source&&existing is Mesh mesh){mesh.Clear();mesh.indexFormat=source.indexFormat;mesh.vertices=source.vertices;mesh.normals=source.normals;mesh.uv=source.uv;mesh.colors=source.colors;mesh.tangents=source.tangents;mesh.subMeshCount=source.subMeshCount;for(int i=0;i<source.subMeshCount;i++)mesh.SetIndices(source.GetIndices(i),source.GetTopology(i),i);mesh.bounds=source.bounds;}
      else if(o is Material sourceMat&&existing is Material material){material.shader=sourceMat.shader;material.CopyPropertiesFromMaterial(sourceMat);}
      else EditorUtility.CopySerialized(o,existing);
      EditorUtility.SetDirty(existing);UnityEngine.Object.DestroyImmediate(o);
    }

    [MenuItem("VESPER/Build migration slice")]
    public static void Build(){
      Folder(Generated);Folder(Generated+"/Meshes");Folder(Generated+"/Materials");Folder(Root+"/Scenes");Folder(Root+"/Settings");
      foreach(var path in Directory.GetFiles(Root+"/Textures","*.png")){
        var ti=(TextureImporter)AssetImporter.GetAtPath(path);if(ti==null)continue;
        ti.textureType=path.Contains("normal")?TextureImporterType.NormalMap:TextureImporterType.Default;
        ti.sRGBTexture=!path.Contains("normal");ti.textureCompression=TextureImporterCompression.Uncompressed;ti.maxTextureSize=2048;ti.anisoLevel=8;ti.wrapMode=path.Contains("flame")||path.Contains("panorama")?TextureWrapMode.Clamp:TextureWrapMode.Repeat;ti.SaveAndReimport();
      }
      var bridge=JsonUtility.FromJson<Bridge>(File.ReadAllText(Source+"/unity-scene.json"));
      if(bridge.version!=1)throw new Exception("Unsupported bridge schema");
      var scene=EditorSceneManager.NewScene(NewSceneSetup.EmptyScene,NewSceneMode.Single);
      var meshes=new Dictionary<string,Mesh>();var mats=new Dictionary<string,Material>();var sourceMats=bridge.materials.ToDictionary(m=>m.id);
      foreach(var id in bridge.geometryIds){var g=JsonUtility.FromJson<Geo>(File.ReadAllText(Source+"/unity-geometry-"+id+".json"));var mesh=MakeMesh(g);var path=Generated+"/Meshes/"+id+".asset";Asset(mesh,path);meshes[id]=AssetDatabase.LoadAssetAtPath<Mesh>(path);}
      foreach(var m in bridge.materials){var mat=MakeMaterial(m);var path=Generated+"/Materials/"+m.id+".mat";Asset(mat,path);mats[m.id]=AssetDatabase.LoadAssetAtPath<Material>(path);}
      var objects=new Dictionary<string,GameObject>();int importedInstances=0,omittedInstances=0;
      foreach(var n in bridge.nodes){var o=new GameObject(n.name);objects[n.id]=o;
        if(!string.IsNullOrEmpty(n.parent)&&objects.TryGetValue(n.parent,out var parent))o.transform.SetParent(parent.transform,false);
        o.transform.localPosition=P(n.position);o.transform.localRotation=Q(n.quaternion);o.transform.localScale=V(n.scale);
        if(n.instances.Length>0){
          var selected=n.instances.Where(i=>n.distant||(i.position[0]>=-10&&i.position[0]<=10&&i.position[2]>=-13&&i.position[2]<=22&&i.position[1]>=-3&&i.position[1]<=15)).ToArray();
          importedInstances+=selected.Length;omittedInstances+=n.instances.Length-selected.Length;
          var source=meshes[n.geometry];int chunk=0;
          foreach(var group in selected.Select((i,index)=>new {i,index}).GroupBy(x=>x.index/100)){
            var combine=new List<CombineInstance>();var tinted=new List<Mesh>();
            foreach(var item in group){var mesh=UnityEngine.Object.Instantiate(source);mesh.colors=Enumerable.Repeat(C(item.i.color),mesh.vertexCount).ToArray();tinted.Add(mesh);combine.Add(new CombineInstance{mesh=mesh,transform=Matrix4x4.TRS(P(item.i.position),Q(item.i.quaternion),V(item.i.scale))});}
            var merged=new Mesh{name=n.name+" batch "+chunk,indexFormat=IndexFormat.UInt32};merged.CombineMeshes(combine.ToArray(),true,true);merged.RecalculateBounds();
            string path=Generated+"/Meshes/batch-"+n.id+"-"+chunk+".asset";Asset(merged,path);foreach(var mesh in tinted)UnityEngine.Object.DestroyImmediate(mesh);
            var part=new GameObject("Masonry batch "+chunk++);part.transform.SetParent(o.transform,false);part.AddComponent<MeshFilter>().sharedMesh=AssetDatabase.LoadAssetAtPath<Mesh>(path);var mr=part.AddComponent<MeshRenderer>();mr.sharedMaterial=mats[n.materials[0]];mr.shadowCastingMode=n.distant?ShadowCastingMode.Off:ShadowCastingMode.On;
          }
        }else if(!string.IsNullOrEmpty(n.geometry)&&n.materials.Length>0){
          if(n.type=="Sprite"&&sourceMats[n.materials[0]].map=="ruins-panorama.png"){UnityEngine.Object.DestroyImmediate(o);objects.Remove(n.id);continue;}
          o.AddComponent<MeshFilter>().sharedMesh=meshes[n.geometry];var mr=o.AddComponent<MeshRenderer>();mr.sharedMaterials=n.materials.Select(id=>mats[id]).ToArray();mr.shadowCastingMode=n.castShadow?ShadowCastingMode.On:ShadowCastingMode.Off;
          if(n.type=="Sprite")o.AddComponent<VesperBillboard>();
        }
        o.SetActive(n.visible);
      }
      // Import the context visible behind the first comparison zone too. The
      // deep foundation, full-scene camera polish and remaining VFX follow later.
      ConfigurePipeline();ConfigureLighting();
      var cameraObject=new GameObject("Migration comparison camera");var camera=cameraObject.AddComponent<Camera>();camera.tag="MainCamera";
      camera.orthographic=true;camera.orthographicSize=bridge.camera.orthoHeight*.5f;camera.nearClipPlane=.1f;camera.farClipPlane=160;
      camera.transform.position=P(bridge.camera.position);camera.transform.LookAt(P(bridge.camera.target));camera.clearFlags=CameraClearFlags.SolidColor;camera.backgroundColor=new Color(.025f,.045f,.066f);camera.allowHDR=true;
      var cameraData=camera.GetUniversalAdditionalCameraData();cameraData.renderPostProcessing=true;cameraData.antialiasing=AntialiasingMode.SubpixelMorphologicalAntiAliasing;cameraData.antialiasingQuality=AntialiasingQuality.High;
      var cameraControl=cameraObject.AddComponent<VesperCamera>();cameraControl.target=P(bridge.camera.target);
      var backdrop=GameObject.CreatePrimitive(PrimitiveType.Quad);backdrop.name="Preserved city panorama";UnityEngine.Object.DestroyImmediate(backdrop.GetComponent<Collider>());backdrop.transform.SetParent(camera.transform,false);backdrop.transform.localPosition=new Vector3(0,0,120);backdrop.transform.localScale=new Vector3(46.63f,23.315f,1);backdrop.layer=31;
      var backdropMat=new Material(Shader.Find("Universal Render Pipeline/Unlit")){name="City backdrop"};backdropMat.SetTexture("_BaseMap",AssetDatabase.LoadAssetAtPath<Texture2D>(Root+"/Textures/ruins-panorama.png"));backdropMat.SetColor("_BaseColor",new Color(.28f,.34f,.42f));backdropMat.SetFloat("_Cull",0);Asset(backdropMat,Generated+"/Materials/CityBackdrop.mat");backdrop.GetComponent<MeshRenderer>().sharedMaterial=AssetDatabase.LoadAssetAtPath<Material>(Generated+"/Materials/CityBackdrop.mat");backdrop.GetComponent<MeshRenderer>().shadowCastingMode=ShadowCastingMode.Off;
      var reflection=new GameObject("Native floor reflection");reflection.transform.position=new Vector3(0,-.025f,0);reflection.AddComponent<VesperPlanarReflection>();
      if(objects.TryGetValue(bridge.player,out var player)){var controller=player.AddComponent<VesperKnight>();controller.home=player.transform.position;cameraControl.player=player.transform;}
      var volume=new GameObject("Night grade").AddComponent<Volume>();volume.isGlobal=true;
      var profile=AssetDatabase.LoadAssetAtPath<VolumeProfile>(Root+"/Settings/NightGrade.asset");if(!profile){profile=ScriptableObject.CreateInstance<VolumeProfile>();AssetDatabase.CreateAsset(profile,Root+"/Settings/NightGrade.asset");}
      // Use persistent overrides directly: hidden VolumeProfile.Add objects are
      // not returned by LoadAssetAtPath, and transient profiles release overrides.
      var tone=VolumeOverride<Tonemapping>();tone.mode.value=TonemappingMode.ACES;
      var bloom=VolumeOverride<Bloom>();bloom.threshold.value=1.5f;bloom.intensity.value=.2f;bloom.scatter.value=.52f;
      var color=VolumeOverride<ColorAdjustments>();color.postExposure.value=0;color.contrast.value=4;
      profile.components.Clear();profile.components.Add(tone);profile.components.Add(bloom);profile.components.Add(color);profile.Reset();EditorUtility.SetDirty(profile);volume.sharedProfile=profile;
      PlayerSettings.colorSpace=ColorSpace.Linear;PlayerSettings.companyName="VESPER";PlayerSettings.productName="VESPER Unity migration";PlayerSettings.defaultScreenWidth=1536;PlayerSettings.defaultScreenHeight=1024;PlayerSettings.fullScreenMode=FullScreenMode.Windowed;
      QualitySettings.vSyncCount=0;Application.targetFrameRate=60;
      EditorSceneManager.SaveScene(scene,Root+"/Scenes/VesperMigrationSlice.unity");EditorBuildSettings.scenes=new[]{new EditorBuildSettingsScene(Root+"/Scenes/VesperMigrationSlice.unity",true)};AssetDatabase.SaveAssets();
      var report=new {schema=1,geometries=meshes.Count,materials=mats.Count,nodes=objects.Count,importedInstances,omittedInstances,missingScripts=UnityEngine.Object.FindObjectsByType<Transform>().Sum(t=>GameObjectUtility.GetMonoBehavioursWithMissingScriptCount(t.gameObject)),scene=scene.path};
      string json="{\"geometryCount\":"+meshes.Count+",\"materialCount\":"+mats.Count+",\"nodeCount\":"+objects.Count+",\"importedInstances\":"+importedInstances+",\"deferredInstances\":"+omittedInstances+",\"missingScripts\":"+report.missingScripts+"}";
      Directory.CreateDirectory("../../.dream-loop/unity-migration");File.WriteAllText("../../.dream-loop/unity-migration/import-report.json",json);
      Debug.Log("VESPER_IMPORT_PASS "+json);
    }
    static Mesh MakeMesh(Geo g){if(g.positions.Length%3!=0)throw new Exception("Invalid position stride: "+g.id);int count=g.positions.Length/3;if(g.uv.Length!=0&&g.uv.Length!=count*2)throw new Exception("Invalid UV stride: "+g.id);if(g.indices.Any(i=>i<0||i>=count))throw new Exception("Index out of bounds: "+g.id);var m=new Mesh{name=g.name,indexFormat=IndexFormat.UInt32};var p=new Vector3[count];var normals=new Vector3[count];var uv=new Vector2[count];
      for(int i=0;i<count;i++){p[i]=new Vector3(-g.positions[i*3],g.positions[i*3+1],g.positions[i*3+2]);if(g.normals.Length==count*3)normals[i]=new Vector3(-g.normals[i*3],g.normals[i*3+1],g.normals[i*3+2]);if(g.uv.Length==count*2)uv[i]=new Vector2(g.uv[i*2],g.uv[i*2+1]);}
      m.vertices=p;m.uv=uv;if(g.colors.Length==count*3){var colors=new Color[count];for(int i=0;i<count;i++)colors[i]=new Color(g.colors[i*3],g.colors[i*3+1],g.colors[i*3+2],1);m.colors=colors;}
      int[] index=g.indices.Length>0?g.indices:Enumerable.Range(0,count).ToArray();
      // Bridge v1 nodes each use one material. Collapse authoring face groups so
      // procedural boxes and merged instancing retain every face in Unity.
      for(int i=0;i+2<index.Length;i+=3){int t=index[i];index[i]=index[i+2];index[i+2]=t;}m.triangles=index;
      if(g.normals.Length==count*3)m.normals=normals;else m.RecalculateNormals();m.RecalculateTangents();m.RecalculateBounds();return m;
    }
    static Material MakeMaterial(Mat m){bool stone=m.map=="stone-grain-v2.png";bool flame=m.map=="flame-v1.png";bool unlit=m.type=="MeshBasicMaterial"||m.type=="SpriteMaterial";
      var shader=Shader.Find(stone||m.vertexColors?"Vesper/WetStone":flame?"Vesper/Flame":unlit?"Universal Render Pipeline/Unlit":"Universal Render Pipeline/Lit");if(!shader)throw new Exception("Missing shader "+m.name);
      var mat=new Material(shader){name=m.name,enableInstancing=true};var baseColor=C(m.color).gamma;baseColor.a=m.opacity;mat.SetColor("_BaseColor",baseColor);mat.SetFloat("_Smoothness",1-m.roughness);mat.SetFloat("_Metallic",m.metalness);
      if(!string.IsNullOrEmpty(m.map))mat.SetTexture("_BaseMap",AssetDatabase.LoadAssetAtPath<Texture2D>(Root+"/Textures/"+m.map));
      if(!string.IsNullOrEmpty(m.normalMap)){mat.SetTexture("_BumpMap",AssetDatabase.LoadAssetAtPath<Texture2D>(Root+"/Textures/"+m.normalMap));mat.SetFloat("_BumpScale",m.normalScale[0]);mat.EnableKeyword("_NORMALMAP");}
      if(m.map.StartsWith("bark-")){mat.SetTextureScale("_BaseMap",new Vector2(1,-1));mat.SetTextureOffset("_BaseMap",new Vector2(0,1));}
      if(stone){mat.SetFloat("_Wetness",m.clearcoat>0?1:0);mat.SetFloat("_WorldScale",.18f);mat.SetFloat("_Distant",m.distant?1:0);}
      else if(m.vertexColors){mat.SetFloat("_Wetness",0);mat.SetFloat("_PatinaStrength",0);mat.SetFloat("_BumpScale",0);}
      if(m.emissiveIntensity>0){mat.SetColor("_EmissionColor",C(m.emissive)*m.emissiveIntensity);mat.EnableKeyword("_EMISSION");}
      if(m.side==2)mat.SetFloat("_Cull",0);
      if(m.transparent&&!flame){mat.SetFloat("_Surface",1);mat.SetFloat("_SrcBlend",(float)BlendMode.SrcAlpha);mat.SetFloat("_DstBlend",(float)BlendMode.OneMinusSrcAlpha);mat.SetFloat("_ZWrite",0);mat.EnableKeyword("_SURFACE_TYPE_TRANSPARENT");mat.renderQueue=3000;}
      if(flame){mat.SetColor("_BaseColor",new Color(3.2f,2.8f,2,1));mat.renderQueue=3000;}
      return mat;
    }
    static T VolumeOverride<T>() where T:VolumeComponent {
      string path=Root+"/Settings/"+typeof(T).Name+".asset";var component=AssetDatabase.LoadAllAssetsAtPath(path).OfType<T>().FirstOrDefault();
      if(!component){component=ScriptableObject.CreateInstance<T>();AssetDatabase.CreateAsset(component,path);}component.hideFlags=HideFlags.None;component.SetAllOverridesTo(true);EditorUtility.SetDirty(component);return component;
    }
    static void ConfigurePipeline(){var rendererData=ScriptableObject.CreateInstance<UniversalRendererData>();rendererData.name="Vesper Forward+";rendererData.renderingMode=RenderingMode.ForwardPlus;
      var ao=ScriptableObject.CreateInstance<ScreenSpaceAmbientOcclusion>();ao.name="Courtyard contact shading";var settings=new SerializedObject(ao);settings.FindProperty("m_Settings.Downsample").boolValue=true;settings.FindProperty("m_Settings.Intensity").floatValue=1.2f;settings.FindProperty("m_Settings.Radius").floatValue=.45f;settings.ApplyModifiedPropertiesWithoutUndo();Asset(ao,Root+"/Settings/CourtyardAO.asset");rendererData.rendererFeatures.Add(AssetDatabase.LoadAssetAtPath<ScreenSpaceAmbientOcclusion>(Root+"/Settings/CourtyardAO.asset"));
      Asset(rendererData,Root+"/Settings/VesperRenderer.asset");rendererData=AssetDatabase.LoadAssetAtPath<UniversalRendererData>(Root+"/Settings/VesperRenderer.asset");
      var pipeline=UniversalRenderPipelineAsset.Create(rendererData);pipeline.name="Vesper URP";pipeline.supportsHDR=true;pipeline.supportsCameraDepthTexture=true;pipeline.supportsCameraOpaqueTexture=true;pipeline.msaaSampleCount=1;pipeline.renderScale=1;pipeline.shadowDistance=70;pipeline.shadowCascadeCount=2;pipeline.mainLightShadowmapResolution=2048;pipeline.maxAdditionalLightsCount=8;var pipelineSerialized=new SerializedObject(pipeline);pipelineSerialized.FindProperty("m_MainLightShadowsSupported").boolValue=true;pipelineSerialized.FindProperty("m_AdditionalLightShadowsSupported").boolValue=true;pipelineSerialized.ApplyModifiedPropertiesWithoutUndo();
      Asset(pipeline,Root+"/Settings/VesperURP.asset");pipeline=AssetDatabase.LoadAssetAtPath<UniversalRenderPipelineAsset>(Root+"/Settings/VesperURP.asset");GraphicsSettings.defaultRenderPipeline=pipeline;QualitySettings.renderPipeline=pipeline;
    }
    static Light Light(string name,LightType type,Vector3 source,Vector3 target,Color color,float intensity){var l=new GameObject(name).AddComponent<Light>();l.type=type;l.transform.position=P(new[]{source.x,source.y,source.z});l.transform.LookAt(P(new[]{target.x,target.y,target.z}));l.color=color;l.intensity=intensity/Mathf.PI*(type==LightType.Point?1.6f:1);return l;}
    static void ConfigureLighting(){RenderSettings.ambientMode=AmbientMode.Trilight;RenderSettings.ambientSkyColor=new Color(.27f,.36f,.47f);RenderSettings.ambientEquatorColor=new Color(.11f,.15f,.21f);RenderSettings.ambientGroundColor=new Color(.035f,.033f,.035f);RenderSettings.ambientIntensity=1;
      RenderSettings.fog=true;RenderSettings.fogMode=FogMode.ExponentialSquared;RenderSettings.fogColor=new Color(.12f,.20f,.27f);RenderSettings.fogDensity=.008f;
      var moon=Light("Moon",LightType.Directional,new Vector3(-20,28,-18),Vector3.zero,new Color(.737f,.835f,.878f),2.1f);moon.shadows=LightShadows.Soft;moon.shadowBias=.025f;moon.shadowNormalBias=.035f;RenderSettings.sun=moon;
      Light("Soft fill",LightType.Directional,new Vector3(-12,18,20),Vector3.zero,new Color(.608f,.698f,.808f),.24f);
      Light("Blue rim",LightType.Directional,new Vector3(5,12,-20),Vector3.zero,new Color(.463f,.667f,.741f),.75f);
      var key=Light("Tree key",LightType.Spot,new Vector3(-11,11,8),new Vector3(-7.2f,4,3.7f),new Color(.73f,.77f,.81f),25);key.range=19;key.spotAngle=63;key.innerSpotAngle=25;
      foreach(float x in new[]{-1.65f,6.9f}){var f=Light("Brazier",LightType.Point,new Vector3(x,2,-1.45f),Vector3.zero,new Color(1,.565f,.18f),x<0?18:26);f.range=9.8f;f.shadows=LightShadows.Soft;f.shadowBias=.025f;f.gameObject.AddComponent<VesperFirelight>();}
    }
}
}
