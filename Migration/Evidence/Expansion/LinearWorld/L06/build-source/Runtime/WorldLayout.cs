using UnityEngine;
namespace Vesper.Expansion.LinearWorld {
// One straight route. Climate and terrain are spatial; the player never changes maps.
public static class WorldLayout {
 public const float WaterHeight=-.55f;
 public static readonly Vector2[] Bends={new Vector2(0,0),new Vector2(0,15),new Vector2(0,25),new Vector2(0,38),new Vector2(0,55),new Vector2(0,85),new Vector2(0,120),new Vector2(0,150),new Vector2(0,185),new Vector2(0,215),new Vector2(0,255),new Vector2(0,275),new Vector2(0,300)};
 static float S(float a,float b,float v)=>Mathf.SmoothStep(0,1,Mathf.InverseLerp(a,b,v));
 public static float Center(float d)=>0;
 public static float BridgeRise(float d)=>1.1f*S(9,18,d)*(1-S(32,41,d));
 public static float Level(float d)=>.8f+BridgeRise(d)+1.4f*S(45,105,d)+13*S(180,300,d);
 public static Vector3 Point(float d,float offset=0)=>new Vector3(offset,Level(d),-d);
 public static Vector3 Weights(float d){float rain=S(55,120,d),snow=S(190,255,d);return new Vector3(1-rain,rain*(1-snow),snow);}
 public static float SnowCover(float x,float d){float broad=S(188,262,d),patch=(Mathf.PerlinNoise(x*.28f+4,d*.23f)-.5f)*.48f;return S(.16f,.55f,broad+patch);}
 public static float ShoreShift(float x)=>(Mathf.Sin(x*.23f)*1.25f+Mathf.Sin(x*.57f)*.4f)*S(2.6f,7,Mathf.Abs(x));
 public static float NearShore(float x)=>18+ShoreShift(x);
 public static float FarShore(float x)=>32+ShoreShift(x);
 public static bool River(float x,float d)=>d>NearShore(x)&&d<FarShore(x);
 public static float Height(float x,float d){
  float edge=Mathf.Min(Mathf.Abs(d-NearShore(x)),Mathf.Abs(d-FarShore(x)));
  if(River(x,d))return Mathf.Lerp(-.43f,-2.15f,S(0,3,edge));
  float lateral=Mathf.Abs(x),level=Level(d);
  float texture=(Mathf.PerlinNoise(x*.10f+12,d*.065f+23)-.5f)*2.1f+(Mathf.PerlinNoise(x*.36f+18,d*.29f)-.5f)*.38f;
  float ground=level-BridgeRise(d)*S(2.15f,4.2f,lateral)+texture*S(2.15f,7,lateral);
  ground+=S(11,33,lateral)*(1.6f+3*S(190,280,d));
  if(d>9&&d<41)ground=Mathf.Lerp(ground,-.43f,(1-S(0,2.8f,edge))*S(2.2f,4,lateral));
  // Small level chapel footprint. Main path and adjacent soil meet without a step.
  float pad=S(2.7f,4,x)*(1-S(11.8f,14,x))*S(140,144,d)*(1-S(158,162,d));
  ground=Mathf.Lerp(ground,Level(150),pad);
  return ground;
 }
 public static string Region(float d)=>d<55?"WILLOWBANK":d<120?"DAMP WOOD":d<190?"VESPER ABBEY":d<255?"FROST ASCENT":"WHITE PASS";
}
}
