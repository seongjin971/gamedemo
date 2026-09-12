Shader "Vesper/AtmosphereStone"
{
    Properties
    {
        [MainTexture] _BaseMap("Stone grain (sRGB)", 2D) = "white" {}
        _DetailMap("Stratified mineral surface", 2D) = "gray" {}
        [Normal] _DetailNormal("Measured stone normal",2D)="bump"{}
        [Normal] _MicroNormal("Measured fine mineral normal",2D)="bump"{}
        _MicroRoughness("Measured fine mineral roughness",2D)="gray"{}
        _MineralColor("Coherent mineral albedo",2D)="gray"{}
        _MineralScale("Mineral repeats per world metre",Float)=3
        _MineralColorStrength("Mineral color modulation",Range(0,1))=0
        _MineralNormalCenter("Layer normal tangent mean",Vector)=(0,0,0,0)
        _RoughnessMap("Measured stone roughness",2D)="white"{}
        _StoneAO("Measured stone cavity occlusion",2D)="white"{}
        _Photographic("Photographic PBR stone",Float)=0
        _WetMask("Authored courtyard puddle footprint", 2D) = "black" {}
        [Normal] _BumpMap("Stone normal", 2D) = "bump" {}
        [MainColor] _BaseColor("Stone tint", Color) = (0.60, 0.66, 0.71, 1)
        _Smoothness("Dry smoothness", Range(0,1)) = 0.28
        _Metallic("Metallic", Range(0,1)) = 0.03
        _BumpScale("Normal strength", Range(0,2)) = 0.65
        _Wetness("Wet pool amount", Range(0,1)) = 1
        _RainWetness("Rain film on exposed stone",Range(0,1))=0
        _WaterLayer("Separate standing water above floor", Float) = 0
        _WorldScale("World texture scale", Float) = 0.18
        _PatinaStrength("Weathering strength", Range(0,1)) = 0.6
        _Distant("Distant ruin height haze", Range(0,1)) = 0
        _Wind("Grass wind", Float) = 0
        _ReflectionStrength("Planar reflection strength", Range(0,2)) = 0.85
        _ReflectionDistortion("Planar reflection distortion", Range(0,0.03)) = 0.003
        _ReflectionHeightRange("Reflection plane height range", Float) = 0.12
        [Enum(UnityEngine.Rendering.CullMode)] _Cull("Cull", Float) = 2
        [Enum(UnityEngine.Rendering.BlendMode)] _SrcBlend("Source blend",Float)=5
        [Enum(UnityEngine.Rendering.BlendMode)] _DstBlend("Destination blend",Float)=10
    }
    SubShader
    {
        Tags { "RenderPipeline"="UniversalPipeline" "RenderType"="Opaque" "Queue"="Geometry" "UniversalMaterialType"="Lit" }
        LOD 300
        HLSLINCLUDE
        #define _CLEARCOAT 1
        #define _SPECULAR_SETUP 1
        #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"
        #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Lighting.hlsl"

        TEXTURE2D(_BaseMap); SAMPLER(sampler_BaseMap);
        TEXTURE2D(_DetailMap); SAMPLER(sampler_DetailMap);
        TEXTURE2D(_DetailNormal); SAMPLER(sampler_DetailNormal);
        TEXTURE2D(_MicroNormal); SAMPLER(sampler_MicroNormal);
        TEXTURE2D(_MicroRoughness); SAMPLER(sampler_MicroRoughness);
        TEXTURE2D(_MineralColor); SAMPLER(sampler_MineralColor);
        TEXTURE2D(_RoughnessMap); SAMPLER(sampler_RoughnessMap);
        TEXTURE2D(_StoneAO); SAMPLER(sampler_StoneAO);
        TEXTURE2D(_WetMask); SAMPLER(sampler_WetMask);
        TEXTURE2D(_BumpMap); SAMPLER(sampler_BumpMap);
        TEXTURE2D(_VesperPlanarReflection); SAMPLER(sampler_VesperPlanarReflection);
        float4x4 _VesperReflectionVP;
        float4 _VesperReflectionPlane; // xyz normal, w signed plane distance
        float4 _VesperReflectionTexelSize;
        float _VesperReflectionAvailable;
        float _VesperShadowDiagnostic;
        float _VesperStoneDiagnostic; // opt-in Editor evidence, zero in players
        CBUFFER_START(UnityPerMaterial)
            float4 _BaseMap_ST;
            half4 _BaseColor;
            half _Smoothness;
            half _Metallic;
            half _BumpScale;
            half _Wetness;
            half _RainWetness;
            half _WaterLayer;
            half _Photographic;
            float _MineralScale;
            half _MineralColorStrength;
            half4 _MineralNormalCenter;
            float _WorldScale;
            half _PatinaStrength;
            half _Distant;
            half _Wind;
            half _ReflectionStrength;
            half _ReflectionDistortion;
            float _ReflectionHeightRange;
        CBUFFER_END

        struct Attributes
        {
            float4 positionOS : POSITION;
            float3 normalOS : NORMAL;
            float2 uv : TEXCOORD0;
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
            float2 uv : TEXCOORD4;
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
        // Preserve the browser's deliberately restrained moon specular while
        // letting nearby fire illuminate the water film. A single shared coat
        // gain produces a silver wash when the orbit crosses the moon direction.
        half3 WaterLight(Light light,InputData inputData,half amount)
        {
            if(amount<.001) return 0;
            half3 n=normalize(inputData.normalWS),v=inputData.viewDirectionWS,l=light.direction;
            half3 tangent=normalize(cross(abs(n.z)>.9?half3(0,1,0):half3(0,0,1),n));
            half3 bitangent=cross(n,tangent),h=SafeNormalize(l+v);
            half nv=saturate(dot(n,v)),nl=saturate(dot(n,l));
            float ax=.17,ay=.45;
            float hx=dot(h,tangent)/ax,hy=dot(h,bitangent)/ay,hz=saturate(dot(h,n));
            float d=1/(PI*ax*ay*pow(hx*hx+hy*hy+hz*hz,2)+.00001);
            float k=.10,g=nv/(nv*(1-k)+k)*nl/(nl*(1-k)+k);
            float f=.025+.975*pow(1-saturate(dot(v,h)),5);
            float spec=min(12,d*g*f/max(.001,4*nv));
            return light.color*(light.distanceAttenuation*light.shadowAttenuation)*spec*amount;
        }
        half4 CourtyardLighting(InputData inputData,SurfaceData surfaceData)
        {
            BRDFData brdf;InitializeBRDFData(surfaceData,brdf);
            BRDFData coat=CreateClearCoatBRDFData(surfaceData,brdf);
            half4 shadowMask=CalculateShadowMask(inputData);
            AmbientOcclusionFactor ao=CreateAmbientOcclusionFactor(inputData,surfaceData);
            Light moon=GetMainLight(inputData,shadowMask,ao);
            if(_VesperShadowDiagnostic>.5)return half4(moon.shadowAttenuation.xxx,1);
            MixRealtimeAndBakedGI(moon,inputData.normalWS,inputData.bakedGI);
            half3 color=GlobalIllumination(brdf,coat,surfaceData.clearCoatMask,inputData.bakedGI,ao.indirectAmbientOcclusion,inputData.positionWS,inputData.normalWS,inputData.viewDirectionWS,inputData.normalizedScreenSpaceUV);
            half3 indirect=color;
            BRDFData moonBRDF=brdf;
            #if !defined(_AUTHORED_STONE_UV)
            moonBRDF.specular*=.8;
            #endif
            color+=LightingPhysicallyBased(moonBRDF,coat,moon,inputData.normalWS,inputData.viewDirectionWS,surfaceData.clearCoatMask*.20,false);
            half3 directMoon=color-indirect;
            half3 beforePoints=color;
            #if defined(_ADDITIONAL_LIGHTS)
            uint pixelLightCount=GetAdditionalLightsCount();
            #if USE_CLUSTER_LIGHT_LOOP
            [loop]for(uint lightIndex=0;lightIndex<min(URP_FP_DIRECTIONAL_LIGHTS_COUNT,MAX_VISIBLE_LIGHTS);lightIndex++){
                CLUSTER_LIGHT_LOOP_SUBTRACTIVE_LIGHT_CHECK
                Light light=GetAdditionalLight(lightIndex,inputData,shadowMask,ao);
                color+=LightingPhysicallyBased(moonBRDF,coat,light,inputData.normalWS,inputData.viewDirectionWS,surfaceData.clearCoatMask*.09,false);
            }
            #endif
            LIGHT_LOOP_BEGIN(pixelLightCount)
                Light light=GetAdditionalLight(lightIndex,inputData,shadowMask,ao);
                color+=LightingPhysicallyBased(brdf,coat,light,inputData.normalWS,inputData.viewDirectionWS,surfaceData.clearCoatMask*.2,false);
                color+=WaterLight(light,inputData,surfaceData.clearCoatMask*.8);
            LIGHT_LOOP_END
            #endif
            if(_VesperStoneDiagnostic>2.5&&_VesperStoneDiagnostic<3.5)return half4(indirect,1);
            if(_VesperStoneDiagnostic>3.5&&_VesperStoneDiagnostic<4.5)return half4(directMoon,1);
            if(_VesperStoneDiagnostic>4.5)return half4(color-beforePoints,1);
            return half4(color+surfaceData.emission,surfaceData.alpha);
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
            // An authored drainage mask defines bounded irregular standing water.
            float2 p = float2(-positionWS.x, positionWS.z);
            float2 maskUV=float2((p.x+7.8)/18,1-(p.y+8)/26);
            float mask=max(SAMPLE_TEXTURE2D(_WetMask,sampler_WetMask,maskUV).r,max(SAMPLE_TEXTURE2D(_WetMask,sampler_WetMask,maskUV+float2(.018,0)).r,SAMPLE_TEXTURE2D(_WetMask,sampler_WetMask,maskUV-float2(.018,0)).r));
            float wet=smoothstep(.12,.8,mask);
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
        float2 DetailUV(float2 uv,half3 color)
        {
            float angle=frac(dot(color,float3(17,31,47)))*6.283185;
            float variation=frac(dot(color,float3(71,29,13)));
            float sn=sin(angle),cs=cos(angle);
            return mul(float2x2(cs,-sn,sn,cs),uv*3.1*(.75+variation));
        }
        half3 StoneSurfaceNormal(float3 p,half3 n,float2 uv,float2 detailUV,half wet,out half3 normalTS)
        {
            normalTS=half3(0,0,1);
            // Submerged stone keeps its own relief; only the separate water
            // plane has a flat normal. Do not flatten the same surface twice.
            #if defined(_SEPARATE_WATER)
            wet=0;
            #endif
            // Wet rock remains rock. The separate water mesh owns a flat water
            // normal; rain film on masonry must retain its fractured relief.
            half3 waterNormal=n;
            float2 normalUV=uv;
            #if defined(_PHOTOGRAPHIC_STONE)
                normalUV=detailUV;
                #if defined(_AUTHORED_STONE_UV)
                // Slab relief is now real geometry. The enlarged scan normal
                // must not reproduce its five-times-enlarged grain as lumps.
                normalTS=UnpackNormalScale(SAMPLE_TEXTURE2D(_DetailNormal,sampler_DetailNormal,normalUV),_BumpScale*.40*lerp(1,.70,wet));
                #else
                normalTS=UnpackNormalScale(SAMPLE_TEXTURE2D(_DetailNormal,sampler_DetailNormal,normalUV),1.7*lerp(1,.70,wet));
                #endif
            #else
                normalTS=UnpackNormalScale(SAMPLE_TEXTURE2D(_BumpMap,sampler_BumpMap,normalUV),_BumpScale*.04*lerp(1,.16,wet));
            #endif
            half3 result=PerturbedNormal(p,waterNormal,normalUV,normalTS);
            #if defined(_AUTHORED_STONE_UV)
            // The scanned heightfield carries slabs/joints. A separate measured
            // mineral frequency restores fine rough grain within those slabs;
            // it never changes their geometry, UV alignment or pool boundaries.
            float2 microUV=p.xz*_MineralScale;
            half3 mineral=UnpackNormalScale(SAMPLE_TEXTURE2D(_MicroNormal,sampler_MicroNormal,microUV),1.05);
            mineral.xy-=_MineralNormalCenter.xy*1.05;
            mineral=normalize(mineral);
            result=PerturbedNormal(p,result,microUV,mineral);
            #endif
            return result;
        }
        Varyings StoneVertex(Attributes input)
        {
            Varyings output=(Varyings)0;
            UNITY_SETUP_INSTANCE_ID(input);
            UNITY_TRANSFER_INSTANCE_ID(input,output);
            UNITY_INITIALIZE_VERTEX_OUTPUT_STEREO(output);
            input.positionOS.x += sin(_Time.y*1.5+input.positionOS.x*1.7+input.positionOS.z)*input.positionOS.y*.09*_Wind;
            VertexPositionInputs p=GetVertexPositionInputs(input.positionOS.xyz);
            output.positionCS=p.positionCS;
            output.positionWS=p.positionWS;
            output.normalWS=TransformObjectToWorldNormal(input.normalOS);
            output.fogAndVertexLight=half4(ComputeFogFactor(p.positionCS.z),VertexLighting(p.positionWS,output.normalWS));
            output.shadowCoord=GetShadowCoord(p);
            output.color=input.color;
            output.uv=input.uv;
            return output;
        }
        ENDHLSL

        Pass
        {
            Name "ForwardLit"
            Blend [_SrcBlend] [_DstBlend]
            Tags { "LightMode"="UniversalForwardOnly" }
            Cull [_Cull] ZWrite On ZTest LEqual
            HLSLPROGRAM
            #pragma target 3.5
            #pragma vertex StoneVertex
            #pragma fragment StoneFragment
            #pragma shader_feature_local_fragment _PHOTOGRAPHIC_STONE
            #pragma shader_feature_local_fragment _AUTHORED_STONE_UV
            #pragma shader_feature_local_fragment _SEPARATE_WATER
            #pragma multi_compile_instancing
            #pragma multi_compile_fog
            #pragma multi_compile _ _MAIN_LIGHT_SHADOWS _MAIN_LIGHT_SHADOWS_CASCADE _MAIN_LIGHT_SHADOWS_SCREEN
            #pragma multi_compile _ _ADDITIONAL_LIGHTS_VERTEX _ADDITIONAL_LIGHTS
            #pragma multi_compile_fragment _ _ADDITIONAL_LIGHT_SHADOWS
            #pragma multi_compile_fragment _ _SHADOWS_SOFT _SHADOWS_SOFT_LOW _SHADOWS_SOFT_MEDIUM _SHADOWS_SOFT_HIGH
            #pragma multi_compile_fragment _ _SCREEN_SPACE_OCCLUSION
            #pragma multi_compile_fragment _ _LIGHT_COOKIES
            #pragma multi_compile _ _CLUSTER_LIGHT_LOOP

            half4 StoneFragment(Varyings input) : SV_Target
            {
                UNITY_SETUP_INSTANCE_ID(input);
                UNITY_SETUP_STEREO_EYE_INDEX_POST_VERTEX(input);
                half3 geometricNormal=normalize(input.normalWS);
                float2 uv=StoneUV(input.positionWS,geometricNormal);
                half4 grain=half4(1,1,1,1);
                float surfaceVariation=frac(dot(input.color.rgb,float3(71,29,13)));
                float2 detailUV=DetailUV(uv,input.color.rgb);
                #if defined(_AUTHORED_STONE_UV)
                detailUV=input.uv;
                #endif
                #if defined(_PHOTOGRAPHIC_STONE)
                half3 detail=SAMPLE_TEXTURE2D(_DetailMap,sampler_DetailMap,detailUV).rgb;
                half detailLuma=dot(detail,half3(.2126,.7152,.0722));
                half3 photographicStone=lerp(detail,detailLuma.xxx,.82)*1.35*half3(.92,.99,1.06);
                grain.rgb=photographicStone;
                #if defined(_AUTHORED_STONE_UV)
                // Preserve the slab-scale scan while the same second scan's
                // color, normal and roughness resolve at the viewing distance.
                // .161164 is Rock05's measured mean linear diffuse luminance;
                // monochrome modulation preserves the existing mineral palette.
                half3 mineralColor=SAMPLE_TEXTURE2D(_MineralColor,sampler_MineralColor,input.positionWS.xz*_MineralScale).rgb;
                half mineralLuma=dot(mineralColor,half3(.2126,.7152,.0722));
                grain.rgb*=lerp(1,mineralLuma/.1611642454,_MineralColorStrength);
                #endif
                #else
                grain=SAMPLE_TEXTURE2D(_BaseMap,sampler_BaseMap,uv);
                #endif
                half wet=max(WetPool(input.positionWS)*smoothstep(.80,.97,geometricNormal.y),_RainWetness*lerp(.35,1.15,surfaceVariation));
                half3 normalTS=half3(0,0,1);
                half3 surfaceNormal=StoneSurfaceNormal(input.positionWS,geometricNormal,uv,detailUV,wet,normalTS);
                float2 weatherUV=input.positionWS.xz+input.positionWS.y*float2(.51,.77);
                half patina=StoneNoise(weatherUV*1.7)*.50+StoneNoise(weatherUV*7.3)*.30+StoneNoise(weatherUV*28)*.20;

                SurfaceData surface=(SurfaceData)0;
                surface.albedo=grain.rgb*_BaseColor.rgb*input.color.rgb;
                surface.albedo*=lerp(1,lerp(.66,1.18,patina),_PatinaStrength)*lerp(1,lerp(.70,.48,saturate(_WaterLayer)),wet);
                surface.metallic=_Metallic;
                // Bare silicate stone uses dielectric F0 near .04. The old
                // water-like .025 plus halved moon specular survived the coat
                // glare diagnosis and suppressed the exposed mineral glints.
                surface.specular=half3(.04,.04,.04);
                // Three's wet slab has roughness .43; the first native pass used
                // .24 and exaggerated the broad moon/point-light specular sheen.
                surface.smoothness=saturate(lerp(saturate(_Smoothness+(surfaceVariation-.5)*.18),.84,wet)-(1-grain.g)*.065);
                #if defined(_PHOTOGRAPHIC_STONE)
                half measuredDrySmooth=saturate((1-SAMPLE_TEXTURE2D(_RoughnessMap,sampler_RoughnessMap,detailUV).r)*.62+.035);
                measuredDrySmooth=lerp(measuredDrySmooth,.34+(1-SAMPLE_TEXTURE2D(_RoughnessMap,sampler_RoughnessMap,detailUV).r)*.18,saturate(_WaterLayer));
                half measuredWetSmooth=lerp(.84,.60,saturate(_WaterLayer));
                #if defined(_AUTHORED_STONE_UV)
                // Photogrammetric paving contains dusty filled seams as well as
                // slabs. Preserve measured variation without coating the entire
                // scanned surface in the old polished-stone response.
                half mineralRough=SAMPLE_TEXTURE2D(_MicroRoughness,sampler_MicroRoughness,input.positionWS.xz*_MineralScale).r;
                half mineralVariation=clamp((mineralRough-.515)*1.7,-.15,.15);
                measuredDrySmooth=saturate(.27+(1-SAMPLE_TEXTURE2D(_RoughnessMap,sampler_RoughnessMap,detailUV).r)*.14-mineralVariation*.55);
                measuredWetSmooth=clamp(.58-mineralVariation,.43,.73);
                #endif
                surface.smoothness=lerp(measuredDrySmooth,measuredWetSmooth,wet);
                #endif
                surface.normalTS=normalTS;
                #if defined(_PHOTOGRAPHIC_STONE)
                surface.occlusion=SAMPLE_TEXTURE2D(_StoneAO,sampler_StoneAO,detailUV).r;
                #else
                surface.occlusion=lerp(.94,1,patina);
                #endif
                surface.alpha=1;
                if(_VesperStoneDiagnostic>.5&&_VesperStoneDiagnostic<1.5)return half4(surface.albedo,1);
                if(_VesperStoneDiagnostic>1.5&&_VesperStoneDiagnostic<2.5)return half4(surfaceNormal*.5+.5,1);
                // Source coat energy was explicitly reduced to 14% direct / 24%
                // indirect. Match that effective energy rather than its raw .75
                // coat parameter. Real planar imagery remains independent below.
                surface.clearCoatMask=(wet*.72+(1-wet)*.20*saturate(_WaterLayer))*lerp(1,lerp(.38,1,smoothstep(.1,.2,input.positionWS.y)),_WaterLayer);
                surface.clearCoatSmoothness=.86;
                #if defined(_AUTHORED_STONE_UV)
                // A second coat below the real water surface caused the broad
                // moon glints diagnosed at player41 orbit frame0129. Exposed
                // scanned rock uses its own measured BRDF, pools their water.
                surface.clearCoatMask=0;
                #endif

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
                half4 color=CourtyardLighting(lighting,surface);
                if(_VesperShadowDiagnostic>.5)return color;
                color.rgb*=.78;

                #if !defined(_SEPARATE_WATER)
                float planeDistance=abs(dot(float4(input.positionWS,1),_VesperReflectionPlane));
                half planeWeight=1-smoothstep(_ReflectionHeightRange*.5,max(.001,_ReflectionHeightRange),planeDistance);
                float4 reflectionPosition=mul(_VesperReflectionVP,float4(input.positionWS,1));
                float2 reflectionUV=reflectionPosition.xy/max(.0001,reflectionPosition.w)*.5+.5;
                #if UNITY_UV_STARTS_AT_TOP
                reflectionUV.y=1-reflectionUV.y;
                #endif
                reflectionUV+=normalTS.xy*_ReflectionDistortion + float2(sin(input.positionWS.x*51+sin(input.positionWS.z*22)+_Time.y*.8)*.00016,0);
                half edge=smoothstep(0,.035,min(min(reflectionUV.x,1-reflectionUV.x),min(reflectionUV.y,1-reflectionUV.y)));
                half inFront=step(.0001,reflectionPosition.w);
                half reflectWeight=wet*planeWeight*edge*inFront*_VesperReflectionAvailable*step(.001,_ReflectionStrength);
                [branch] if(reflectWeight>.001)
                {
                    float2 blur=float2(0,.032);
                    half3 reflection=SAMPLE_TEXTURE2D(_VesperPlanarReflection,sampler_VesperPlanarReflection,reflectionUV).rgb*.26;
                    reflection+=(SAMPLE_TEXTURE2D(_VesperPlanarReflection,sampler_VesperPlanarReflection,reflectionUV+float2(.016,0)).rgb+SAMPLE_TEXTURE2D(_VesperPlanarReflection,sampler_VesperPlanarReflection,reflectionUV-float2(.016,0)).rgb)*.12;
                    reflection+=(SAMPLE_TEXTURE2D(_VesperPlanarReflection,sampler_VesperPlanarReflection,reflectionUV+blur).rgb+SAMPLE_TEXTURE2D(_VesperPlanarReflection,sampler_VesperPlanarReflection,reflectionUV-blur).rgb)*.14;
                    reflection+=(SAMPLE_TEXTURE2D(_VesperPlanarReflection,sampler_VesperPlanarReflection,reflectionUV+blur*2).rgb+SAMPLE_TEXTURE2D(_VesperPlanarReflection,sampler_VesperPlanarReflection,reflectionUV-blur*2).rgb)*.07;
                    reflection+=(SAMPLE_TEXTURE2D(_VesperPlanarReflection,sampler_VesperPlanarReflection,reflectionUV+blur*3).rgb+SAMPLE_TEXTURE2D(_VesperPlanarReflection,sampler_VesperPlanarReflection,reflectionUV-blur*3).rgb)*.04;
                    reflection=max(reflection,half3(.025,.048,.070));
                    half grazing=1-saturate(dot(geometricNormal,lighting.viewDirectionWS));
                    half fresnel=.075+.60*grazing*grazing*grazing;
                    half luma=dot(reflection,half3(.2126,.7152,.0722));
                    half broken=smoothstep(.38,.65,StoneNoise(input.positionWS.xz*float2(6,24))*.6+StoneNoise(input.positionWS.xz*float2(19,65))*.4);
                    half warm=saturate((reflection.r-reflection.g)*5);
                    half waterBlend=saturate(reflectWeight*lerp(.65,.95,warm)*(.35+broken*.65)*_ReflectionStrength);
                    color.rgb=lerp(color.rgb,reflection,waterBlend);
                }
                #endif
                color.rgb=MixFog(color.rgb,lighting.fogCoord);
                // The browser's distant architecture merges into blue valley
                // haze with depth below the courtyard. Near stone is unchanged.
                half distantHaze=(1-smoothstep(-21,1,input.positionWS.y))*.35*saturate(_Distant);
                color.rgb=lerp(color.rgb,half3(.014,.033,.050),distantHaze);
                float distantAlpha=lerp(1,smoothstep(-16,2,input.positionWS.y),saturate(_Distant));
                float foundationAlpha=smoothstep(-12,-4,input.positionWS.y);
                return half4(color.rgb,distantAlpha*foundationAlpha);
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
            Cull [_Cull] ZWrite On ColorMask R
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
            Cull [_Cull] ZWrite On
            HLSLPROGRAM
            #pragma target 3.5
            #pragma vertex StoneVertex
            #pragma fragment StoneNormalsFragment
            #pragma shader_feature_local_fragment _PHOTOGRAPHIC_STONE
            #pragma shader_feature_local_fragment _AUTHORED_STONE_UV
            #pragma shader_feature_local_fragment _SEPARATE_WATER
            #pragma multi_compile_instancing
            #pragma multi_compile_fragment _ _GBUFFER_NORMALS_OCT
            half4 StoneNormalsFragment(Varyings input) : SV_Target
            {
                UNITY_SETUP_INSTANCE_ID(input);
                half3 n=normalize(input.normalWS);
                float2 uv=StoneUV(input.positionWS,n);
                #if defined(_SEPARATE_WATER)
                half wet=0;
                #else
                half variation=frac(dot(input.color.rgb,float3(71,29,13)));
                half wet=max(WetPool(input.positionWS)*smoothstep(.80,.97,n.y),_RainWetness*lerp(.35,1.15,variation));
                #endif
                half3 normalTS=half3(0,0,1);
                float2 detailUV=DetailUV(uv,input.color.rgb);
                #if defined(_AUTHORED_STONE_UV)
                detailUV=input.uv;
                #endif
                n=StoneSurfaceNormal(input.positionWS,n,uv,detailUV,wet,normalTS);
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
