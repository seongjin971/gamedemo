# Candidate 48 water diagnosis

Bounded source-only work. No Unity files were changed and no Unity/Blender process was launched. `analyze_water.py` uses Python 3 and Pillow and writes `water-hit-report.json` in this directory. Original scene, PavingV14 geometry, and wet-mask hashes are in the report.

## Confirmed

- Installed Core `ShaderLibrary/Common.hlsl`, `ComputeNormalizedDeviceCoordinatesWithZ`, explicitly flips clip Y under `UNITY_UV_STARTS_AT_TOP` before the NDC-to-UV conversion. The current GPU projection (`GL.GetGPUProjectionMatrix(..., true)`) plus the StandingWater shader flip follows that same convention. Code alone does not support the proposed double-flip diagnosis.
- The legacy `reflection.png` is saved only for capture index 0 (slice, 1037x739 source), whereas `full.png` is index 1 (1536x1024 source, different camera). Those two images cannot establish pixel registration. Per-view matched reflection captures are needed.
- The actual candidate48 reflection PNG contains both flames. It contains a broad bright blue sky and dark scene silhouettes. Thus flames are not globally absent from the reflection render. PNG readback is RGB24 and cannot establish their unclipped HDR radiance.
- Current StandingWater has a single planar reflection texture fetch, with subpixel ripple displacement at 1024 width. It does not use the older opaque stone reflection branch's wide blur. The wet-mask itself has broad cloud-shaped patches.
- At full/zoom elevation .72 radians, the shader Fresnel is 0.0294702. With `color = reflection + direct/F` and `alpha = coverage*F`, source-alpha blending contributes `coverage*F*reflection + coverage*direct`. Therefore the gold point-light lobe is not attenuated by that Fresnel factor, while the reflected flame is. A gold patch does not by itself prove bad flame mapping.
- ReflectionSky emits linear RGB from (.12,.22,.33) to (.34,.49,.67), plus cloud <= .018. Stone IBL's OvercastStoneEnvironment is instead (.028..0352, .050..0604, .073..0866). These are materially different radiance fields. A coherent adjustment would make sky background sample the same overcast environment radiance used by stone, preserving the reflection of actual flame/geometry. Scaling the entire reflection RT would also weaken flame and is not equivalent.
- Reflection still has a 24-bit depth attachment. `requiresDepthTexture = Off` disables a sampled camera depth texture; it does not remove depth testing. The oblique plane clips at approximately Y=.020, which does not remove the flames near Y=2.

## CPU intersection results

For actual serialized flame centers, camera forward `d`, reflection height `hr`, and water height `hw`: `Pvirtual=(Px,2*hr-Py,Pz); t=(hw-Pvirtual.y)/d.y; W=Pvirtual+t*d`. There is no extra factor of two on the horizontal displacement. Reflection height -.005 and water height -.004 are retained distinctly.

| View | Flame | Water hit X,Z | Center coverage | Water minus floor Y |
| --- | --- | --- | --- | --- |
| full / zoom | left | -7.92350, .61580 | 1.0 | +4.37 mm |
| full / zoom | right | .62446, .61993 | 1.0 | +1.47 mm |
| orbit | left | -8.04433, -.09140 | 1.0 | +20.72 mm |
| orbit | right | .50338, -.08869 | 1.0 | +6.24 mm |

All center points are within the water quad. The full/zoom right northwest probe, 15 cm from center, has floor 8.76 mm above water and can suppress that local water surface. Orbit right northwest probe has coverage only .0777. These support partial shape clipping near the right flame, not complete center masking. The other 23 samples have coverage 1.0; the other 22 probe floors are below water.

The report is an exact vertical intersection with source triangles plus base-mip bilinear mask sampling (linear R, clamp, max of U and U±.018). It does not prove camera-ray visibility, cover the whole displaced billboard, or include other scene geometry. GPU mip/filter derivatives can differ. Full and zoom have identical directions, so their water intersections are identical despite different framing.

## Minimal native diagnostic

Use one frozen full camera/time and save its matched linear HDR reflection RT (EXR or RGBAHalf sample values), plus ordinary final PNG. Keep existing camera matrices and Y conversion initially.

1. Raw projected reflection: coverage forced to 1, direct light 0, ripple 0, opaque diagnostic output on the same water plane. This separates mapping from Fresnel/mask dilution. The core helper conversion should match the existing mapping exactly.
2. Coverage-only output at the same depth test. Pair with exported expected flame-center water pixels from `Camera.WorldToScreenPoint(W)`. If raw reflection is absent at a predicted point, a second raw frame with depth test Always distinguishes water occlusion from projection/RT content.
3. Existing blend/mask with direct term disabled. Compare against baseline to determine whether the flat gold patch is direct BRDF light. A complementary direct-only frame is useful if ambiguity remains.

Only after mapping is verified should sky-only environment coherence be changed. A lower shared overcast radiance is justified by the existing inconsistent environment contracts; exact artistic brightness still needs native comparison. Black geometry in the RT may be reflected undersides and dim ambient rather than missing lights; isolating reflection direct lighting would be a separate diagnostic if it persists.

## Sources inspected

- `Unity/Vesper/Assets/Vesper/Runtime/VesperPlanarReflection.cs`
- `Unity/Vesper/Assets/Vesper/Shaders/StandingWater.shader`, `ReflectionSky.shader`, `AtmosphereFlame.shader`, `AtmosphereStone.shader`
- `Unity/Vesper/Assets/Vesper/Editor/VesperAtmosphereBuild.cs`, `VesperAtmosphereCapture.cs`
- Installed URP `Runtime/FrameData/UniversalCameraData.cs`, `Runtime/ScriptableRenderer.cs`; installed Core `ShaderLibrary/Common.hlsl`.
- Direct views: `Migration/Reference/concept.png`, candidate48 `full.png`, `reflection.png`, and original wet-mask image.
