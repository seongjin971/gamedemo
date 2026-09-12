Shader "Vesper/StandingWater"
{
 Properties { _WetMask("Authored drainage mask",2D)="black"{} }
 SubShader {
  Tags {"RenderPipeline"="UniversalPipeline" "Queue"="Transparent-20" "RenderType"="Transparent"}
  Pass {
   Name "Continuous shallow water"
   Cull Off ZWrite Off ZTest LEqual Blend SrcAlpha OneMinusSrcAlpha
   HLSLPROGRAM
   #pragma target 3.5
   #pragma vertex vert
   #pragma fragment frag
   #pragma multi_compile _ _ADDITIONAL_LIGHTS_VERTEX _ADDITIONAL_LIGHTS
   #pragma multi_compile _ _CLUSTER_LIGHT_LOOP
   #pragma multi_compile_fragment _ _ADDITIONAL_LIGHT_SHADOWS
   #pragma multi_compile_fragment _ _SHADOWS_SOFT _SHADOWS_SOFT_LOW _SHADOWS_SOFT_MEDIUM _SHADOWS_SOFT_HIGH
   #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"
   #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Lighting.hlsl"
   TEXTURE2D(_WetMask);SAMPLER(sampler_WetMask);
   TEXTURE2D(_VesperPlanarReflection);SAMPLER(sampler_VesperPlanarReflection);
   float4x4 _VesperReflectionVP;
   float _VesperReflectionAvailable;
   float _VesperWaterDiagnostic;
   struct A {float4 p:POSITION;};
   struct V {float4 p:SV_POSITION;float3 world:TEXCOORD0;};
   V vert(A i){V o;o.world=TransformObjectToWorld(i.p.xyz);o.p=TransformWorldToHClip(o.world);return o;}
   half4 frag(V i):SV_Target {
    float2 uv=float2((-i.world.x+7.8)/18,1-(i.world.z+8)/26);
    half mask=max(SAMPLE_TEXTURE2D(_WetMask,sampler_WetMask,uv).r,max(SAMPLE_TEXTURE2D(_WetMask,sampler_WetMask,uv+float2(.018,0)).r,SAMPLE_TEXTURE2D(_WetMask,sampler_WetMask,uv-float2(.018,0)).r));
    half coverage=smoothstep(.36,.63,mask);clip(coverage-.015);
    if(_VesperWaterDiagnostic>.5&&_VesperWaterDiagnostic<1.5)return half4(coverage,0,0,1);
    float4 q=mul(_VesperReflectionVP,float4(i.world,1));float2 ruv=q.xy/max(.0001,q.w)*.5+.5;
    #if UNITY_UV_STARTS_AT_TOP
    ruv.y=1-ruv.y;
    #endif
    // Low-amplitude broad ripples belong to the water plane, independent of
    // stone normals, seams and per-instance mineral orientation below it.
    float rippleA=sin(i.world.z*24.1+i.world.x*2.8-_Time.y*.75);
    float rippleB=sin(i.world.z*39.7-i.world.x*13.1+_Time.y*.41);
    ruv+=float2((rippleA*.65+rippleB*.35)*.00052,rippleB*.00018);
    // Preserve recognizable reflected shapes. The former 15-pixel vertical
    // blur turned moonlit pools and braziers into opaque cloud-like smears.
    half3 reflection=SAMPLE_TEXTURE2D(_VesperPlanarReflection,sampler_VesperPlanarReflection,ruv).rgb;
    half grazing=1-saturate(GetWorldSpaceNormalizeViewDir(i.world).y);
    // Dielectric reflectance controls both reflected objects and sky equally.
    // Opaque-looking, hue-selected 50-80% blends hid the stone bed and made
    // cold pools resemble blue paint. The authored mask only marks coverage.
    half fresnel=.025+.975*pow(grazing,5);
    half alpha=coverage*fresnel*_VesperReflectionAvailable;
    // Fire highlights belong to this water surface, not a second clear coat
    // over every stone. A small anisotropic lobe follows the shallow ripples.
    half3 direct=0;
    #if defined(_ADDITIONAL_LIGHTS)
    InputData inputData=(InputData)0;inputData.positionWS=i.world;
    inputData.normalizedScreenSpaceUV=GetNormalizedScreenSpaceUV(i.p);
    half3 v=GetWorldSpaceNormalizeViewDir(i.world);
    half3 n=normalize(half3(.006*cos(i.world.z*39.7-i.world.x*13.1+_Time.y*.41),1,.014*cos(i.world.z*24.1+i.world.x*2.8-_Time.y*.75)));
    half3 tangent=normalize(cross(half3(0,0,1),n)),bitangent=cross(n,tangent);
    uint pixelLightCount=GetAdditionalLightsCount();
    LIGHT_LOOP_BEGIN(pixelLightCount)
     Light light=GetAdditionalLight(lightIndex,i.world,half4(1,1,1,1));
     half3 h=SafeNormalize(v+light.direction);
     float ax=.035,az=.10;
     float hx=dot(h,tangent),hz=dot(h,bitangent),hy=saturate(dot(h,n));
     float denom=hx*hx/(ax*ax)+hz*hz/(az*az)+hy*hy;
     float distribution=rcp(PI*ax*az*denom*denom+.00001);
     float nl=saturate(dot(light.direction,n)),nv=saturate(dot(v,n)),k=.035;
     float visibility=nl/(nl*(1-k)+k)*nv/(nv*(1-k)+k);
     float f=.025+.975*pow(1-saturate(dot(v,h)),5);
     float spec=min(16,distribution*visibility*f/max(.001,4*nv));
     direct+=light.color*(light.distanceAttenuation*light.shadowAttenuation)*spec;
    LIGHT_LOOP_END
    #endif
    if(_VesperWaterDiagnostic>1.5&&_VesperWaterDiagnostic<2.5)return half4(reflection,1);
    if(_VesperWaterDiagnostic>2.5)return half4(direct,1);
    return half4(reflection+direct/max(.001,fresnel),alpha);
   }
   ENDHLSL
  }
 }
}
