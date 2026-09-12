Shader "Vesper/ContinuousRiver" {
Properties { _ShallowColor("Shallows",Color)=(.13,.37,.35,1) _DeepColor("Deep water",Color)=(.035,.16,.19,1) _ReflectionStrength("Reflection",Range(0,1))=.8 }
SubShader { Tags {"RenderPipeline"="UniversalPipeline" "Queue"="Transparent-10" "RenderType"="Transparent"}
Pass { Name "River surface" Cull Off ZWrite Off Blend SrcAlpha OneMinusSrcAlpha
HLSLPROGRAM
#pragma target 3.5
#pragma vertex vert
#pragma fragment frag
#pragma multi_compile _ _MAIN_LIGHT_SHADOWS _MAIN_LIGHT_SHADOWS_CASCADE
#pragma multi_compile_fragment _ _SHADOWS_SOFT _SHADOWS_SOFT_LOW _SHADOWS_SOFT_MEDIUM _SHADOWS_SOFT_HIGH
#pragma multi_compile_fog
#include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"
#include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Lighting.hlsl"
#include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/DeclareDepthTexture.hlsl"
#include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/DeclareOpaqueTexture.hlsl"
TEXTURE2D(_VesperPlanarReflection);SAMPLER(sampler_VesperPlanarReflection);
float4x4 _VesperReflectionVP;float _VesperReflectionAvailable;
CBUFFER_START(UnityPerMaterial)
half4 _ShallowColor,_DeepColor;half _ReflectionStrength;
CBUFFER_END
struct A{float4 p:POSITION;};struct V{float4 p:SV_POSITION;float3 w:TEXCOORD0;half fog:TEXCOORD1;};
V vert(A i){V o;o.w=TransformObjectToWorld(i.p.xyz);o.p=TransformWorldToHClip(o.w);o.fog=ComputeFogFactor(o.p.z);return o;}
float waterHash(float2 p){p=frac(p*float2(.1031,.11369));p+=dot(p,p.yx+33.33);return frac((p.x+p.y)*p.x);}
float2 waterGradient(float2 p){float2 g=floor(p),f=frac(p),u=f*f*(3-2*f),du=6*f*(1-f);float a=waterHash(g),b=waterHash(g+float2(1,0)),c=waterHash(g+float2(0,1)),d=waterHash(g+1);return float2(lerp(b-a,d-c,u.y)*du.x,lerp(c-a,d-b,u.x)*du.y);}
half4 frag(V i):SV_Target{
 float2 uv=GetNormalizedScreenSpaceUV(i.p);float depth=SampleSceneDepth(uv);
 #if !UNITY_REVERSED_Z
 depth=lerp(UNITY_NEAR_CLIP_VALUE,1,depth);
 #endif
 float3 bed=ComputeWorldSpacePosition(uv,depth,UNITY_MATRIX_I_VP);float thickness=max(0,i.w.y-bed.y);
 float2 flow=i.w.xz+float2(_Time.y*.16,-_Time.y*.09);
 float2 ripple=waterGradient(flow*.83)*.12+waterGradient(flow*2.71+17.4)*.055+waterGradient(flow*8.17-4.8)*.018;
 half3 n=normalize(half3(ripple.x,1,ripple.y));
 half3 view=GetWorldSpaceNormalizeViewDir(i.w);half fresnel=.075+.925*pow(1-saturate(dot(n,view)),5);
 float4 q=mul(_VesperReflectionVP,float4(i.w,1));float2 ruv=q.xy/max(.001,q.w)*.5+.5;
 #if UNITY_UV_STARTS_AT_TOP
 ruv.y=1-ruv.y;
 #endif
 ruv+=n.xz*.022;half3 reflected=SAMPLE_TEXTURE2D(_VesperPlanarReflection,sampler_VesperPlanarReflection,ruv).rgb;
 half3 behind=SampleSceneColor(uv+n.xz*.006*saturate(thickness));
 half absorption=1-exp(-thickness*.75);half3 body=lerp(behind,lerp(_ShallowColor.rgb,_DeepColor.rgb,saturate(thickness*.28)),absorption);
 Light light=GetMainLight(TransformWorldToShadowCoord(i.w));half3 h=normalize(view+light.direction);half spec=pow(saturate(dot(n,h)),1400)*.18;
 body*=lerp(.42,1,light.shadowAttenuation);
 half3 color=lerp(body,reflected,fresnel*_ReflectionStrength*_VesperReflectionAvailable)+light.color*spec*light.shadowAttenuation;
 // A thin quiet contact edge, not white foam across the whole river.
 half edge=(1-smoothstep(.03,.18,thickness))*.06;color+=edge;
 return half4(MixFog(color,i.fog),saturate(thickness*5+.25));
}
ENDHLSL
}
}
}
