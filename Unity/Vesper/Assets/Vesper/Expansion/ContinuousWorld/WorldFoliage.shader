Shader "Vesper/WorldFoliage" {
Properties { _BaseMap("Branch atlas",2D)="white"{} _BaseColor("Leaf tint",Color)=(.8,.87,.71,1) _Cutoff("Leaf edge",Range(0,1))=.42 _Cull("Culling",Float)=0 _Wind("Breeze",Float)=.025 }
SubShader { Tags {"RenderType"="TransparentCutout" "Queue"="AlphaTest" "RenderPipeline"="UniversalPipeline"} Cull Off
Pass {Name "ForwardLit" Tags {"LightMode"="UniversalForward"}
HLSLPROGRAM
#pragma target 3.5
#pragma vertex vert
#pragma fragment frag
#pragma multi_compile_instancing
#pragma multi_compile _ _MAIN_LIGHT_SHADOWS _MAIN_LIGHT_SHADOWS_CASCADE _MAIN_LIGHT_SHADOWS_SCREEN
#pragma multi_compile_fragment _ _SHADOWS_SOFT _SHADOWS_SOFT_LOW _SHADOWS_SOFT_MEDIUM _SHADOWS_SOFT_HIGH
#pragma multi_compile_fog
#include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"
#include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Lighting.hlsl"
TEXTURE2D(_BaseMap);SAMPLER(sampler_BaseMap);
CBUFFER_START(UnityPerMaterial)
float4 _BaseMap_ST;half4 _BaseColor;float _Cutoff,_Cull,_Wind;
CBUFFER_END
struct A{float4 p:POSITION;float3 n:NORMAL;float2 uv:TEXCOORD0;UNITY_VERTEX_INPUT_INSTANCE_ID};
struct V{float4 p:SV_POSITION;float3 w:TEXCOORD0;half3 n:TEXCOORD1;float2 uv:TEXCOORD2;half fog:TEXCOORD3;UNITY_VERTEX_INPUT_INSTANCE_ID};
V vert(A i){V o;UNITY_SETUP_INSTANCE_ID(i);UNITY_TRANSFER_INSTANCE_ID(i,o);o.w=TransformObjectToWorld(i.p.xyz);float sway=sin(o.w.x*.75+o.w.z*.49+_Time.y*.9)*sin(o.w.y*1.2+_Time.y*.47);o.w.xz+=float2(sway,sway*.35)*_Wind;o.p=TransformWorldToHClip(o.w);o.n=TransformObjectToWorldNormal(i.n);o.uv=TRANSFORM_TEX(i.uv,_BaseMap);o.fog=ComputeFogFactor(o.p.z);return o;}
half4 frag(V i):SV_Target{UNITY_SETUP_INSTANCE_ID(i);half4 leaf=SAMPLE_TEXTURE2D(_BaseMap,sampler_BaseMap,i.uv)*_BaseColor;clip(leaf.a-_Cutoff);half3 n=normalize(i.n);Light light=GetMainLight(TransformWorldToShadowCoord(i.w));half diffuse=abs(dot(n,light.direction))*.65+.25;half3 ambient=SampleSH(half3(0,1,0))*.8;half3 view=GetWorldSpaceNormalizeViewDir(i.w);half transmission=pow(saturate(dot(-view,light.direction)),4)*.14;half3 color=leaf.rgb*(ambient+light.color*(diffuse*light.shadowAttenuation+transmission));return half4(MixFog(color,i.fog),1);}
ENDHLSL
}
UsePass "Universal Render Pipeline/Lit/ShadowCaster"
UsePass "Universal Render Pipeline/Lit/DepthOnly"
UsePass "Universal Render Pipeline/Lit/DepthNormals"
}
}
