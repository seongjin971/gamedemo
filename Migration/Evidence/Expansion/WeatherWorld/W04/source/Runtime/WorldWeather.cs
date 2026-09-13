using UnityEngine;
namespace Vesper.Expansion.WeatherWorld {
public sealed class WorldWeather:MonoBehaviour {
 public WorldEnvironment world;public ParticleSystem splashes;float splashRemainder;
 readonly ParticleSystem.Particle[] particles=new ParticleSystem.Particle[4096];
 public float RainWeight(Vector3 p)=>world.shelter.Contains(p)?0:WorldLayout.Weights(-p.z).y;
 public float SnowWeight(Vector3 p)=>world.shelter.Contains(p)?0:WorldLayout.Weights(-p.z).z;
 public int VisibleParticles(ParticleSystem system,bool snow=false){if(!system)return 0;int n=system.GetParticles(particles),visible=0;for(int i=0;i<n;i++)if((snow?SnowWeight(particles[i].position):RainWeight(particles[i].position))>.1f)visible++;return visible;}
 void LateUpdate(){
  if(!world||!world.player)return;Shader.SetGlobalVector("_WorldShelterMin",world.shelter.min);Shader.SetGlobalVector("_WorldShelterMax",world.shelter.max);
  if(!splashes)return;splashRemainder+=Time.deltaTime*180*world.Weights.y;
  int count=Mathf.Min(10,Mathf.FloorToInt(splashRemainder));splashRemainder-=count;
  for(int i=0;i<count;i++){var circle=Random.insideUnitCircle*15;var origin=world.player.transform.position+new Vector3(circle.x,22,circle.y);if(!Physics.Raycast(origin,Vector3.down,out var hit,55,WorldMotor.SurfaceMask|WorldMotor.BlockMask,QueryTriggerInteraction.Ignore)||hit.normal.y<.7f)continue;var p=hit.point+Vector3.up*.04f;if(RainWeight(p)<.1f)continue;var emit=new ParticleSystem.EmitParams{position=p,velocity=Vector3.zero,startLifetime=Random.Range(.42f,.68f),startSize=Random.Range(.18f,.38f),startColor=new Color(.85f,.92f,1,Random.Range(.6f,.9f))};splashes.Emit(emit,1);}
 }
}
}
