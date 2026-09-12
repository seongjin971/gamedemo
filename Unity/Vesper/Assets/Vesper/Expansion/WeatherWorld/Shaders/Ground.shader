Shader "Vesper/Weather/Ground" {
Properties { _BaseMap("Surface atlas",2D)="white"{} _MossMap("Moss bed",2D)="gray"{} _SnowMap("Snow surface",2D)="white"{} _PackedMap("Compacted snow",2D)="white"{} _StoneMap("Stone surface",2D)="white"{} _BaseColor("Tint",Color)=(1,1,1,1) _DetailScale("Detail scale",Float)=.27 _NormalStrength("Normal detail",Float)=.28 _Diagnostic("QA channels",Float)=0 }
SubShader { Tags {"RenderType"="Opaque" "RenderPipeline"="UniversalPipeline"}
Pass {Name "ForwardLit" Tags {"LightMode"="UniversalForward"}
HLSLPROGRAM
#pragma target 3.5
#pragma vertex vert
#pragma fragment frag
#pragma multi_compile _ _MAIN_LIGHT_SHADOWS _MAIN_LIGHT_SHADOWS_CASCADE _MAIN_LIGHT_SHADOWS_SCREEN
#pragma multi_compile_fragment _ _SHADOWS_SOFT _SHADOWS_SOFT_LOW _SHADOWS_SOFT_MEDIUM _SHADOWS_SOFT_HIGH
#pragma multi_compile_fog
#pragma multi_compile_fragment _ _SCREEN_SPACE_OCCLUSION
#include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"
#include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Lighting.hlsl"
#include "StormAtmosphere.hlsl"
TEXTURE2D(_BaseMap);SAMPLER(sampler_BaseMap);
TEXTURE2D(_MossMap);SAMPLER(sampler_MossMap);
TEXTURE2D(_SnowMap);SAMPLER(sampler_SnowMap);TEXTURE2D(_PackedMap);SAMPLER(sampler_PackedMap);TEXTURE2D(_StoneMap);SAMPLER(sampler_StoneMap);
CBUFFER_START(UnityPerMaterial)
float4 _BaseMap_ST;half4 _BaseColor;float _DetailScale,_NormalStrength,_Diagnostic;
CBUFFER_END
struct A{float4 p:POSITION;float3 n:NORMAL;half4 c:COLOR;};
struct V{float4 p:SV_POSITION;float3 w:TEXCOORD0;half3 n:TEXCOORD1;half4 c:COLOR;half fog:TEXCOORD2;};
V vert(A i){V o;o.w=TransformObjectToWorld(i.p.xyz);o.p=TransformWorldToHClip(o.w);o.n=TransformObjectToWorldNormal(i.n);o.c=i.c;o.fog=ComputeFogFactor(o.p.z);return o;}
half3 tile(float2 uv,float2 quadrant){return SAMPLE_TEXTURE2D(_BaseMap,sampler_BaseMap,quadrant+(.003+frac(uv)*.994)*.5).rgb;}
half4 frag(V i):SV_Target{
 float2 uv=i.w.xz*_DetailScale;half path=i.c.r,snow=i.c.g,rock=i.c.b,wet=i.c.a;
 if(_Diagnostic>.5)return half4(path,snow,rock,1);
 half3 soil=tile(uv,float2(0,.5));half3 weights=pow(abs(normalize(i.n)),4);weights/=max(.001,weights.x+weights.y+weights.z);half3 stone=SAMPLE_TEXTURE2D(_StoneMap,sampler_StoneMap,i.w.zy*_DetailScale*.67).rgb*weights.x+SAMPLE_TEXTURE2D(_StoneMap,sampler_StoneMap,i.w.xz*_DetailScale*.67).rgb*weights.y+SAMPLE_TEXTURE2D(_StoneMap,sampler_StoneMap,i.w.xy*_DetailScale*.67).rgb*weights.z;half3 ice=SAMPLE_TEXTURE2D(_SnowMap,sampler_SnowMap,uv*.8).rgb;
 half3 moss=SAMPLE_TEXTURE2D(_MossMap,sampler_MossMap,uv*.77).rgb;half3 grass=lerp(soil*half3(.49,.68,.38),moss*half3(.72,.9,.58),.58);half3 dry=lerp(grass,soil*half3(.82,.81,.74),path);dry=lerp(dry,stone*.75,rock);
 half3 packed=SAMPLE_TEXTURE2D(_PackedMap,sampler_PackedMap,uv).rgb;half3 packedSnow=lerp(ice,packed,path*.85)*.98*lerp(half3(1,1,1),half3(.78,.83,.88),path*.95);half3 albedo=lerp(dry*(1-wet*.3),packedSnow,snow)*_BaseColor.rgb;
 half height=dot(soil,half3(.3,.5,.2));half dx=dot(tile(uv+float2(.003,0),float2(0,.5)),half3(.3,.5,.2))-height;half dz=dot(tile(uv+float2(0,.003),float2(0,.5)),half3(.3,.5,.2))-height;
 half2 drift=half2(cos(i.w.x*.55+i.w.z*.19),sin(i.w.z*.47-i.w.x*.15))*.028*snow*(1-path*.55);
 half3 n=normalize(i.n+half3(-dx+drift.x,0,-dz+drift.y)*_NormalStrength*10*(1-snow*.75));Light light=GetMainLight(TransformWorldToShadowCoord(i.w));
 AmbientOcclusionFactor ao=GetScreenSpaceAmbientOcclusion(GetNormalizedScreenSpaceUV(i.p));half3 ambient=SampleSH(n)*ao.indirectAmbientOcclusion;half3 color=albedo*(ambient+light.color*saturate(dot(n,light.direction))*light.shadowAttenuation*ao.directAmbientOcclusion);
 half3 v=GetWorldSpaceNormalizeViewDir(i.w),h=normalize(light.direction+v);half glint=pow(saturate(dot(n,h)),lerp(30,130,wet))*.09*wet;
 color+=light.color*glint*light.shadowAttenuation;
 color+=albedo*WeatherSurfaceLight(i.w)+WeatherWetFlash(n,wet*(1-snow)*.35);
 return half4(WeatherFog(color,i.fog,i.w),1);
}
ENDHLSL
}
UsePass "Universal Render Pipeline/Lit/ShadowCaster"
UsePass "Universal Render Pipeline/Lit/DepthOnly"
UsePass "Universal Render Pipeline/Lit/DepthNormals"
}
}
