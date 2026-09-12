using UnityEngine;

[ExecuteAlways]
public class VesperBillboard:MonoBehaviour {
    void LateUpdate(){if(Camera.main)transform.rotation=Camera.main.transform.rotation;}
}
