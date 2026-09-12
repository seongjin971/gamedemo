using UnityEngine;
using Vesper.Expansion.WeatherW10;
namespace Vesper.Expansion.WeatherW10 {
// Screen-space multiplicative flash: raises the rendered image itself without adding gray fog.
public sealed class WeatherW08Flash:MonoBehaviour {
 public WorldEnvironment world;public WeatherW07Flash comparisonGate;public Material screenMaterial;
 public float normalGain=.80f,strongGain=1.15f;
 void OnGUI(){
  if(!world||!screenMaterial||!comparisonGate||!comparisonGate.enabled||world.Flash<.0001f||Event.current.type!=EventType.Repaint)return;
  int old=GUI.depth;GUI.depth=-50;
  screenMaterial.SetFloat("_Gain",world.Flash*(world.StrongFlash?strongGain:normalGain));
  Graphics.DrawTexture(new Rect(0,0,Screen.width,Screen.height),Texture2D.whiteTexture,screenMaterial);
  GUI.depth=old;
 }
}
}
