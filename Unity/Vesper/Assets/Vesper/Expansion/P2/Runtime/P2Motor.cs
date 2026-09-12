using System.Collections.Generic;
using UnityEngine;
using UnityEngine.AI;
namespace Vesper.Expansion.P2 {
[DefaultExecutionOrder(-40)]
public sealed class P2Motor:MonoBehaviour {
 public const int SurfaceMask=1<<28, BlockMask=1<<29;
 public Vector3 home;
 public float walkSpeed=2.25f,acceleration=5.5f,turnSpeed=420;
 public float Speed{get;private set;} public float Distance{get;private set;} public float TurnRate{get;private set;}
 public int Arrivals{get;private set;} public int Rejected{get;private set;} public int ResetSerial{get;private set;}
 public bool IsWalking=>route.Count>0 || Speed>.02f;
 readonly List<Vector3> route=new List<Vector3>();
 public Vector3 ClickDestination {get;private set;}
 public bool Click(Ray ray){
  // First collision wins: no ray-through wall, water, bridge rail or lower deck fallback.
  if(!Physics.Raycast(ray,out var hit,150,SurfaceMask|BlockMask,QueryTriggerInteraction.Ignore) || hit.collider.gameObject.layer!=28 || hit.normal.y<.7f){Rejected++;return false;}
  // Navigation leaves character clearance around the visible masonry edges.
  // Resolve edge clicks onto nearby safe ground without widening the motor's
  // height tolerance or casting through a foreground obstruction.
  if(!NavMesh.SamplePosition(hit.point,out var nearby,.65f,NavMesh.AllAreas) || Mathf.Abs(nearby.position.y-hit.point.y)>.15f){Rejected++;return false;}
  var destination=nearby.position;
  int steps=Mathf.Max(1,Mathf.CeilToInt(Vector3.Distance(hit.point,destination)/.08f));
  for(int i=0;i<=steps;i++){
   var p=Vector3.Lerp(hit.point,destination,(float)i/steps);
   if(!Physics.SphereCast(p+Vector3.up*.25f,.12f,Vector3.down,out var support,.4f,SurfaceMask|BlockMask,QueryTriggerInteraction.Ignore) || support.collider.gameObject.layer!=28 || support.normal.y<.7f || Mathf.Abs(support.point.y-hit.point.y)>.15f){Rejected++;return false;}
  }
  if(!Walk(destination))return false;
  ClickDestination=destination;return true;
 }
 public bool Walk(Vector3 target){
  if((P2World.Instance && P2World.Instance.Busy) || !NavMesh.SamplePosition(target,out var end,.18f,NavMesh.AllAreas) || Mathf.Abs(end.position.y-target.y)>.15f){Rejected++;return false;}
  var path=new NavMeshPath();
  if(!NavMesh.CalculatePath(transform.position,end.position,NavMesh.AllAreas,path) || path.status!=NavMeshPathStatus.PathComplete){Rejected++;return false;}
  route.Clear(); for(int i=1;i<path.corners.Length;i++)route.Add(path.corners[i]);
  if(route.Count==0)route.Add(end.position);
  return true;
 }
 void Update(){
  float dt=Mathf.Min(Time.deltaTime,.05f); if(dt<=0)return;
  Distance=0; if(P2World.Instance && P2World.Instance.Busy){Speed=0;return;}
  var before=transform.position; float yaw=transform.eulerAngles.y;
  float remaining=0; var prev=before;foreach(var p in route){remaining+=Vector3.Distance(prev,p);prev=p;}
  float desired=Mathf.Min(walkSpeed,Mathf.Sqrt(2*acceleration*remaining));
  if(route.Count>0){var dir=route[0]-before;dir.y=0;if(dir.sqrMagnitude>.00001f){var rot=Quaternion.LookRotation(dir);float angle=Quaternion.Angle(transform.rotation,rot);transform.rotation=Quaternion.RotateTowards(transform.rotation,rot,turnSpeed*dt);desired*=Mathf.Lerp(.12f,1,Mathf.Clamp01(1-angle/100));}}
  Speed=Mathf.MoveTowards(Speed,desired,acceleration*dt);float budget=Speed*dt;
  while(route.Count>0 && budget>0){
   var delta=route[0]-transform.position; delta.y=0;float len=delta.magnitude;float step=Mathf.Min(len,budget);
   var next=transform.position+(len>.00001f?delta/len*step:Vector3.zero);
   if(!NavMesh.SamplePosition(next,out var sample,.35f,NavMesh.AllAreas) || Mathf.Abs(sample.position.y-next.y)>.32f){route.Clear();Speed=0;break;}
   next=sample.position;
   // Correct NavMesh voxel approximation to the actual collision surface on this level.
   if(Physics.SphereCast(next+Vector3.up*.35f,.12f,Vector3.down,out var ground,.7f,SurfaceMask,QueryTriggerInteraction.Ignore))next.y=ground.point.y;
   float surfaceDistance=Vector3.Distance(transform.position,next);
   if(surfaceDistance>step && surfaceDistance>.00001f)next=Vector3.Lerp(transform.position,next,step/surfaceDistance);
   transform.position=next;budget-=step;
   if(len<=step+.001f){route.RemoveAt(0);if(route.Count==0){Arrivals++;Speed=0;}}else break;
  }
  Distance=Vector3.Distance(before,transform.position);Speed=Distance/dt;TurnRate=Mathf.DeltaAngle(yaw,transform.eulerAngles.y)/dt;
 }
 public void ResetPosition(){route.Clear();Speed=Distance=TurnRate=0;transform.position=home;transform.rotation=Quaternion.Euler(0,180,0);ResetSerial++;}
}
}
