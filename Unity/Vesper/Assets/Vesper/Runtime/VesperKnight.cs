using UnityEngine;

public class VesperKnight:MonoBehaviour {
    public bool IsWalking=>route.Count>0;
    public Vector3 home;Transform cape;Quaternion capeRest;VesperNavigation nav;System.Collections.Generic.List<Vector3> route=new System.Collections.Generic.List<Vector3>();
    readonly System.Collections.Generic.Dictionary<Transform,Quaternion> limbs=new System.Collections.Generic.Dictionary<Transform,Quaternion>();float phase,move;
    void Start(){foreach(var t in GetComponentsInChildren<Transform>()){if(t.name=="Cape"){cape=t;capeRest=t.localRotation;}if(t.name=="LeftLeg"||t.name=="RightLeg"||t.name=="LeftArm"||t.name=="RightArm")limbs[t]=t.localRotation;}}
    void Update(){float dt=Mathf.Min(Time.deltaTime,.045f),remaining=2.25f*dt;bool walking=route.Count>0;move=Mathf.Lerp(move,walking?1:0,1-Mathf.Exp(-10*dt));
      while(route.Count>0&&remaining>0){var delta=route[0]-transform.position;float d=delta.magnitude,step=Mathf.Min(d,remaining);if(d>.001f){transform.position+=delta/d*step;transform.rotation=Quaternion.Slerp(transform.rotation,Quaternion.LookRotation(delta),1-Mathf.Exp(-14*dt));}remaining-=step;if(d<.03f||step==d)route.RemoveAt(0);else break;}
      phase+=dt*(walking?8:1.5f);foreach(var limb in limbs){float sign=limb.Key.name.StartsWith("Left")?1:-1;limb.Key.localRotation=limb.Value*Quaternion.Euler(Mathf.Sin(phase)*move*.46f*sign*(limb.Key.name.EndsWith("Arm")?-.5f:1)*Mathf.Rad2Deg,0,0);}
      if(cape)cape.localRotation=capeRest*Quaternion.Euler((Mathf.Sin(Time.time*1.9f)*.035f-move*.1f)*Mathf.Rad2Deg,0,(Mathf.Sin(Time.time*2.4f)*.035f+Mathf.Sin(phase)*move*.045f)*Mathf.Rad2Deg);}
    public void Walk(Vector3 p){if(nav==null)nav=new VesperNavigation();if(nav.Valid(p))route=nav.Path(transform.position,p);}
    public void ResetPosition(){route.Clear();transform.position=home;transform.rotation=Quaternion.Euler(0,180,0);}
}
