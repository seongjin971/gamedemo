using UnityEngine;

public class VesperFirelight:MonoBehaviour {
    Light lamp;float power;
    void Start(){lamp=GetComponent<Light>();power=lamp.intensity;}
    void Update(){lamp.intensity=power*(1+.06f*Mathf.Sin(Time.time*9.7f)+.035f*Mathf.Sin(Time.time*17.1f));}
}
