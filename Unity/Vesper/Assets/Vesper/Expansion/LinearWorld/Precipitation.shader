Shader "Vesper/Linear/Precipitation" {
Properties { _BaseColor("Weather tint",Color)=(.72,.81,.88,.22) _Kind("Rain 0 / snow 1 / splash 2",Float)=0 }
SubShader { Tags {"RenderPipeline"="UniversalPipeline" "Queue"="Transparent" "RenderType"="Transparent"} ZWrite Off Cull Off Blend SrcAlpha OneMinusSrcAlpha
Pass {Name "Weather" Tags {"LightMode"="UniversalForward"}
HLSLPROGRAM
#pragma vertex vert
#pragma fragment frag
#pragma multi_compile_fog
#include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"
#include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/DeclareDepthTexture.hlsl"
CBUFFER_START(UnityPerMaterial)
half4 _BaseColor;float _Kind;
CBUFFER_END
float4 _WorldShelterMin,_WorldShelterMax;
struct A{float4 p:POSITION;float2 uv:TEXCOORD0;half4 c:COLOR;};struct V{float4 p:SV_POSITION;float3 w:TEXCOORD0;float2 uv:TEXCOORD1;half4 c:COLOR;half fog:TEXCOORD2;};
V vert(A i){V o;o.w=TransformObjectToWorld(i.p.xyz);o.p=TransformWorldToHClip(o.w);o.uv=i.uv;o.c=i.c;o.fog=ComputeFogFactor(o.p.z);return o;}
half4 frag(V i):SV_Target{
 float d=-i.w.z;half rain=smoothstep(55,120,d),snow=smoothstep(190,255,d);half weight=_Kind==1?snow:rain*(1-snow);
 bool sheltered=all(i.w>_WorldShelterMin.xyz)&&all(i.w<_WorldShelterMax.xyz);if(sheltered)weight=0;
 half2 q=i.uv*2-1;half radius=length(q);half alpha;
 if(_Kind==0)alpha=(1-smoothstep(.15,1,abs(q.x)))*(1-smoothstep(.45,1,abs(q.y)));
 else if(_Kind==1)alpha=1-smoothstep(.1,1,radius);
 else alpha=(1-smoothstep(.65,.96,radius))*smoothstep(.43,.66,radius);
 float depth=SampleSceneDepth(GetNormalizedScreenSpaceUV(i.p));
 #if !UNITY_REVERSED_Z
 depth=lerp(UNITY_NEAR_CLIP_VALUE,1,depth);
 #endif
 float3 behind=ComputeWorldSpacePosition(GetNormalizedScreenSpaceUV(i.p),depth,UNITY_MATRIX_I_VP);
 half soft=_Kind==2?1:saturate(distance(behind,i.w)*2);
 return half4(MixFog(_BaseColor.rgb*i.c.rgb,i.fog),alpha*_BaseColor.a*i.c.a*weight*soft);
}
ENDHLSL
}
}
}
