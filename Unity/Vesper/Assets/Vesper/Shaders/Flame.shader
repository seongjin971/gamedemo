Shader "Vesper/Flame"
{
    Properties
    {
        [MainTexture] _BaseMap("Flame on black (sRGB)", 2D) = "black" {}
        [HDR] [MainColor] _BaseColor("Flame radiance / opacity", Color) = (1.8,1.25,0.9,0.9)
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
                output.positionCS=TransformObjectToHClip(input.positionOS.xyz);
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
                half3 radiance=flame.rgb*_BaseColor.rgb*(flame.a*_BaseColor.a);
                // Additive emitters fade toward black instead of adding fog color.
                radiance=MixFogColor(radiance,half3(0,0,0),input.fog);
                return half4(radiance,0);
            }
            ENDHLSL
        }
    }
    FallBack "Hidden/Universal Render Pipeline/FallbackError"
}
