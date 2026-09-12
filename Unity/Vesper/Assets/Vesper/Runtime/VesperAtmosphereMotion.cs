using UnityEngine;

namespace Vesper {
 public sealed class VesperAtmosphereMotion : MonoBehaviour {
  public Transform[] rings, flames; public Transform halo;
  Vector3[] sizes,positions; Vector3 haloHome;
  void Start(){sizes=new Vector3[flames.Length];positions=new Vector3[flames.Length];for(int i=0;i<flames.Length;i++){sizes[i]=flames[i].localScale;positions[i]=flames[i].position;}if(halo)haloHome=halo.position;}
  void Update(){float t=Time.time;if(halo)halo.position=haloHome+Vector3.up*(Mathf.Sin(t*.85f)*.07f);if(rings.Length>2){rings[2].localRotation=Quaternion.Euler(0,(1.1f+t*.16f)*Mathf.Rad2Deg,0);rings[3].localRotation=Quaternion.Euler((.92f+t*.12f)*Mathf.Rad2Deg,0,0);}for(int i=0;i<flames.Length;i++){float p=i*2.3f;flames[i].localScale=Vector3.Scale(sizes[i],new Vector3(1+Mathf.Sin(t*7+p)*.07f,1+Mathf.Sin(t*10+p)*.12f,1));flames[i].position=positions[i]+Vector3.up*(Mathf.Sin(t*8+p)*.045f);}}
 }
}
