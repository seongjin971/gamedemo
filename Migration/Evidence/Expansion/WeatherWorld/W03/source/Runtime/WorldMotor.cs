using System.Collections.Generic;
using UnityEngine;
using UnityEngine.AI;

namespace Vesper.Expansion.WeatherWorld {
[DefaultExecutionOrder(-40)]
public sealed class WorldMotor : MonoBehaviour {
 public const int SurfaceMask=1<<28, BlockMask=1<<29;
 public Vector3 home;
 public float walkSpeed=2.25f, acceleration=5.5f, turnSpeed=420;
 public float Speed{get;private set;} public float Distance{get;private set;} public float TurnRate{get;private set;}
 public int Arrivals{get;private set;} public int Rejected{get;private set;} public int ResetSerial{get;private set;}
 public int SafetyStops{get;private set;} public string LastReject{get;private set;}
 public bool IsWalking=>route.Count>0 || Speed>.02f;
 public Vector3 ClickDestination{get;private set;}
 public int RemainingCorners=>route.Count;
 readonly List<Vector3> route=new List<Vector3>();
 bool Reject(string reason){Rejected++;LastReject=reason;return false;}
 public bool Ground(Vector3 p,out RaycastHit hit){
  hit=default;if(WorldLayout.River(p.x,-p.z)&&p.y<WorldLayout.WaterHeight+.05f)return false;
  return Physics.Raycast(p+Vector3.up*.5f,Vector3.down,out hit,1.05f,SurfaceMask|BlockMask,QueryTriggerInteraction.Ignore)
   && hit.collider.gameObject.layer==28 && hit.normal.y>.72f && Mathf.Abs(hit.point.y-p.y)<.45f;
 }
 public bool BodyClear(Vector3 p){return !Physics.CheckCapsule(p+Vector3.up*.4f,p+Vector3.up*1.4f,.23f,BlockMask,QueryTriggerInteraction.Ignore);}
 public bool Click(Ray ray){
  if(!Physics.Raycast(ray,out var hit,250,SurfaceMask|BlockMask,QueryTriggerInteraction.Ignore))return Reject("No ground");
  if(WorldLayout.River(hit.point.x,-hit.point.z)&&hit.point.y<WorldLayout.WaterHeight+.05f)return Reject("Deep water");
  if(hit.collider.gameObject.layer!=28 || hit.normal.y<.72f)return Reject("Blocked surface");
  if(!NavMesh.SamplePosition(hit.point,out var near,.60f,NavMesh.AllAreas)||Mathf.Abs(near.position.y-hit.point.y)>.22f)return Reject("Outside safe ground");
  int steps=Mathf.Max(1,Mathf.CeilToInt(Vector3.Distance(hit.point,near.position)/.07f));
  for(int i=0;i<=steps;i++){
   var p=Vector3.Lerp(hit.point,near.position,(float)i/steps);
   if(!Ground(p,out var support)||Mathf.Abs(support.point.y-p.y)>.22f||!BodyClear(support.point))return Reject("Unsafe edge correction");
  }
  return Walk(near.position);
 }
 public bool Walk(Vector3 target){
  if(!NavMesh.SamplePosition(target,out var end,.25f,NavMesh.AllAreas)||Mathf.Abs(end.position.y-target.y)>.25f)return Reject("Unreachable target");
  if(!Ground(end.position,out var g)||!BodyClear(g.point))return Reject("No target support");
  var path=new NavMeshPath();
  if(!NavMesh.CalculatePath(transform.position,end.position,NavMesh.AllAreas,path)||path.status!=NavMeshPathStatus.PathComplete)return Reject("Disconnected route");
  route.Clear();for(int i=1;i<path.corners.Length;i++)route.Add(path.corners[i]);
  if(route.Count==0)route.Add(end.position);
  ClickDestination=end.position;LastReject="";return true;
 }
 void Update(){
  float dt=Mathf.Min(Time.deltaTime,.05f);if(dt<=0)return;Distance=0;
  var before=transform.position;float yaw=transform.eulerAngles.y,remaining=0;var prev=before;
  foreach(var p in route){remaining+=Vector3.Distance(prev,p);prev=p;}
  float desired=Mathf.Min(walkSpeed,Mathf.Sqrt(2*acceleration*remaining));
  if(route.Count>0){var dir=route[0]-before;dir.y=0;if(dir.sqrMagnitude>.00001f){var rot=Quaternion.LookRotation(dir);float angle=Quaternion.Angle(transform.rotation,rot);transform.rotation=Quaternion.RotateTowards(transform.rotation,rot,turnSpeed*dt);desired*=Mathf.Lerp(.12f,1,Mathf.Clamp01(1-angle/100));}}
  Speed=Mathf.MoveTowards(Speed,desired,acceleration*dt);float budget=Speed*dt;
  while(route.Count>0&&budget>.000001f){
   var delta=route[0]-transform.position;delta.y=0;float len=delta.magnitude;
   if(len<.025f){route.RemoveAt(0);if(route.Count==0){Arrivals++;Speed=0;}continue;}
   float step=Mathf.Min(len,Mathf.Min(budget,.08f));var next=transform.position+delta/len*step;
   if(!NavMesh.SamplePosition(next,out var sample,.3f,NavMesh.AllAreas)||Mathf.Abs(sample.position.y-next.y)>.28f){StopUnsafe("Navigation edge");break;}
   // Sampling supplies safe height; do not accumulate its lateral projection on slopes.
   // Nearest-point projection from grounded Y can otherwise add movement every frame.
   if(Vector2.Distance(new Vector2(next.x,next.z),new Vector2(sample.position.x,sample.position.z))>.12f){StopUnsafe("Navigation horizontal clearance");break;}
   next.y=sample.position.y;
   if(!Ground(next,out var ground)){StopUnsafe("Lost ground support");break;}next.y=ground.point.y;
   var displacement=next-transform.position;float distance=displacement.magnitude;
   if(distance>step && distance<step*1.7f+.025f){next=transform.position+displacement*(step/distance);if(!Ground(next,out ground)){StopUnsafe("Lost slope support");break;}next.y=ground.point.y;displacement=next-transform.position;distance=displacement.magnitude;}
   if(distance>step*1.7f+.025f){StopUnsafe("Unsupported step from "+transform.position+" to "+next+" displacement="+distance+" budget="+step);break;}
   if(!BodyClear(next)|| (distance>.00001f&&Physics.CapsuleCast(transform.position+Vector3.up*.4f,transform.position+Vector3.up*1.4f,.23f,displacement.normalized,distance,BlockMask,QueryTriggerInteraction.Ignore))){StopUnsafe("Body obstruction from "+transform.position+" to "+next);break;}
   transform.position=next;budget-=Mathf.Max(step,distance);
   if(len<=step+.025f){route.RemoveAt(0);if(route.Count==0){Arrivals++;Speed=0;}}
  }
  Distance=Vector3.Distance(before,transform.position);Speed=Distance/dt;TurnRate=Mathf.DeltaAngle(yaw,transform.eulerAngles.y)/dt;
 }
 void StopUnsafe(string reason){route.Clear();Speed=0;SafetyStops++;LastReject=reason;}
 public void Stop(){route.Clear();Speed=Distance=TurnRate=0;}
 public void ResetPosition(){Stop();transform.position=home;transform.rotation=Quaternion.Euler(0,180,0);ResetSerial++;}
}
}
