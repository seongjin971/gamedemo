Shader "Vesper/ContinuousTerrain" {
Properties { _BaseMap("Albedo",2D)="white"{} _BaseColor("Tint",Color)=(1,1,1,1) }
SubShader { Tags { "RenderType"="Opaque" "RenderPipeline"="UniversalPipeline" }
Pass { Name "ForwardLit" Tags {"LightMode"="UniversalForward"}
HLSLPROGRAM
#pragma vertex vert
#pragma fragment frag
#pragma multi_compile _ _MAIN_LIGHT_SHADOWS _MAIN_LIGHT_SHADOWS_CASCADE _MAIN_LIGHT_SHADOWS_SCREEN
#pragma multi_compile_fragment _ _SHADOWS_SOFT
#pragma multi_compile_fog
#include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"
#include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Lighting.hlsl"
struct A{float4 positionOS:POSITION;float3 normalOS:NORMAL;float2 uv:TEXCOORD0;half4 color:COLOR;};
struct V{float4 positionCS:SV_POSITION;float3 positionWS:TEXCOORD0;half3 normalWS:TEXCOORD1;float2 uv:TEXCOORD2;half4 color:COLOR;half fog:TEXCOORD3;};
TEXTURE2D(_BaseMap);SAMPLER(sampler_BaseMap);
CBUFFER_START(UnityPerMaterial)
float4 _BaseMap_ST;half4 _BaseColor;
CBUFFER_END
V vert(A i){V o;VertexPositionInputs p=GetVertexPositionInputs(i.positionOS.xyz);o.positionCS=p.positionCS;o.positionWS=p.positionWS;o.normalWS=TransformObjectToWorldNormal(i.normalOS);o.uv=TRANSFORM_TEX(i.uv,_BaseMap);o.color=i.color;o.fog=ComputeFogFactor(p.positionCS.z);return o;}
half4 frag(V i):SV_Target{half3 n=normalize(i.normalWS);Light l=GetMainLight(TransformWorldToShadowCoord(i.positionWS));half3 tex=SAMPLE_TEXTURE2D(_BaseMap,sampler_BaseMap,i.uv).rgb;half3 albedo=i.color.rgb*_BaseColor.rgb*tex;half3 col=albedo*(SampleSH(n)+l.color*saturate(dot(n,l.direction))*l.shadowAttenuation);return half4(MixFog(col,i.fog),1);}
ENDHLSL
}
UsePass "Universal Render Pipeline/Lit/ShadowCaster"
UsePass "Universal Render Pipeline/Lit/DepthOnly"
UsePass "Universal Render Pipeline/Lit/DepthNormals"
}
}
