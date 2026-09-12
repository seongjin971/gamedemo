Shader "Vesper/ShallowWater" {
 Properties { _Mineral("Shore breakup",2D)="gray"{} }
 SubShader {Tags {"RenderPipeline"="UniversalPipeline" "Queue"="Transparent-10" "RenderType"="Transparent"} Pass {
 Cull Off ZWrite Off Blend SrcAlpha OneMinusSrcAlpha
 HLSLPROGRAM
 #pragma vertex vert
 #pragma fragment frag
 #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"
 TEXTURE2D(_Mineral);SAMPLER(sampler_Mineral);
 TEXTURE2D(_VesperPlanarReflection);SAMPLER(sampler_VesperPlanarReflection);
 float4x4 _VesperReflectionVP;float _VesperReflectionAvailable;
 struct A{float4 p:POSITION;float2 uv:TEXCOORD0;};
 struct V{float4 p:SV_POSITION;float3 world:TEXCOORD0;float2 uv:TEXCOORD1;};
 V vert(A i){V o;o.world=TransformObjectToWorld(i.p.xyz);o.p=TransformWorldToHClip(o.world);o.uv=i.uv;return o;}
 half4 frag(V i):SV_Target{
  float2 q=i.uv*2-1;
  float mineral=SAMPLE_TEXTURE2D(_Mineral,sampler_Mineral,i.world.xz*.47).r;
  float edge=1-dot(q,q)+(mineral-.22)*1.2+sin(q.x*9+q.y*7)*.09;
  float shape=smoothstep(.08,.25,edge);clip(shape-.01);
  float4 reflected=mul(_VesperReflectionVP,float4(i.world,1));
  float2 uv=reflected.xy/reflected.w*.5+.5;
  #if UNITY_UV_STARTS_AT_TOP
  uv.y=1-uv.y;
  #endif
  float wave=sin(i.world.z*95+sin(i.world.x*21)+_Time.y*.9);
  uv.x+=wave*.0012;
  half3 reflection=SAMPLE_TEXTURE2D(_VesperPlanarReflection,sampler_VesperPlanarReflection,uv).rgb*.30;
  for(int k=1;k<=3;k++){
   float2 offset=float2(0,k*.013);
   reflection+=(SAMPLE_TEXTURE2D(_VesperPlanarReflection,sampler_VesperPlanarReflection,uv+offset).rgb+SAMPLE_TEXTURE2D(_VesperPlanarReflection,sampler_VesperPlanarReflection,uv-offset).rgb)*.116666;
  }
  reflection=max(reflection,half3(.026,.055,.078));
  float ripple=smoothstep(-.1,.55,wave+sin(i.world.x*37-i.world.z*4)*.35);
  float bright=smoothstep(.06,.22,dot(reflection,half3(.2126,.7152,.0722)));
  float alpha=shape*(.16+bright*.58)*(.15+ripple*.85)*_VesperReflectionAvailable;
  return half4(reflection,alpha);
 }
 ENDHLSL
 }}
}
