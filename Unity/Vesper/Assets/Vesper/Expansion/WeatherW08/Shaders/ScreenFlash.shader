Shader "Vesper/WeatherW08/ScreenFlash" {
 Properties{_MainTex("Source",2D)="white"{} _Gain("Peak gain",Float)=0}
 SubShader{Tags{"Queue"="Overlay" "RenderType"="Transparent"} Cull Off ZWrite Off ZTest Always
  Blend DstColor One
  Pass{
   CGPROGRAM
   #pragma vertex vert
   #pragma fragment frag
   #include "UnityCG.cginc"
   float _Gain;
   struct V{float4 vertex:SV_POSITION;};
   V vert(appdata_base a){V o;o.vertex=UnityObjectToClipPos(a.vertex);return o;}
   half4 frag(V i):SV_Target{return half4(half3(.92,.98,1.04)*_Gain,0);}
   ENDCG
  }
 }
}
