using UnityEngine;
using Original = Vesper.Expansion.LinearWorld.WorldLayout;
namespace Vesper.Expansion.WeatherWorld {
// Adds 48 metres before the rain while keeping the existing landmarks intact.
public static class WorldLayout {
 public const float WaterHeight=Original.WaterHeight;
 public static float S(float a,float b,float v)=>Mathf.SmoothStep(0,1,Mathf.InverseLerp(a,b,v));
 public static float FromSource(float d)=>d<=48?d:d<90?48+(d-48)*90/42:d+48;
 public static float ToSource(float d)=>d<=48?d:d<138?48+(d-48)*42/90:d-48;
 public static Vector3 Map(Vector3 p){p.z=-FromSource(-p.z);return p;}
 public static float Level(float d)=>Original.Level(ToSource(d));
 public static float Height(float x,float d)=>Original.Height(x,ToSource(d));
 public static bool River(float x,float d)=>Original.River(x,ToSource(d));
 public static Vector3 Point(float d,float offset=0)=>new Vector3(offset,Level(d),-d);
 public static float SnowCover(float x,float d)=>Original.SnowCover(x,ToSource(d));
 public static float Darkness(float d)=>S(46,73,d);
 public static Vector3 Weights(float d){float rain=S(112,168,d),snow=S(238,303,d);return new Vector3(1-rain,rain*(1-snow),snow);}
 public static string Region(float d)=>d<55?"WILLOWBANK":d<112?"STORMWATCH GROVE":d<168?"RAINWOOD":d<238?"VESPER ABBEY":d<303?"NIGHTFALL ASCENT":"MIDNIGHT PASS";
}
}
