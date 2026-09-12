using UnityEngine;

public class VesperCamera:MonoBehaviour {
    public Vector3 target;public Transform player;Vector3 initialTarget,initialPlayer,press;float angle=.46f,elevation=.72f,zoom=8.4f;Camera cam;bool dragging;
    void Start(){cam=GetComponent<Camera>();initialTarget=target;if(player)initialPlayer=player.position;}
    void Update(){if(Input.GetMouseButtonDown(0)){press=Input.mousePosition;dragging=false;}if(Input.GetMouseButton(0)&&Vector3.Distance(press,Input.mousePosition)>5)dragging=true;
      if(dragging&&Input.GetMouseButton(0)){angle-=Input.GetAxis("Mouse X")*.025f;elevation=Mathf.Clamp(elevation-Input.GetAxis("Mouse Y")*.015f,.48f,1.14f);}
      if(Input.GetMouseButtonUp(0)&&!dragging&&player){var ray=cam.ScreenPointToRay(Input.mousePosition);if(new Plane(Vector3.up,Vector3.zero).Raycast(ray,out float d))player.GetComponent<VesperKnight>().Walk(ray.GetPoint(d));}
      zoom=Mathf.Clamp(zoom-Input.mouseScrollDelta.y*.5f,6,12);cam.orthographicSize=Mathf.Lerp(cam.orthographicSize,zoom,1-Mathf.Exp(-9*Time.deltaTime));
      if(Input.GetKeyDown(KeyCode.R)){angle=.46f;elevation=.72f;zoom=8.4f;target=initialTarget;if(player)player.GetComponent<VesperKnight>().ResetPosition();}
      var follow=initialTarget+(player?(player.position-initialPlayer)*.24f:Vector3.zero);target=Vector3.Lerp(target,follow,1-Mathf.Exp(-1.3f*Time.deltaTime));
      transform.position=target+new Vector3(-Mathf.Sin(angle)*Mathf.Cos(elevation),Mathf.Sin(elevation),Mathf.Cos(angle)*Mathf.Cos(elevation))*42;transform.LookAt(target);
    }
}
