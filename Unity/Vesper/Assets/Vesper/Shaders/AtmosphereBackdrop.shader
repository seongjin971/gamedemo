Shader "Vesper/AtmosphereBackdrop" {
 Properties { _BaseMap("City panorama",2D)="black"{} _BaseColor("Tint",Color)=(.6,.65,.7,1) }
 SubShader { Tags {"RenderPipeline"="UniversalPipeline" "Queue"="Background"} Pass {
 Cull Off ZWrite Off
 HLSLPROGRAM
 #pragma vertex vert
 #pragma fragment frag
 #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"
 TEXTURE2D(_BaseMap); SAMPLER(sampler_BaseMap);
 CBUFFER_START(UnityPerMaterial)
 half4 _BaseColor;
 CBUFFER_END
 struct A {float4 p:POSITION; float2 uv:TEXCOORD0;};
 struct V {float4 p:SV_POSITION;float2 uv:TEXCOORD0;};
 V vert(A i){V o;i.p.xy*=1.6;o.p=TransformObjectToHClip(i.p.xyz);o.uv=(i.uv-.5)*1.6+.5;return o;}
 half4 frag(V i):SV_Target{
  float2 originalUV=i.uv;
  i.uv=saturate(i.uv);
  half right=smoothstep(.35,.8,i.uv.x);
  float2 blur=float2(.0018,.0012)*right;
  half3 c=SAMPLE_TEXTURE2D(_BaseMap,sampler_BaseMap,i.uv).rgb*.4;
  c+=(SAMPLE_TEXTURE2D(_BaseMap,sampler_BaseMap,i.uv+blur).rgb+SAMPLE_TEXTURE2D(_BaseMap,sampler_BaseMap,i.uv-blur).rgb)*.3;
  c*=_BaseColor.rgb;c=lerp(c,dot(c,half3(.2126,.7152,.0722)).xxx,.05);
  c=lerp(c,half3(.020,.046,.063),right*.42);
  float outside=max(max(-originalUV.x,originalUV.x-1),max(-originalUV.y,originalUV.y-1));
  c=lerp(c,half3(.012,.027,.040),smoothstep(0,.25,outside)*.8);
  return half4(lerp(c,half3(.012,.027,.040),.03),1);
 }
 ENDHLSL
 }}
}
