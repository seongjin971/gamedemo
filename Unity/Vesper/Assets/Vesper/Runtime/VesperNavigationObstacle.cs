using UnityEngine;

// World-XZ polygon generated from the installed tree's low trunk/root mesh.
public sealed class VesperNavigationObstacle:MonoBehaviour {
 public Vector2[] worldPolygon;
 public bool Blocks(Vector3 position,float clearance){
  if(worldPolygon==null||worldPolygon.Length<3)return false;
  var p=new Vector2(position.x,position.z);bool inside=false;
  for(int i=0,j=worldPolygon.Length-1;i<worldPolygon.Length;j=i++){
   var a=worldPolygon[j];var b=worldPolygon[i];var edge=b-a;
   float t=Mathf.Clamp01(Vector2.Dot(p-a,edge)/Mathf.Max(edge.sqrMagnitude,1e-12f));
   if((p-(a+t*edge)).sqrMagnitude<clearance*clearance)return true;
   if((a.y>p.y)!=(b.y>p.y)&&p.x<(b.x-a.x)*(p.y-a.y)/(b.y-a.y)+a.x)inside=!inside;
  }return inside;
 }
}
