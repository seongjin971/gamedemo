using UnityEngine;
namespace Vesper.Expansion.ContinuousWorld {
// Shared authored corridor: render mesh, collision and route landmarks derive from this definition.
public static class WorldLayout {
 public const float WaterHeight=-.95f;
 public static readonly Vector2[] Bends={new Vector2(0,0),new Vector2(-8,30),new Vector2(-8,62),new Vector2(12,85),new Vector2(-22,110),new Vector2(0,145),new Vector2(20,175),new Vector2(10,210),new Vector2(-24,245),new Vector2(-4,275),new Vector2(26,305),new Vector2(0,342),new Vector2(-12,375)};
 public static float Center(float d){for(int i=1;i<Bends.Length;i++)if(d<=Bends[i].y)return Mathf.Lerp(Bends[i-1].x,Bends[i].x,Mathf.SmoothStep(0,1,Mathf.InverseLerp(Bends[i-1].y,Bends[i].y,d)));return Bends[Bends.Length-1].x;}
 public static float BridgeRise(float d)=>2*Mathf.SmoothStep(0,1,Mathf.InverseLerp(25,41.5f,d))*(1-Mathf.SmoothStep(0,1,Mathf.InverseLerp(55.5f,71,d)));
 public static float Level(float d){if(d<95)return .8f+BridgeRise(d)+Mathf.SmoothStep(0,2,Mathf.InverseLerp(65,95,d));if(d<150)return 2.8f+Mathf.SmoothStep(0,6.2f,Mathf.InverseLerp(95,150,d));if(d<210)return 9;return 9+Mathf.SmoothStep(0,46,Mathf.InverseLerp(210,375,d));}
 public static Vector3 Point(float d,float offset=0){return new Vector3(Center(d)+offset,Level(d),-d);}
 public static Vector3 Weights(float d){float rain=Mathf.SmoothStep(0,1,Mathf.InverseLerp(95,145,d));float snow=Mathf.SmoothStep(0,1,Mathf.InverseLerp(242,292,d));return new Vector3(1-rain,rain*(1-snow),snow);}
 public static float ShoreShift(float x){return (Mathf.Sin(x*.17f)*1.3f+Mathf.Sin(x*.37f)*.55f)*Mathf.SmoothStep(0,1,Mathf.InverseLerp(5.5f,14,Mathf.Abs(x-Center(48.5f))));}
 public static float NearShore(float x)=>43+ShoreShift(x)-6*Mathf.SmoothStep(0,1,Mathf.InverseLerp(4.5f,8,Center(48.5f)-x));
 public static float FarShore(float x)=>54+ShoreShift(x)+6*Mathf.SmoothStep(0,1,Mathf.InverseLerp(3.2f,6,Mathf.Abs(x-Center(48.5f))));
 public static bool River(float x,float d){return d>NearShore(x)&&d<FarShore(x);}
 public static float Height(float x,float d){
  float dist=Mathf.Abs(x-Center(d)),level=Level(d);
  // The bridge is straight while the trail bends. Give both exits a supported apron.
  if(d>34&&d<67)dist=Mathf.Min(dist,Mathf.Abs(x-Center(48.5f)));
  if(River(x,d)){float edge=Mathf.Min(d-NearShore(x),FarShore(x)-d);return Mathf.Lerp(-.7f,-3,Mathf.SmoothStep(0,1,Mathf.InverseLerp(0,1.8f,edge)));}
  float terrain=(Mathf.PerlinNoise(x*.036f+18,d*.031f+11)-.5f)*5+(Mathf.PerlinNoise(x*.1f+47,d*.09f+24)-.5f)*1.3f;
  float fringe=Mathf.SmoothStep(0,1,Mathf.InverseLerp(5.2f,16,dist));
  float mass=Mathf.Pow(Mathf.InverseLerp(14,65,dist),1.5f)*(d>220?30:11);
  float natural=level-BridgeRise(d)*Mathf.SmoothStep(0,1,Mathf.InverseLerp(3.4f,7,dist))+terrain*fringe+mass-24*Mathf.SmoothStep(0,1,Mathf.InverseLerp(383,396,d));
  natural-=24*Mathf.SmoothStep(0,1,Mathf.InverseLerp(355,372,d))*Mathf.SmoothStep(0,1,Mathf.InverseLerp(8,16,Center(d)-x));
  float pad=Mathf.SmoothStep(0,1,Mathf.InverseLerp(21,24,x))*(1-Mathf.SmoothStep(0,1,Mathf.InverseLerp(42,49,x)))*Mathf.SmoothStep(0,1,Mathf.InverseLerp(158,166,d))*(1-Mathf.SmoothStep(0,1,Mathf.InverseLerp(200,209,d)));
  natural=Mathf.Lerp(natural,9,pad);
  // Exposed banks taper into the shallow shelf; bridge approaches retain their full support.
  if(d>27&&d<69){float edge=d<NearShore(x)?NearShore(x)-d:d-FarShore(x);float shore=(1-Mathf.SmoothStep(0,1,Mathf.InverseLerp(0,2.8f,edge)))*Mathf.SmoothStep(0,1,Mathf.InverseLerp(3.8f,6.5f,Mathf.Abs(x-Center(48.5f))));natural=Mathf.Lerp(natural,-.7f,shore);}
  if(d>=41.5f&&d<=55.5f&&Mathf.Abs(x-Center(48.5f))<3.2f)natural=Mathf.Min(natural,Level(d)-.14f);
  return natural;
 }
 public static string Region(float d){return d<95?"THE WILLOWBANK":d<145?"THE RAINWOOD":d<220?"VESPER ABBEY":d<292?"THE FROST ASCENT":d<370?"THE WHITE PASS":"THE WHITE PASS / OVERLOOK";}
}
}
