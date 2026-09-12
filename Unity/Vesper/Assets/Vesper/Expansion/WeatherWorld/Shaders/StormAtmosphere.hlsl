// Directionless sheet lightning. Global exposure performs the screen-wide pulse.
float4 _WeatherFlashState; // intensity, broad event, player progress, night weight
half3 WeatherFog(half3 color,half fogFactor,float3 world){
 return MixFog(color,fogFactor);
}
half3 WeatherWetFlash(float3 normal,float wet){
 return half3(.025,.035,.05)*wet*_WeatherFlashState.x;
}
half3 WeatherSurfaceLight(float3 world){
 return half3(.045,.055,.075)*_WeatherFlashState.x;
}
