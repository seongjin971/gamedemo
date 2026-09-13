using System;
using System.IO;
using System.Linq;
using UnityEngine;

namespace Vesper.Expansion.ContinuousWorld.Editor {
public static partial class WorldVisuals {
 [Serializable]sealed class SnowLayout {public SnowEntry[] entries;}
 [Serializable]sealed class SnowEntry {public string name;public int layer;public bool activeSelf;public Vector3 localPosition,localScale;public Quaternion localRotation;public string[] componentTypes;public SnowEntry[] children;}
 static bool ContainsComponent(SnowEntry entry,string type)=>entry.componentTypes.Contains(type)||(entry.children!=null&&entry.children.Any(c=>ContainsComponent(c,type)));
 static void BuildSnowLayout(Transform parent){
  // Authored D01 layout recovered read-only from its preserved player, independent of other regions' random consumption.
  var path=Path.GetFullPath("../../Migration/Source/Expansion/ContinuousWorld/SnowD01Layout.json");
  var layout=JsonUtility.FromJson<SnowLayout>(File.ReadAllText(path));int count=0;
  foreach(var entry in layout.entries){
   if(entry.name=="Snow flurries")continue;
   var pos=entry.localPosition;float d=-pos.z;
   // Keep the authored horizontal composition while settling rocks onto the new west overlook drop.
   pos.y-=24*Mathf.SmoothStep(0,1,Mathf.InverseLerp(355,372,d))*Mathf.SmoothStep(0,1,Mathf.InverseLerp(8,16,WorldLayout.Center(d)-pos.x));
   string model=entry.name.Replace("SnowCover/CW_CardedAlpineFir_SnowCover","FirSnowV2/CW_CardedAlpineFir_SnowCoverV2");
   bool hf=model.StartsWith("CW_HF_");var go=Model(parent,model,pos,entry.localScale,0,ContainsComponent(entry,"MeshCollider"),hf);
   if(!go)throw new InvalidOperationException("Missing authored snow model "+entry.name);
   go.transform.localRotation=entry.localRotation;go.layer=entry.layer;go.SetActive(entry.activeSelf);
   if(entry.componentTypes.Contains("CapsuleCollider")){var trunk=go.AddComponent<CapsuleCollider>();trunk.center=Vector3.up*1.8f;trunk.height=3.6f;trunk.radius=.24f;}
   count++;
  }
  if(count!=141)throw new InvalidOperationException("Incomplete authored snow layout "+count);
  Debug.Log("WORLD AUTHORED SNOW restored "+count+" model wrappers from protected D01 layout");
 }
}
}
