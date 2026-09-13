using System.Collections.Generic;
using System.Linq;
using UnityEngine;
namespace Vesper.Expansion.LinearWorld.Editor {
public static partial class LinearBuild {
 static void Terrain(Transform parent){
  for(int d0=-24;d0<336;d0+=24)for(int x0=-48;x0<48;x0+=24){
   int cells=x0==-24||x0==0?48:16;float step=24f/cells;var v=new List<Vector3>();var t=new List<int>();
   for(int z=0;z<=cells;z++)for(int x=0;x<=cells;x++){float px=x0+x*step,d=d0+z*step;v.Add(new Vector3(px,WorldLayout.Height(px,d),-d));}
   for(int z=0;z<cells;z++)for(int x=0;x<cells;x++){int a=z*(cells+1)+x;t.AddRange(new[]{a,a+1,a+cells+1,a+1,a+cells+2,a+cells+1});}
   var chunk=MeshObject(parent,"Linear terrain "+x0+" "+d0,v,t,earth,28);
   var mesh=chunk.GetComponent<MeshFilter>().sharedMesh;
   mesh.normals=v.Select(p=>{float dx=(WorldLayout.Height(p.x+.1f,-p.z)-WorldLayout.Height(p.x-.1f,-p.z))/.2f;float dz=(WorldLayout.Height(p.x,-p.z-.1f)-WorldLayout.Height(p.x,-p.z+.1f))/.2f;return new Vector3(-dx,1,-dz).normalized;}).ToArray();
  }
  // Finite start/end boundaries blend into the dressing, keeping the route bounded.
  foreach(float d in new[]{-3f,304f}){var g=Box(parent,"Route boundary",WorldLayout.Point(d)+Vector3.up*1.5f,new Vector3(96,3,.3f),stone);g.GetComponent<Renderer>().enabled=false;}
 }
 static void Bridge(Transform parent){
  float h=WorldLayout.Level(25);var deck=Box(parent,"Linear bridge deck",new Vector3(0,h-.25f,-25),new Vector3(4.1f,.5f,14),stone,28);deck.GetComponent<Renderer>().enabled=false;
  foreach(float x in new[]{-2.15f,2.15f}){var rail=Box(parent,"Linear bridge parapet collision",new Vector3(x,h+.45f,-25),new Vector3(.25f,.9f,14),stone);rail.GetComponent<Renderer>().enabled=false;}
 }
}
}
