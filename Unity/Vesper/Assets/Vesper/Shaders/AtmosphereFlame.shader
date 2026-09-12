Shader "Vesper/AtmosphereFlame"
{
    Properties
    {
        [MainTexture] _BaseMap("Flame on black (sRGB)", 2D) = "black" {}
        [HDR] [MainColor] _BaseColor("Flame radiance / opacity", Color) = (1.8,1.25,0.9,0.9)
        _RadianceScale("Source energy normalization",Float)=1
        _Upright("Physical upright plume",Range(0,1))=0
        _SourceRadiance("Preserve source flame radiance",Range(0,1))=0
    }
    SubShader
    {
        Tags { "RenderPipeline"="UniversalPipeline" "RenderType"="Transparent" "Queue"="Transparent" "IgnoreProjector"="True" }
        Pass
        {
            Name "FlameAdditive"
            Tags { "LightMode"="UniversalForward" }
            Cull Off
            ZWrite Off
            ZTest LEqual
            Blend One One
            ColorMask RGB
            HLSLPROGRAM
            #pragma target 3.0
            #pragma vertex FlameVertex
            #pragma fragment FlameFragment
            #pragma multi_compile_fog
            #pragma multi_compile_instancing
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"

            TEXTURE2D(_BaseMap); SAMPLER(sampler_BaseMap);
            CBUFFER_START(UnityPerMaterial)
                float4 _BaseMap_ST;
                half4 _BaseColor;
                half _RadianceScale;
                half _Upright;
                half _SourceRadiance;
            CBUFFER_END
            struct Attributes
            {
                float4 positionOS : POSITION;
                float2 uv : TEXCOORD0;
                UNITY_VERTEX_INPUT_INSTANCE_ID
            };
            struct Varyings
            {
                float4 positionCS : SV_POSITION;
                float2 uv : TEXCOORD0;
                half fog : TEXCOORD1;
                UNITY_VERTEX_OUTPUT_STEREO
            };
            Varyings FlameVertex(Attributes input)
            {
                Varyings output=(Varyings)0;
                UNITY_SETUP_INSTANCE_ID(input);
                UNITY_INITIALIZE_VERTEX_OUTPUT_STEREO(output);
                // VesperBillboard faces the source camera before either render.
                // Keep that same physical quad in the reflected view. Building
                // a second quad from the reflected inverse-view axes reverses
                // its world-space up direction and moves the bright core to a
                // different physical location, defeating a planar reflection.
                float3 positionWS=TransformObjectToWorld(input.positionOS.xyz);
                float3 center=TransformObjectToWorld(float3(0,0,0));
                float3 axisX=unity_ObjectToWorld._m00_m10_m20;
                float scaleY=length(unity_ObjectToWorld._m01_m11_m21);
                float3 upright=center+axisX*input.positionOS.x+float3(0,input.positionOS.y*scaleY,0);
                output.positionCS=TransformWorldToHClip(lerp(positionWS,upright,_Upright));
                output.uv=TRANSFORM_TEX(input.uv,_BaseMap);
                output.fog=ComputeFogFactor(output.positionCS.z);
                return output;
            }
            half4 FlameFragment(Varyings input) : SV_Target
            {
                UNITY_SETUP_STEREO_EYE_INDEX_POST_VERTEX(input);
                float2 uv=input.uv;
                // Preserve the source Three.js plume's two-axis travelling warp.
                uv.x+=sin(uv.y*11-_Time.y*4)*.012*uv.y;
                uv.y+=sin(_Time.y*3+uv.x*9)*.012*uv.y;
                half4 flame=SAMPLE_TEXTURE2D(_BaseMap,sampler_BaseMap,saturate(uv));
                // The importer marks the generated PNG sRGB; Unity decodes it to
                // linear before sampling. HDR multiplication stays linear, and
                // the source camera performs tone mapping once after blending.
                half density=max(0,max(flame.r,max(flame.g,flame.b)));
                // The sRGB orange source has very little blue after linear decoding.
                // Requiring high blue suppressed the white-hot core everywhere.
                half core=smoothstep(.18,.65,flame.g)*smoothstep(.5,.95,flame.r);
                half3 fireColor=lerp(half3(1,.32,.075),half3(1,.82,.52),core);
                // Preserve the weaker orange tongues while increasing the small
                // source core's HDR energy. Its physical water reflection loses
                // about 97% at this camera angle; do not paint opacity into water.
                half3 radiance=fireColor*pow(density,1.6)*_BaseColor.rgb*(flame.a*_BaseColor.a)*(.25+core*.75)*(1+core*4);
                // The generated turbulent source already carries its gradients.
                // A second density power/core mask erased its orange side licks.
                half3 sourceRadiance=flame.rgb*_BaseColor.rgb*(flame.a*_BaseColor.a);
                radiance=lerp(radiance,sourceRadiance,_SourceRadiance);
                // Additive emitters fade toward black instead of adding fog color.
                radiance=MixFogColor(radiance*_RadianceScale,half3(0,0,0),input.fog);
                return half4(radiance,0);
            }
            ENDHLSL
        }
    }
    FallBack "Hidden/Universal Render Pipeline/FallbackError"
}
