using System;
using System.IO;
using System.Linq;
using System.Text;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.AI;

namespace Vesper.Expansion.P2.Editor {
public static class P2ClickAudit {
 public static void Build() {
  Directory.CreateDirectory(Evidence);
  var report=BuildPipeline.BuildPlayer(new BuildPlayerOptions { scenes=new[]{P2GroundBuild.Scene}, locationPathName="Builds/VesperP2ClickFix/VesperP2.exe",target=BuildTarget.StandaloneWindows64,options=BuildOptions.StrictMode });
  File.WriteAllText(Evidence+"/build-report.txt",$"{report.summary.result}; errors={report.summary.totalErrors}; warnings={report.summary.totalWarnings}; seconds={report.summary.totalTime.TotalSeconds}");
  EditorApplication.Exit(report.summary.result==UnityEditor.Build.Reporting.BuildResult.Succeeded?0:1);
 }
 public const string Evidence="../../Migration/Evidence/Expansion/P2-ClickFix";
 public static void Audit() { try {
  Directory.CreateDirectory(Evidence);
  EditorSceneManager.OpenScene("Assets/Vesper/Scenes/Expansion/VesperP2.unity");
  var cam=Camera.main; var cc=cam.GetComponent<P2Camera>();
  var target=cc.homeTarget;
  cam.transform.position=target+new Vector3(-Mathf.Sin(.46f)*Mathf.Cos(.72f),Mathf.Sin(.72f),Mathf.Cos(.46f)*Mathf.Cos(.72f))*42;
  cam.transform.LookAt(target);cam.orthographicSize=cc.homeSize;cam.aspect=1.5f;
  Physics.SyncTransforms();
  var sb=new StringBuilder("x,z,viewportX,viewportY,firstCollider,hitY,normalY,navTarget,pathComplete,allHits\n");
  for(float z=2;z<=10;z+=1)for(float x=-6;x<=6;x+=1){
   var point=new Vector3(x,0,z);var vp=cam.WorldToViewportPoint(point);
   var ray=cam.ViewportPointToRay(vp);
   var hits=Physics.RaycastAll(ray,150,P2Motor.SurfaceMask|P2Motor.BlockMask,QueryTriggerInteraction.Ignore).OrderBy(h=>h.distance).ToArray();
   var nav=NavMesh.SamplePosition(point,out var nh,.18f,NavMesh.AllAreas);
   var path=new NavMeshPath();bool complete=nav&&NavMesh.CalculatePath(cc.player.transform.position,nh.position,NavMesh.AllAreas,path)&&path.status==NavMeshPathStatus.PathComplete;
   var first=hits.FirstOrDefault();
   sb.AppendLine($"{x},{z},{vp.x:F3},{vp.y:F3},{(first.collider?first.collider.name:"NONE")},{first.point.y:F3},{first.normal.y:F3},{nav},{complete},\"{string.Join(" | ",hits.Take(8).Select(h=>$"{h.collider.name}:{h.collider.gameObject.layer}@{h.point.y:F3}"))}\"");
  }
  File.WriteAllText(Evidence+"/courtyard-rays.csv",sb.ToString());
  sb.Clear();
  foreach(var point in new[]{new Vector3(4.73f,0,.24f),new Vector3(4.68f,0,.35f),new Vector3(4.91f,0,3.78f),new Vector3(-2.98f,0,1.30f)}) {
   bool found=NavMesh.SamplePosition(point,out var nearest,2,NavMesh.AllAreas);
   var path=new NavMeshPath();bool complete=found&&NavMesh.CalculatePath(cc.player.transform.position,nearest.position,NavMesh.AllAreas,path)&&path.status==NavMeshPathStatus.PathComplete;
   sb.AppendLine($"point={point} originalValid={new VesperNavigation().Valid(point)} nearest={nearest.position} distance={nearest.distance} found={found} path={complete}");
  }
  File.WriteAllText(Evidence+"/reported-targets.txt",sb.ToString());
  EditorApplication.Exit(0);
 }catch(Exception e){Debug.LogException(e);EditorApplication.Exit(1);}}
}
}
