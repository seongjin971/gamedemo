Shader "Vesper/WetStone"
{
    Properties
    {
        [MainTexture] _BaseMap("Stone grain (sRGB)", 2D) = "white" {}
        [Normal] _BumpMap("Stone normal", 2D) = "bump" {}
        [MainColor] _BaseColor("Stone tint", Color) = (0.60, 0.66, 0.71, 1)
        _Smoothness("Dry smoothness", Range(0,1)) = 0.28
        _Metallic("Metallic", Range(0,1)) = 0.03
        _BumpScale("Normal strength", Range(0,2)) = 0.65
        _Wetness("Wet pool amount", Range(0,1)) = 1
        _WorldScale("World texture scale", Float) = 0.18
        _PatinaStrength("Weathering strength", Range(0,1)) = 0.6
        _Distant("Distant ruin height haze", Range(0,1)) = 0
        _ReflectionStrength("Planar reflection strength", Range(0,2)) = 0.85
        _ReflectionDistortion("Planar reflection distortion", Range(0,0.03)) = 0.003
        _ReflectionHeightRange("Reflection plane height range", Float) = 0.12
        [Enum(UnityEngine.Rendering.CullMode)] _Cull("Cull", Float) = 2
    }
    SubShader
    {
        Tags { "RenderPipeline"="UniversalPipeline" "RenderType"="Opaque" "Queue"="Geometry" "UniversalMaterialType"="Lit" }
        LOD 300
        HLSLINCLUDE
        #define _CLEARCOAT 1
        #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"
        #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Lighting.hlsl"

        TEXTURE2D(_BaseMap); SAMPLER(sampler_BaseMap);
        TEXTURE2D(_BumpMap); SAMPLER(sampler_BumpMap);
        TEXTURE2D(_VesperPlanarReflection); SAMPLER(sampler_VesperPlanarReflection);
        float4x4 _VesperReflectionVP;
        float4 _VesperReflectionPlane; // xyz normal, w signed plane distance
        float4 _VesperReflectionTexelSize;
        float _VesperReflectionAvailable;
        CBUFFER_START(UnityPerMaterial)
            float4 _BaseMap_ST;
            half4 _BaseColor;
            half _Smoothness;
            half _Metallic;
            half _BumpScale;
            half _Wetness;
            float _WorldScale;
            half _PatinaStrength;
            half _Distant;
            half _ReflectionStrength;
            half _ReflectionDistortion;
            float _ReflectionHeightRange;
        CBUFFER_END

        struct Attributes
        {
            float4 positionOS : POSITION;
            float3 normalOS : NORMAL;
            half4 color : COLOR;
            UNITY_VERTEX_INPUT_INSTANCE_ID
        };
        struct Varyings
        {
            float4 positionCS : SV_POSITION;
            float3 positionWS : TEXCOORD0;
            half3 normalWS : TEXCOORD1;
            half4 fogAndVertexLight : TEXCOORD2;
            float4 shadowCoord : TEXCOORD3;
            half4 color : COLOR;
            UNITY_VERTEX_INPUT_INSTANCE_ID
            UNITY_VERTEX_OUTPUT_STEREO
        };

        float StoneHash(float2 p)
        {
            p = frac(p * float2(0.1031, 0.1030));
            p += dot(p, p.yx + 33.33);
            return frac((p.x + p.y) * p.x);
        }
        float StoneNoise(float2 p)
        {
            float2 i = floor(p), f = frac(p);
            f = f*f*(3-2*f);
            return lerp(lerp(StoneHash(i), StoneHash(i+float2(1,0)), f.x),
                        lerp(StoneHash(i+float2(0,1)), StoneHash(i+float2(1,1)), f.x), f.y);
        }
        float WetPool(float3 positionWS)
        {
            // Restore browser coordinates for the preserved five-pool placement.
            float2 p = float2(-positionWS.x, positionWS.z);
            float2 q = p + float2(sin(p.y*.77+p.x*.26), cos(p.x*.71-p.y*.37))*.8;
            float n = StoneNoise(q*.72)*.65 + StoneNoise(q*1.7)*.35;
            float2 a = (q-float2(-1.7,3))/float2(2.5,5.7);
            float2 b = (q-float2(6.5,3.7))/float2(2.7,5.5);
            float2 c = (q-float2(-2,11))/float2(5.5,6);
            float2 d = (q-float2(3,8.5))/float2(1.6,2.3);
            float2 e = (q-float2(-4,15))/float2(2,1.8);
            float field = max(max(exp(-dot(a,a)), exp(-dot(b,b))), exp(-dot(c,c))*.6);
            field = max(field, max(exp(-dot(d,d)), exp(-dot(e,e))));
            // Pool boundaries remain bounded even where the high-frequency noise is high.
            float wet = smoothstep(.34,.74,field*.66+n*.44) * smoothstep(.06,.23,field);
            wet *= lerp(1,.78,smoothstep(.12,.4,positionWS.y));
            float stair = smoothstep(.2,.5,positionWS.y)*smoothstep(3.8,5.4,p.x)*(1-smoothstep(-2,-.5,p.y));
            return saturate(lerp(wet,.90,stair*.70) * _Wetness);
        }
        float2 StoneUV(float3 p, half3 geometricNormal)
        {
            half3 axis = abs(geometricNormal);
            float2 uv = axis.y>axis.x && axis.y>axis.z ? p.xz : (axis.x>axis.z ? p.zy : p.xy);
            return uv * max(.001,_WorldScale) * _BaseMap_ST.xy + _BaseMap_ST.zw;
        }
        half3 PerturbedNormal(float3 p, half3 n, float2 uv, half3 normalTS)
        {
            // Cotangent frame derives the world-projected grain orientation without
            // requiring tangents on exported masonry or depending on mesh UV seams.
            float3 px=ddx(p), py=ddy(p);
            float2 ux=ddx(uv), uy=ddy(uv);
            float3 pyPerp=cross(py,n), pxPerp=cross(n,px);
            float3 tangent=pyPerp*ux.x+pxPerp*uy.x;
            float3 bitangent=pyPerp*ux.y+pxPerp*uy.y;
            float norm=rsqrt(max(1e-12,max(dot(tangent,tangent),dot(bitangent,bitangent))));
            return normalize(normalTS.x*tangent*norm+normalTS.y*bitangent*norm+normalTS.z*n);
        }
        Varyings StoneVertex(Attributes input)
        {
            Varyings output=(Varyings)0;
            UNITY_SETUP_INSTANCE_ID(input);
            UNITY_TRANSFER_INSTANCE_ID(input,output);
            UNITY_INITIALIZE_VERTEX_OUTPUT_STEREO(output);
            VertexPositionInputs p=GetVertexPositionInputs(input.positionOS.xyz);
            output.positionCS=p.positionCS;
            output.positionWS=p.positionWS;
            output.normalWS=TransformObjectToWorldNormal(input.normalOS);
            output.fogAndVertexLight=half4(ComputeFogFactor(p.positionCS.z),VertexLighting(p.positionWS,output.normalWS));
            output.shadowCoord=GetShadowCoord(p);
            output.color=input.color;
            return output;
        }
        ENDHLSL

        Pass
        {
            Name "ForwardLit"
            Tags { "LightMode"="UniversalForwardOnly" }
            Cull [_Cull] ZWrite On ZTest LEqual
            HLSLPROGRAM
            #pragma target 3.5
            #pragma vertex StoneVertex
            #pragma fragment StoneFragment
            #pragma multi_compile_instancing
            #pragma multi_compile_fog
            #pragma multi_compile _ _MAIN_LIGHT_SHADOWS _MAIN_LIGHT_SHADOWS_CASCADE _MAIN_LIGHT_SHADOWS_SCREEN
            #pragma multi_compile _ _ADDITIONAL_LIGHTS_VERTEX _ADDITIONAL_LIGHTS
            #pragma multi_compile_fragment _ _ADDITIONAL_LIGHT_SHADOWS
            #pragma multi_compile_fragment _ _SHADOWS_SOFT _SHADOWS_SOFT_LOW _SHADOWS_SOFT_MEDIUM _SHADOWS_SOFT_HIGH
            #pragma multi_compile_fragment _ _SCREEN_SPACE_OCCLUSION
            #pragma multi_compile_fragment _ _LIGHT_COOKIES
            #pragma multi_compile _ _FORWARD_PLUS
            #pragma multi_compile _ _CLUSTER_LIGHT_LOOP

            half4 StoneFragment(Varyings input) : SV_Target
            {
                UNITY_SETUP_INSTANCE_ID(input);
                UNITY_SETUP_STEREO_EYE_INDEX_POST_VERTEX(input);
                half3 geometricNormal=normalize(input.normalWS);
                float2 uv=StoneUV(input.positionWS,geometricNormal);
                half4 grain=SAMPLE_TEXTURE2D(_BaseMap,sampler_BaseMap,uv);
                half wet=WetPool(input.positionWS)*smoothstep(.80,.97,geometricNormal.y);
                half3 normalTS=UnpackNormalScale(SAMPLE_TEXTURE2D(_BumpMap,sampler_BumpMap,uv),_BumpScale*.75*lerp(1,.60,wet));
                half3 surfaceNormal=PerturbedNormal(input.positionWS,geometricNormal,uv,normalTS);
                float2 weatherUV=input.positionWS.xz+input.positionWS.y*float2(.51,.77);
                half patina=StoneNoise(weatherUV*1.7)*.50+StoneNoise(weatherUV*7.3)*.30+StoneNoise(weatherUV*28)*.20;

                SurfaceData surface=(SurfaceData)0;
                surface.albedo=grain.rgb*_BaseColor.rgb*input.color.rgb;
                surface.albedo*=lerp(1,lerp(.66,1.18,patina),_PatinaStrength)*lerp(1,.92,wet);
                surface.metallic=_Metallic;
                surface.specular=half3(.04,.04,.04);
                // Three's wet slab has roughness .43; the first native pass used
                // .24 and exaggerated the broad moon/point-light specular sheen.
                surface.smoothness=saturate(lerp(_Smoothness,.57,wet)-(1-grain.g)*.045);
                surface.normalTS=normalTS;
                surface.occlusion=lerp(.94,1,patina);
                surface.alpha=1;
                // Source coat energy was explicitly reduced to 14% direct / 24%
                // indirect. Match that effective energy rather than its raw .75
                // coat parameter. Real planar imagery remains independent below.
                surface.clearCoatMask=wet*.12;
                surface.clearCoatSmoothness=.58;

                InputData lighting=(InputData)0;
                lighting.positionWS=input.positionWS;
                lighting.positionCS=input.positionCS;
                lighting.normalWS=surfaceNormal;
                lighting.viewDirectionWS=GetWorldSpaceNormalizeViewDir(input.positionWS);
                #if defined(_MAIN_LIGHT_SHADOWS_SCREEN)
                    lighting.shadowCoord=input.shadowCoord;
                #else
                    lighting.shadowCoord=TransformWorldToShadowCoord(input.positionWS);
                #endif
                lighting.fogCoord=InitializeInputDataFog(float4(input.positionWS,1),input.fogAndVertexLight.x);
                lighting.vertexLighting=input.fogAndVertexLight.yzw;
                lighting.bakedGI=SampleSH(surfaceNormal);
                lighting.normalizedScreenSpaceUV=GetNormalizedScreenSpaceUV(input.positionCS);
                lighting.shadowMask=half4(1,1,1,1);
                half4 color=UniversalFragmentPBR(lighting,surface);

                float planeDistance=abs(dot(float4(input.positionWS,1),_VesperReflectionPlane));
                half planeWeight=1-smoothstep(_ReflectionHeightRange*.5,max(.001,_ReflectionHeightRange),planeDistance);
                float4 reflectionPosition=mul(_VesperReflectionVP,float4(input.positionWS,1));
                float2 reflectionUV=reflectionPosition.xy/max(.0001,reflectionPosition.w)*.5+.5;
                reflectionUV+=normalTS.xy*_ReflectionDistortion;
                half edge=smoothstep(0,.035,min(min(reflectionUV.x,1-reflectionUV.x),min(reflectionUV.y,1-reflectionUV.y)));
                half inFront=step(.0001,reflectionPosition.w);
                half reflectWeight=wet*planeWeight*edge*inFront*_VesperReflectionAvailable;
                if(reflectWeight>.001)
                {
                    float2 blur=float2(0,_VesperReflectionTexelSize.y*1.4);
                    half3 reflection=SAMPLE_TEXTURE2D(_VesperPlanarReflection,sampler_VesperPlanarReflection,reflectionUV).rgb*.60;
                    reflection+=SAMPLE_TEXTURE2D(_VesperPlanarReflection,sampler_VesperPlanarReflection,reflectionUV+blur).rgb*.20;
                    reflection+=SAMPLE_TEXTURE2D(_VesperPlanarReflection,sampler_VesperPlanarReflection,reflectionUV-blur).rgb*.20;
                    half grazing=1-saturate(dot(geometricNormal,lighting.viewDirectionWS));
                    half fresnel=.075+.60*grazing*grazing*grazing;
                    half waterBlend=saturate(reflectWeight*fresnel*_ReflectionStrength);
                    color.rgb=lerp(color.rgb,reflection,waterBlend);
                }
                color.rgb=MixFog(color.rgb,lighting.fogCoord);
                // The browser's distant architecture merges into blue valley
                // haze with depth below the courtyard. Near stone is unchanged.
                half distantHaze=(1-smoothstep(-21,1,input.positionWS.y))*.83*saturate(_Distant);
                color.rgb=lerp(color.rgb,half3(.035,.067,.092),distantHaze);
                return half4(color.rgb,1);
            }
            ENDHLSL
        }

        Pass
        {
            Name "ShadowCaster"
            Tags { "LightMode"="ShadowCaster" }
            Cull Back ZWrite On ZTest LEqual ColorMask 0
            HLSLPROGRAM
            #pragma target 3.5
            #pragma vertex StoneShadowVertex
            #pragma fragment StoneShadowFragment
            #pragma multi_compile_instancing
            #pragma multi_compile_vertex _ _CASTING_PUNCTUAL_LIGHT_SHADOW
            float3 _LightDirection;
            float3 _LightPosition;
            float4 StoneShadowVertex(Attributes input) : SV_POSITION
            {
                UNITY_SETUP_INSTANCE_ID(input);
                float3 p=TransformObjectToWorld(input.positionOS.xyz);
                float3 n=TransformObjectToWorldNormal(input.normalOS);
                #if defined(_CASTING_PUNCTUAL_LIGHT_SHADOW)
                    float3 lightDirection=normalize(_LightPosition-p);
                #else
                    float3 lightDirection=_LightDirection;
                #endif
                float4 positionCS=TransformWorldToHClip(ApplyShadowBias(p,n,lightDirection));
                #if UNITY_REVERSED_Z
                    positionCS.z=min(positionCS.z,UNITY_NEAR_CLIP_VALUE*positionCS.w);
                #else
                    positionCS.z=max(positionCS.z,UNITY_NEAR_CLIP_VALUE*positionCS.w);
                #endif
                return positionCS;
            }
            half4 StoneShadowFragment() : SV_Target { return 0; }
            ENDHLSL
        }
        Pass
        {
            Name "DepthOnly"
            Tags { "LightMode"="DepthOnly" }
            Cull Back ZWrite On ColorMask R
            HLSLPROGRAM
            #pragma target 3.5
            #pragma vertex StoneVertex
            #pragma fragment StoneDepthFragment
            #pragma multi_compile_instancing
            half StoneDepthFragment(Varyings input) : SV_Target { return input.positionCS.z; }
            ENDHLSL
        }
        Pass
        {
            Name "DepthNormals"
            Tags { "LightMode"="DepthNormalsOnly" }
            Cull Back ZWrite On
            HLSLPROGRAM
            #pragma target 3.5
            #pragma vertex StoneVertex
            #pragma fragment StoneNormalsFragment
            #pragma multi_compile_instancing
            #pragma multi_compile_fragment _ _GBUFFER_NORMALS_OCT
            half4 StoneNormalsFragment(Varyings input) : SV_Target
            {
                UNITY_SETUP_INSTANCE_ID(input);
                half3 n=normalize(input.normalWS);
                float2 uv=StoneUV(input.positionWS,n);
                half wet=WetPool(input.positionWS)*smoothstep(.80,.97,n.y);
                half3 normalTS=UnpackNormalScale(SAMPLE_TEXTURE2D(_BumpMap,sampler_BumpMap,uv),_BumpScale*.75*lerp(1,.60,wet));
                n=PerturbedNormal(input.positionWS,n,uv,normalTS);
                #if defined(_GBUFFER_NORMALS_OCT)
                    float2 oct=PackNormalOctQuadEncode(n)*.5+.5;
                    return half4(PackFloat2To888(saturate(oct)),0);
                #else
                    return half4(n,0);
                #endif
            }
            ENDHLSL
        }
    }
    FallBack "Hidden/Universal Render Pipeline/FallbackError"
}
