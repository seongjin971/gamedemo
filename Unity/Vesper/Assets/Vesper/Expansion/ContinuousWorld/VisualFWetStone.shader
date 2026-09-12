Shader "Vesper/VisualF/WetStone" {
Properties { _BaseMap("Stone surface",2D)="white"{} _BaseColor("Wet stone tint",Color)=(.62,.68,.71,1) _Wetness("Wetness",Range(0,1))=.75 _ReflectionStrength("Rain film reflection",Range(0,1))=.22 _Overlay("Feathered rain overlay",Float)=0 _Diagnostic("QA channels",Float)=0 }
SubShader { Tags {"RenderPipeline"="UniversalPipeline" "RenderType"="Opaque"}
Pass {Name "ForwardLit" Tags {"LightMode"="UniversalForward"} Blend SrcAlpha OneMinusSrcAlpha
HLSLPROGRAM
#pragma target 3.5
#pragma vertex vert
#pragma fragment frag
#pragma multi_compile _ _MAIN_LIGHT_SHADOWS _MAIN_LIGHT_SHADOWS_CASCADE
#pragma multi_compile_fragment _ _SHADOWS_SOFT _SHADOWS_SOFT_LOW _SHADOWS_SOFT_MEDIUM _SHADOWS_SOFT_HIGH
#pragma multi_compile_fog
#pragma multi_compile_fragment _ _SCREEN_SPACE_OCCLUSION
#pragma multi_compile _ _ADDITIONAL_LIGHTS
#pragma multi_compile _ _CLUSTER_LIGHT_LOOP
#define _ENVIRONMENTREFLECTIONS_OFF 1
#include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"
#include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Lighting.hlsl"
TEXTURE2D(_BaseMap);SAMPLER(sampler_BaseMap);
TEXTURE2D(_VesperPlanarReflection);SAMPLER(sampler_VesperPlanarReflection);float4x4 _VesperReflectionVP;float _VesperReflectionAvailable;
CBUFFER_START(UnityPerMaterial)
float4 _BaseMap_ST;half4 _BaseColor;half _Wetness,_ReflectionStrength,_Overlay,_Diagnostic;
CBUFFER_END
struct A{float4 p:POSITION;float3 n:NORMAL;float2 uv:TEXCOORD0;half4 c:COLOR;};struct V{float4 p:SV_POSITION;float3 w:TEXCOORD0;half3 n:TEXCOORD1;float2 uv:TEXCOORD2;half fog:TEXCOORD3;half alpha:TEXCOORD4;};
V vert(A i){V o;o.w=TransformObjectToWorld(i.p.xyz);o.p=TransformWorldToHClip(o.w);o.n=TransformObjectToWorldNormal(i.n);o.uv=TRANSFORM_TEX(i.uv,_BaseMap);o.fog=ComputeFogFactor(o.p.z);o.alpha=lerp(1,i.c.a,_Overlay);return o;}
half4 frag(V i):SV_Target{
 // World-scale stone detail avoids tiny smart-UV islands reducing the generated 2K surface to a flat average.
 float2 stoneUV=lerp(i.w.xz*.46,i.uv,_Overlay);
 half3 tex=SAMPLE_TEXTURE2D(_BaseMap,sampler_BaseMap,stoneUV).rgb;half grain=dot(tex,half3(.3,.5,.2));half h1=dot(SAMPLE_TEXTURE2D(_BaseMap,sampler_BaseMap,stoneUV+float2(.002,0)).rgb,half3(.3,.5,.2));half h2=dot(SAMPLE_TEXTURE2D(_BaseMap,sampler_BaseMap,stoneUV+float2(0,.002)).rgb,half3(.3,.5,.2));
 // This material is restricted to the horizontal abbey floor and rain films.
 // Imported averaged bevel normals must not turn each metre-wide slab into a glossy cushion.
 half3 n=normalize(half3(0,1,0)+half3(grain-h1,0,grain-h2)*3.8);half3 v=GetWorldSpaceNormalizeViewDir(i.w);half3 albedo=saturate((lerp(tex,half3(grain,grain,grain),.65)-.22)*1.2+.22)*_BaseColor.rgb;
 half stoneVariation=dot(SAMPLE_TEXTURE2D(_BaseMap,sampler_BaseMap,i.w.xz*.115+float2(.23,.67)).rgb,half3(.3,.5,.2));
 half wet=_Wetness*lerp(.55,1,smoothstep(.12,.4,stoneVariation))*saturate(n.y*2-1);
 if(_Diagnostic>.5&&_Diagnostic<1.5)return half4(albedo,1);
 if(_Diagnostic>1.5&&_Diagnostic<2.5)return half4(n*.5+.5,1);
 if(_Diagnostic>2.5)return half4(wet,wet,wet,1);
 InputData inputData=(InputData)0;inputData.positionWS=i.w;inputData.normalWS=n;inputData.viewDirectionWS=v;inputData.shadowCoord=TransformWorldToShadowCoord(i.w);inputData.bakedGI=SampleSH(n);inputData.normalizedScreenSpaceUV=GetNormalizedScreenSpaceUV(i.p);inputData.shadowMask=half4(1,1,1,1);
 SurfaceData surface=(SurfaceData)0;surface.albedo=albedo*lerp(1,.72,wet);surface.specular=half3(.04,.04,.04);surface.smoothness=lerp(.28,.86,wet);surface.normalTS=half3(0,0,1);surface.occlusion=1;surface.alpha=1;
 half3 color=UniversalFragmentPBR(inputData,surface).rgb;
 float4 q=mul(_VesperReflectionVP,float4(i.w,1));float2 uv=q.xy/max(.001,q.w)*.5+.5;
 #if UNITY_UV_STARTS_AT_TOP
 uv.y=1-uv.y;
 #endif
 uv+=n.xz*.006;half3 reflected=SAMPLE_TEXTURE2D(_VesperPlanarReflection,sampler_VesperPlanarReflection,uv).rgb;half fresnel=_ReflectionStrength+(1-_ReflectionStrength)*pow(1-saturate(dot(v,n)),4);color=lerp(color,reflected,wet*fresnel*_VesperReflectionAvailable);
 return half4(MixFog(color,i.fog),i.alpha);
}
ENDHLSL
}
UsePass "Universal Render Pipeline/Lit/ShadowCaster"
UsePass "Universal Render Pipeline/Lit/DepthOnly"
UsePass "Universal Render Pipeline/Lit/DepthNormals"
}
}
