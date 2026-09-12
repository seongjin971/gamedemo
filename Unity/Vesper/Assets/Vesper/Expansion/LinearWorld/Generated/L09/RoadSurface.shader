Shader "Vesper/Linear/Road/L09" {
Properties {
 _DirtMap("Higgsfield dry earth",2D)="gray"{} _MudMap("Higgsfield rain mud",2D)="gray"{}
 _TrailStoneMap("Higgsfield buried stones",2D)="gray"{} _SlushMap("Higgsfield slush",2D)="gray"{}
 _SnowMap("Existing powder",2D)="white"{} _PackedMap("Existing packed snow",2D)="white"{}
 _TextureScale("Meters to texture",Float)=.25 _NormalStrength("Surface relief",Float)=10
}
SubShader { Tags {"RenderPipeline"="UniversalPipeline" "RenderType"="Transparent" "Queue"="Geometry+10"}
Pass {Name "RoadSurface" Tags {"LightMode"="UniversalForward"}
Blend SrcAlpha OneMinusSrcAlpha
ZWrite Off
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
TEXTURE2D(_DirtMap);SAMPLER(sampler_DirtMap);TEXTURE2D(_MudMap);SAMPLER(sampler_MudMap);
TEXTURE2D(_TrailStoneMap);SAMPLER(sampler_TrailStoneMap);TEXTURE2D(_SlushMap);SAMPLER(sampler_SlushMap);
TEXTURE2D(_SnowMap);SAMPLER(sampler_SnowMap);TEXTURE2D(_PackedMap);SAMPLER(sampler_PackedMap);
TEXTURE2D(_VesperPlanarReflection);SAMPLER(sampler_VesperPlanarReflection);
float4x4 _VesperReflectionVP;float _VesperReflectionAvailable;
CBUFFER_START(UnityPerMaterial)
float _TextureScale,_NormalStrength;
CBUFFER_END
struct A{float4 p:POSITION;float3 n:NORMAL;half4 c:COLOR;};
struct V{float4 p:SV_POSITION;float3 w:TEXCOORD0;half3 n:TEXCOORD1;half4 c:COLOR;half fog:TEXCOORD2;};
V vert(A i){V o;o.w=TransformObjectToWorld(i.p.xyz);o.p=TransformWorldToHClip(o.w);o.n=TransformObjectToWorldNormal(i.n);o.c=i.c;o.fog=ComputeFogFactor(o.p.z);return o;}
float hash21(float2 p){p=frac(p*float2(123.34,345.45));p+=dot(p,p+34.345);return frac(p.x*p.y);}
float patches(float2 p){float2 id=floor(p),f=frac(p);f=f*f*(3-2*f);return lerp(lerp(hash21(id),hash21(id+float2(1,0)),f.x),lerp(hash21(id+float2(0,1)),hash21(id+1),f.x),f.y);}
half luminance3(half3 c){return dot(c,half3(.3,.5,.2));}
half3 stoneAt(float2 uv){return SAMPLE_TEXTURE2D(_TrailStoneMap,sampler_TrailStoneMap,uv).rgb;}
half4 frag(V i):SV_Target{
 float d=-i.w.z;float2 ground=i.w.xz,uv=ground*_TextureScale;
 float variation=patches(ground*.53)*.7+patches(ground*1.37)*.3;
 float edgeNoise=(patches(ground*.71)-.5)*.62+(patches(ground*3.8)-.5)*.14;
 float across=abs(i.w.x)+edgeNoise;
 half alpha=1-smoothstep(1.58,2.65,across);clip(alpha-.002);
 // The architectural stone bridge remains intact; earth shoulders meet its abutments.
 alpha*=1-smoothstep(16.0,17.95,d)*(1-smoothstep(32.05,33.8,d));
 // Feather into the already accepted far-pass snow treatment without a geometric endpoint.
 alpha*=1-smoothstep(268,298,d);
 half wet=smoothstep(48,108,d)*(1-smoothstep(224,264,d));
 half abbey=smoothstep(108,145,d)*(1-smoothstep(162,198,d));
 half stoneAmount=lerp(.36,.65,smoothstep(34,94,d))+abbey*.10;
 stoneAmount*=1-smoothstep(1.18,2.28,across)*.68;
 half stoneMix=smoothstep(.31,.61,stoneAmount+(variation-.5)*.85);
 half3 dirt=SAMPLE_TEXTURE2D(_DirtMap,sampler_DirtMap,uv*.94).rgb;
 half3 mud=SAMPLE_TEXTURE2D(_MudMap,sampler_MudMap,uv*.88+float2(.37,.61)).rgb;
 half3 rock=stoneAt(uv);
 // Soil fills actual dark joints, leaving crisp exposed stone faces instead of translucent cobbles.
 half stoneFace=smoothstep(.10,.20,luminance3(rock));
 stoneMix*=lerp(.20,1,stoneFace);
 half3 dry=lerp(dirt,rock,stoneMix);
 half3 rainy=lerp(mud*.86,rock*half3(.69,.73,.76),stoneMix);
 half3 albedo=lerp(dry,rainy,wet);
 half iceProgress=smoothstep(198,272,d);
 half snowPatch=iceProgress+(patches(ground*.82)-.5)*.64+(patches(ground*4.7)-.5)*.12+(1-stoneFace)*.09;
 half roadSnow=smoothstep(.44,.58,snowPatch+smoothstep(.85,2.3,across)*.23);
 roadSnow=max(roadSnow,i.c.g*smoothstep(1.0,2.45,across));
 half slush=smoothstep(199,229,d)*(1-smoothstep(254,280,d));
 half3 thaw=SAMPLE_TEXTURE2D(_SlushMap,sampler_SlushMap,uv*.90).rgb;
 // Wet grit remains legible between snow islands throughout the ascent.
 albedo=lerp(albedo,lerp(mud,thaw,.36),slush*.37);
 half3 powder=SAMPLE_TEXTURE2D(_SnowMap,sampler_SnowMap,ground*.184).rgb;
 half3 packed=SAMPLE_TEXTURE2D(_PackedMap,sampler_PackedMap,ground*.23).rgb;
 half3 snow=lerp(powder,packed,.78)*half3(.79,.84,.89);
 albedo=lerp(albedo,snow,roadSnow);
 half puddle=smoothstep(.69,.735,patches(ground*.66)+(patches(ground*3.8)-.5)*.12)*wet*(1-stoneFace*.65)*(1-roadSnow);
 albedo*=lerp(1,.49,puddle);
 half height=luminance3(rock),dx=luminance3(stoneAt(uv+float2(.003,0)))-height,dz=luminance3(stoneAt(uv+float2(0,.003)))-height;
 half3 n=normalize(i.n+half3(-dx,0,-dz)*_NormalStrength*lerp(.3,1,stoneMix)*(1-roadSnow*.9)*(1-puddle*.95));
 Light sun=GetMainLight(TransformWorldToShadowCoord(i.w));AmbientOcclusionFactor ao=GetScreenSpaceAmbientOcclusion(GetNormalizedScreenSpaceUV(i.p));
 half3 color=albedo*(SampleSH(n)*ao.indirectAmbientOcclusion+sun.color*saturate(dot(n,sun.direction))*sun.shadowAttenuation*ao.directAmbientOcclusion);
 half3 view=GetWorldSpaceNormalizeViewDir(i.w),halfway=normalize(view+sun.direction);
 half gloss=pow(saturate(dot(n,halfway)),lerp(55,380,puddle))*(.025*wet+.14*puddle);
 color+=sun.color*gloss*sun.shadowAttenuation;
 half3 reflected=SampleSH(half3(0,1,0))*half3(.14,.17,.20);
 float4 q=mul(_VesperReflectionVP,float4(i.w,1));float2 ruv=q.xy/max(.001,q.w)*.5+.5;
 #if UNITY_UV_STARTS_AT_TOP
 ruv.y=1-ruv.y;
 #endif
 half3 planar=SAMPLE_TEXTURE2D(_VesperPlanarReflection,sampler_VesperPlanarReflection,ruv).rgb;planar=planar/(1+planar);
 half availability=_VesperReflectionAvailable*smoothstep(117,135,d)*(1-smoothstep(169,182,d));
 reflected=lerp(reflected,planar*.26,availability*.65);
 color=lerp(color,reflected,puddle*(.34+.30*pow(1-saturate(dot(n,view)),3)));
 return half4(MixFog(color,i.fog),alpha);
}
ENDHLSL
}
}
}
