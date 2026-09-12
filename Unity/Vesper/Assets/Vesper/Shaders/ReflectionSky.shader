Shader "Vesper/ReflectionSky" {
 Properties { _Tex("Moon cloud environment",Cube)=""{} _DirectEnvironment("Use shared stone environment radiance",Float)=0 }
 SubShader { Tags {"Queue"="Background" "RenderType"="Background" "PreviewType"="Skybox"} Cull Off ZWrite Off
  Pass { HLSLPROGRAM
   #pragma vertex vert
   #pragma fragment frag
   #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"
   TEXTURECUBE(_Tex);SAMPLER(sampler_Tex);
   CBUFFER_START(UnityPerMaterial)
   half _DirectEnvironment;
   CBUFFER_END
   struct A {float4 p:POSITION;};struct V {float4 p:SV_POSITION;float3 direction:TEXCOORD0;};
   V vert(A i){V o;o.p=TransformObjectToHClip(i.p.xyz);o.direction=i.p.xyz;return o;}
   half4 frag(V i):SV_Target {
    float3 direction=normalize(i.direction);
    half3 cloud=SAMPLE_TEXTURECUBE_LOD(_Tex,sampler_Tex,direction,2).rgb;
    if(_DirectEnvironment>.5)return half4(cloud,0);
    // An overcast night environment has broad radiance, without projected
    // high-contrast cloud silhouettes masquerading as water surface relief.
    half horizon=pow(1-abs(direction.y),2);
    half3 sky=lerp(half3(.34,.49,.67),half3(.12,.22,.33),horizon);
    sky+=min(cloud,half3(.4,.4,.4))*.045;
    return half4(sky,0);
   }
  ENDHLSL }
 }
}
