using UnityEngine;

namespace Vesper {
 [RequireComponent(typeof(Camera))]
 public sealed class VesperOrbitCamera:MonoBehaviour {
  public Transform player;
  public Vector3 homeTarget=new Vector3(0,2.9f,.7f);
  public float homeSize=14.1f/1.27f;
  public float Angle {get;private set;}=.46f;
  public float Elevation {get;private set;}=.72f;
  public float Zoom {get;private set;}=14.1f/1.27f;
  public int clicks,drags,zooms,resets,blocked;
  Camera cam; Vector3 target,initialPlayer,press,lastMouse;bool dragging;float desiredAngle=.46f,desiredElevation=.72f;
  void Awake(){cam=GetComponent<Camera>();target=homeTarget;Zoom=homeSize;if(player)initialPlayer=player.position;Application.targetFrameRate=60;QualitySettings.vSyncCount=0;}
  void Update(){
   if(Mathf.Abs(Input.mouseScrollDelta.y)>.001f){zooms++;SetZoom(Zoom-Input.mouseScrollDelta.y*.55f);}
   if(Input.GetKeyDown(KeyCode.R)){resets++;ResetView();}
  }
  void OnGUI(){
   // IMGUI drains positional pointer events individually; polling Input once
   // per frame loses the press position when a short drag finishes in one frame.
   var e=Event.current;if(!cam||e.button!=0)return;
   var pos=new Vector3(e.mousePosition.x,Screen.height-e.mousePosition.y,0);
   if(e.type==EventType.MouseDown){press=lastMouse=pos;dragging=false;e.Use();}
   else if(e.type==EventType.MouseDrag){if(Vector3.Distance(press,pos)>5){if(!dragging)drags++;dragging=true;}if(dragging){var delta=pos-lastMouse;Orbit(-delta.x*.004f,-delta.y*.003f);}lastMouse=pos;e.Use();}
   else if(e.type==EventType.MouseUp){if(!dragging&&Vector3.Distance(press,pos)>5){dragging=true;drags++;var delta=pos-press;Orbit(-delta.x*.004f,-delta.y*.003f);}if(!dragging&&player){clicks++;var ray=cam.ScreenPointToRay(pos);if(new Plane(Vector3.up,Vector3.zero).Raycast(ray,out float distance)){var p=ray.GetPoint(distance);if(new VesperNavigation().Valid(p))player.GetComponent<VesperKnight>().Walk(p);else blocked++;}}e.Use();}
  }
  void LateUpdate(){float dt=Time.unscaledDeltaTime;Angle=Mathf.Lerp(Angle,desiredAngle,1-Mathf.Exp(-12*dt));Elevation=Mathf.Lerp(Elevation,desiredElevation,1-Mathf.Exp(-12*dt));cam.orthographicSize=Mathf.Lerp(cam.orthographicSize,Zoom,1-Mathf.Exp(-9*dt));var follow=homeTarget+(player?(player.position-initialPlayer)*.24f:Vector3.zero);target=Vector3.Lerp(target,follow,1-Mathf.Exp(-1.3f*dt));transform.position=target+new Vector3(-Mathf.Sin(Angle)*Mathf.Cos(Elevation),Mathf.Sin(Elevation),Mathf.Cos(Angle)*Mathf.Cos(Elevation))*42;transform.LookAt(target);}
  public void Orbit(float angleDelta,float elevationDelta){desiredAngle=Mathf.Clamp(desiredAngle+angleDelta,-.05f,1.10f);desiredElevation=Mathf.Clamp(desiredElevation+elevationDelta,.48f,1.14f);}
  public void SetZoom(float value){Zoom=Mathf.Clamp(value,7.5f,14f);}
  public void ResetView(){desiredAngle=.46f;desiredElevation=.72f;Zoom=homeSize;target=homeTarget;if(player)player.GetComponent<VesperKnight>().ResetPosition();}
 }
}
