using System;
using System.Linq;
using System.Collections.Generic;
using UnityEngine;

namespace Vesper.Editor {
public static class VesperNavigationBuild {
 static float Cross(Vector2 a,Vector2 b,Vector2 c)=>(b.x-a.x)*(c.y-a.y)-(b.y-a.y)*(c.x-a.x);
 public static void InstallRootBoundary(GameObject tree,Mesh mesh){
  // Include all exposed root tips and the low trunk, but no buried geometry or
  // crown AABB. Transform the actual installed mesh, including both tree yaws.
  var points=mesh.vertices.Where(v=>v.y>=-.005f&&v.y<=.7f).Select(v=>tree.transform.TransformPoint(v)).Select(v=>new Vector2(v.x,v.z)).Distinct().OrderBy(v=>v.x).ThenBy(v=>v.y).ToArray();
  if(points.Length<3)throw new Exception("Tree root footprint has no samples");
  var hull=new List<Vector2>();foreach(var point in points){while(hull.Count>=2&&Cross(hull[hull.Count-2],hull[hull.Count-1],point)<=0)hull.RemoveAt(hull.Count-1);hull.Add(point);}int lower=hull.Count;
  for(int i=points.Length-2;i>=0;i--){while(hull.Count>lower&&Cross(hull[hull.Count-2],hull[hull.Count-1],points[i])<=0)hull.RemoveAt(hull.Count-1);hull.Add(points[i]);}hull.RemoveAt(hull.Count-1);
  var obstacle=tree.AddComponent<VesperNavigationObstacle>();obstacle.worldPolygon=hull.ToArray();
  Validate();Debug.Log("VESPER_ROOT_NAVIGATION hull="+hull.Count+" samples="+points.Length+" clearance=.28 world");
 }
 static void Validate(){
  var nav=new VesperNavigation();var start=new Vector3(-2.25f,0,7.5f);int paths=0;
  if(nav.Valid(new Vector3(7.2f,0,3.7f)))throw new Exception("Tree trunk unexpectedly traversable");
  for(float x=-7;x<=7;x+=1)for(float z=0;z<=11;z+=1){var destination=new Vector3(x,0,z);if(!nav.Valid(destination))continue;var route=nav.Path(start,destination);if(route.Count==0)throw new Exception("Valid floor unreachable "+destination);var previous=start;
   foreach(var next in route){for(int sample=1;sample<=20;sample++)if(!nav.Valid(Vector3.Lerp(previous,next,sample/20f)))throw new Exception("Path crosses root/body clearance "+previous+" -> "+next);previous=next;}paths++;
  }Debug.Log("VESPER_ROOT_NAVIGATION_VALIDATED routes="+paths);
 }
}
}
