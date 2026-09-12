Shader "Vesper/RuneGlow"
{
 Properties { [HDR] _BaseColor("Warm line halo",Color)=(1.6,.65,.15,.22) }
 SubShader {
  Tags {"RenderPipeline"="UniversalPipeline" "Queue"="Transparent" "RenderType"="Transparent"}
  Pass {
   Cull Off ZWrite Off ZTest LEqual Blend SrcAlpha One
   HLSLPROGRAM
   #pragma vertex vert
   #pragma fragment frag
   #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"
   CBUFFER_START(UnityPerMaterial)
   half4 _BaseColor;
   CBUFFER_END
   struct A {float4 p:POSITION;float2 uv:TEXCOORD0;};
   struct V {float4 p:SV_POSITION;float2 uv:TEXCOORD0;};
   V vert(A i){V o;o.p=TransformObjectToHClip(i.p.xyz);o.uv=i.uv;return o;}
   half4 frag(V i):SV_Target {float edge=abs(i.uv.y*2-1);float halo=exp2(-edge*edge*5)*(1-smoothstep(.78,1,edge));return half4(_BaseColor.rgb,_BaseColor.a*halo);}
   ENDHLSL
  }
 }
}
