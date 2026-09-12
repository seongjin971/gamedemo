Shader "Vesper/ValleyMist" {
 Properties { [HDR] _BaseColor("Mist color / opacity",Color)=(.032,.058,.087,.28) }
 SubShader {Tags {"RenderPipeline"="UniversalPipeline" "Queue"="Transparent+20" "RenderType"="Transparent"} Pass {
 Cull Off ZWrite Off Blend SrcAlpha OneMinusSrcAlpha
 HLSLPROGRAM
 #pragma vertex vert
 #pragma fragment frag
 #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"
 CBUFFER_START(UnityPerMaterial)
 half4 _BaseColor;
 CBUFFER_END
 struct A {float4 p:POSITION;float2 uv:TEXCOORD0;}; struct V {float4 p:SV_POSITION;float2 uv:TEXCOORD0;};
 V vert(A i){V o;o.p=TransformObjectToHClip(i.p.xyz);o.uv=i.uv;return o;}
 float h(float2 p){return frac(sin(dot(p,float2(127.1,311.7)))*43758.54);}
 float n(float2 p){float2 i=floor(p),f=frac(p);f=f*f*(3-2*f);return lerp(lerp(h(i),h(i+float2(1,0)),f.x),lerp(h(i+float2(0,1)),h(i+1),f.x),f.y);}
 half4 frag(V i):SV_Target {float2 p=i.uv*float2(6,3);float f=n(p+float2(_Time.y*.017,0))*.65+n(p*2.1-float2(_Time.y*.012,0))*.35;float edge=pow(saturate(sin(i.uv.x*PI)*sin(i.uv.y*PI)),1.2);return half4(_BaseColor.rgb,smoothstep(.32,.72,f)*edge*_BaseColor.a);}
 ENDHLSL
 }}
}
