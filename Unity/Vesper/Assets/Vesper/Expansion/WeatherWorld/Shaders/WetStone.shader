Shader "Vesper/Weather/WetStone" {
Properties { _BaseMap("Weathered limestone",2D)="white"{} _WearMap("Rock atlas",2D)="gray"{} _SnowMap("Settled snow",2D)="white"{} _BaseColor("Stone tint",Color)=(.68,.71,.69,1) _Wetness("Rain film",Range(0,1))=.75 _ReflectionStrength("Reflection",Range(0,1))=.18 _PathWear("Soil at path edge",Float)=0 _Debug("Diagnostic",Float)=0 }
SubShader { Tags {"RenderPipeline"="UniversalPipeline" "RenderType"="Opaque"}
Pass { Name "ForwardLit" Tags {"LightMode"="UniversalForward"}
HLSLPROGRAM
#pragma target 3.5
#pragma vertex vert
#pragma fragment frag
#pragma multi_compile _ _MAIN_LIGHT_SHADOWS _MAIN_LIGHT_SHADOWS_CASCADE
#pragma multi_compile_fragment _ _SHADOWS_SOFT _SHADOWS_SOFT_LOW _SHADOWS_SOFT_MEDIUM _SHADOWS_SOFT_HIGH
#pragma multi_compile_fragment _ _SCREEN_SPACE_OCCLUSION
#pragma multi_compile_fog
#include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"
#include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Lighting.hlsl"
#include "StormAtmosphere.hlsl"
TEXTURE2D(_BaseMap);SAMPLER(sampler_BaseMap);
TEXTURE2D(_WearMap);SAMPLER(sampler_WearMap);TEXTURE2D(_SnowMap);SAMPLER(sampler_SnowMap);
TEXTURE2D(_VesperPlanarReflection);SAMPLER(sampler_VesperPlanarReflection);
float4x4 _VesperReflectionVP;float _VesperReflectionAvailable;
CBUFFER_START(UnityPerMaterial)
float4 _BaseMap_ST;half4 _BaseColor;half _Wetness,_ReflectionStrength,_Debug,_PathWear;
CBUFFER_END
struct A{float4 p:POSITION;float3 n:NORMAL;};struct V{float4 p:SV_POSITION;float3 w:TEXCOORD0;half3 n:TEXCOORD1;half fog:TEXCOORD2;};
V vert(A i){V o;o.w=TransformObjectToWorld(i.p.xyz);o.p=TransformWorldToHClip(o.w);o.n=TransformObjectToWorldNormal(i.n);o.fog=ComputeFogFactor(o.p.z);return o;}
half3 worn(float2 uv){return SAMPLE_TEXTURE2D(_WearMap,sampler_WearMap,float2(.503,.503)+frac(uv)*.494).rgb;}
half4 frag(V i):SV_Target{
 half3 n=normalize(i.n),weights=pow(abs(n),6);weights/=max(.001,weights.x+weights.y+weights.z);
 half3 tex=SAMPLE_TEXTURE2D(_BaseMap,sampler_BaseMap,i.w.zy*.42).rgb*weights.x+SAMPLE_TEXTURE2D(_BaseMap,sampler_BaseMap,i.w.xz*.42).rgb*weights.y+SAMPLE_TEXTURE2D(_BaseMap,sampler_BaseMap,i.w.xy*.42).rgb*weights.z;
 half3 coarse=worn(i.w.zy*.23)*weights.x+worn(i.w.xz*.23)*weights.y+worn(i.w.xy*.23)*weights.z;tex=lerp(tex,coarse,.74);
 half grain=dot(tex,half3(.3,.5,.2));half variation=dot(SAMPLE_TEXTURE2D(_BaseMap,sampler_BaseMap,i.w.xz*.11+float2(.37,.69)).rgb,half3(.3,.5,.2));
 half wet=_Wetness*saturate(n.y)*smoothstep(.19,.48,variation);
 half3 albedo=saturate((lerp(tex,grain.xxx,.45)-.25)*1.8+.25)*_BaseColor.rgb*lerp(1,.67,wet);
 half h1=dot(SAMPLE_TEXTURE2D(_BaseMap,sampler_BaseMap,i.w.xz*.42+float2(.003,0)).rgb,half3(.3,.5,.2));
 half h2=dot(SAMPLE_TEXTURE2D(_BaseMap,sampler_BaseMap,i.w.xz*.42+float2(0,.003)).rgb,half3(.3,.5,.2));
 half coarseH=dot(coarse,half3(.3,.5,.2));half cx=dot(worn(i.w.xz*.23+float2(.002,0)),half3(.3,.5,.2)),cz=dot(worn(i.w.xz*.23+float2(0,.002)),half3(.3,.5,.2));
 n=normalize(n+half3(coarseH-cx,0,coarseH-cz)*2.2*saturate(n.y));
 half edge=smoothstep(.85,1.65,abs(i.w.x)+(coarseH-.35)*.95)*_PathWear;
 half3 soil=SAMPLE_TEXTURE2D(_WearMap,sampler_WearMap,float2(.003,.503)+frac(i.w.xz*.23)*.494).rgb*half3(.82,.81,.74)*(1-_Wetness*.3);
 albedo=lerp(albedo,soil,edge);
 half snow=smoothstep(262,319,-i.w.z)*.93;albedo=lerp(albedo,SAMPLE_TEXTURE2D(_SnowMap,sampler_SnowMap,i.w.xz*.22).rgb*half3(.65,.71,.79),snow);wet*=1-snow;
 Light sun=GetMainLight(TransformWorldToShadowCoord(i.w));AmbientOcclusionFactor ao=GetScreenSpaceAmbientOcclusion(GetNormalizedScreenSpaceUV(i.p));
 half3 color=albedo*(SampleSH(n)*ao.indirectAmbientOcclusion+sun.color*saturate(dot(n,sun.direction))*sun.shadowAttenuation*ao.directAmbientOcclusion);
 half3 view=GetWorldSpaceNormalizeViewDir(i.w),h=normalize(view+sun.direction);
 color+=sun.color*pow(saturate(dot(n,h)),240)*.10*wet*sun.shadowAttenuation;
 float4 q=mul(_VesperReflectionVP,float4(i.w,1));float2 uv=q.xy/max(.001,q.w)*.5+.5;
 #if UNITY_UV_STARTS_AT_TOP
 uv.y=1-uv.y;
 #endif
 half3 reflected=SAMPLE_TEXTURE2D(_VesperPlanarReflection,sampler_VesperPlanarReflection,uv).rgb;
 reflected=reflected/(1+reflected);half f=_ReflectionStrength+pow(1-saturate(dot(n,view)),4)*.35;
 color=lerp(color,reflected,wet*f*_VesperReflectionAvailable);
 float3 toLamp=float3(4.05,4.2,-195.4)-i.w;half lamp=saturate(dot(n,normalize(toLamp)))*3/(1+dot(toLamp,toLamp));
 color+=albedo*half3(.7,.28,.055)*lamp;
 if(_Debug>.5&&_Debug<1.5)return half4(tex,1);
 if(_Debug>1.5&&_Debug<2.5)return half4(albedo,1);
 if(_Debug>2.5&&_Debug<3.5)return half4(n*.5+.5,1);
 if(_Debug>3.5)return half4(reflected,1);
 color+=albedo*WeatherSurfaceLight(i.w)+WeatherWetFlash(n,wet);
 return half4(WeatherFog(color,i.fog,i.w),1);
}
ENDHLSL
}
UsePass "Universal Render Pipeline/Lit/ShadowCaster"
UsePass "Universal Render Pipeline/Lit/DepthOnly"
UsePass "Universal Render Pipeline/Lit/DepthNormals"
}
}
