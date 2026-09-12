from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
assets=ROOT/'Unity/Vesper/Assets/Vesper/Expansion/WeatherWorld'
for name in ['Ground','Road','WetStone']:
    p=assets/'Shaders'/f'{name}.shader'
    s=p.read_text(encoding='utf-8')
    s=s.replace('#include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Lighting.hlsl"','#include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Lighting.hlsl"\n#include "StormAtmosphere.hlsl"')
    s=s.replace('return half4(MixFog(color,i.fog),','color+=albedo*WeatherSurfaceLight(i.w);\n return half4(WeatherFog(color,i.fog,i.w),')
    p.write_text(s,encoding='utf-8')
source=ROOT/'Unity/Vesper/Assets/Vesper/Expansion/ContinuousWorld/WorldFoliage.shader'
s=source.read_text(encoding='utf-8').replace('Shader "Vesper/WorldFoliage"','Shader "Vesper/Weather/Foliage"')
s=s.replace('#include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Lighting.hlsl"','#include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Lighting.hlsl"\n#include "StormAtmosphere.hlsl"')
s=s.replace('return half4(MixFog(color,i.fog),1);','color+=leaf.rgb*WeatherSurfaceLight(i.w);return half4(WeatherFog(color,i.fog,i.w),1);')
(assets/'Shaders/Foliage.shader').write_text(s,encoding='utf-8')
print('W02 localized atmosphere added to isolated shaders')
