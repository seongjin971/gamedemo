# Primary fire-reflection diagnosis — candidate55

Status: source/geometry evidence and CPU ray model; native isolation still required. Read-only audit performed while root prepared candidate56. No Unity scene, shader, source bitmap, or geometry was changed by this audit.

## Finding

The current bright fire core is physically behind the bowl/coal/log assembly from the reflected camera. This is a strong, quantitatively supported cause of the weak reflected core. It is not yet an isolated native causal result, and does not explain every remaining water defect.

The actual candidate55 full and reflection-full PNGs were opened. The reflection has narrow surviving fire tongues around the two pedestal positions. The PNG is clipped display evidence, not linear radiance measurement. Separate floating-point EXR/JSON measurements below establish the energy changes.

## Actual source and imported geometry

Source: `src/world.js`, `brazier()` (around lines334–347). Import: `Unity/Vesper/Assets/Vesper/Import/unity-scene.json`, corresponding `unity-geometry-*.json`, and `Editor/VesperImport.cs`.

The source bowl is `CylinderGeometry(.59,.34,.35,4,1,true)` at Y1.28, rotated45 degrees. It is an open, four-sided tapered bowl, not a circular bowl with radius0.4. The bridge's exact transformed vertices give:

- Bowl: bottomY1.105000003; topY1.454999997; upper square half-side0.417192982 (nominal .59/sqrt(2)).
- Coal octagon: Y1.339999999–1.440000001; top circumradius0.39.
- Each of six horizontal five-sided logs: Y1.329999996–1.492811529. Exact lateral jitter and quaternion differ between logs/emitters.
- Separate lower bronze plinth is centeredY1.08 with height.13, topY1.145. It is not the upper bowl rim. It was excluded from the local ray model below; possible additional plinth/pedestal occlusion remains uncounted.

Native fire centers are X1.65 and X−6.9, both Z−1.45; import mirrors browser X. Actual source bridge snapshots include the browser animation's sampled TRS, rather than the nominal original Sprite centerY2.06/height1.65:

| Native centerX | Sprite bridge UUID | Builder-adjusted centerY | Actual height | Quad bottom/topY |
|---|---|---:|---:|---|
| 1.65 | `729cf16b-4dce-4787-9f92-ea129ce76c62` | 2.130069891 | 1.475567931 | 1.392285925 / 2.867853856 |
| −6.9 | `fb9753be-21b5-4745-b30a-868495343eb0` | 2.126030987 | 1.575790472 | 1.338135751 / 2.913926223 |

Builder adds Y+.11 to each imported flame. Widths are respectively1.299799804 and1.334292411. `VesperAtmosphereCapture` assigns camera rotation to billboards and shader `_Time.y=2.3`. `VesperAtmosphereMotion` lacks ExecuteAlways, so its Play-mode size/position oscillation is not applied by these Edit-mode captures. Source UV warp is active in the shader.

Current `AtmosphereFlame.shader` with `_Upright=1` uses world-vertical localY and camera horizontal localX in both cameras. `_SourceRadiance=1` bypasses the older procedural density/core mask. The relevant distribution is decoded texture RGB × (5.5,5.5,4.5) × texture alpha ×1.044874, followed by black fog. Depth test is LEqual, depth writing off, additive blending, Cull Off. The old shader variable named `core` does not define current luminous core placement.

## Reflection ray condition

`VesperAtmosphereCapture.cs` full camera has azimuth.46, elevation.72, ortho half-height14.1/1.27. Reflection plane is Y−.005. `VesperPlanarReflection` explicitly uses source view matrix × horizontal reflection matrix, preserves the projection, and enables ordinary depth occlusion. Its height clip is near the floor, not near the flame.

The direction from a flame point towards this reflected camera is proportional to `(−sin(.46), −tan(.72), cos(.46))`. From the bowl center, the near square boundary is .417193/cos(.46)=approximately.4656m away horizontally. Therefore the emitter centerline must satisfy:

`Y >= 1.455 + (.417193 / cos(.46)) * tan(.72) = 1.863353964m`

to pass above the upper near rim. Equivalently, centerline texture V must exceed approximately.3193 for the X1.65 fire or.3333 for the X−6.9 fire. This threshold varies across the quad width and with orbit elevation/azimuth. It is not a claim that every pixel below that height intersects the open bowl: finite bowl bottom and the separate coal/logs require triangle tests.

## Actual source core distribution

Read-only Pillow sampling of the unchanged1254×1254 FlameV16 bitmap to256×256 with BICUBIC; sRGB decoded by the standard piecewise transfer curve. No image edited or saved. UV V is bottom-origin. L is the direct linear source luminance specified above, before fog, warp, depth, mip/filtering and rasterization. The128×128 ray grid below also uses BICUBIC. This differs from the256×256 BILINEAR sampler in FlameV16/source-energy.json; do not combine the two grids' exact numerical results.

- L>.02 UV bbox: U.27930–.72070, V.05273–.94336. This is luminous support, not quad bounds.
- L>4 UV bbox: U.40039–.57617, V.08398–.52148; 663 sample pixels. This threshold is an explicit diagnostic definition of the high-radiance core.
- L>4 energy centroid: worldY1.720424 for X1.65; worldY1.688562 for X−6.9.
- L>4 full worldY bbox:1.516211–2.161772 and1.470478–2.159886 respectively. The upper endpoint is sparse; bbox alone hides the concentration below the rim threshold.
- All L>.02 energy centroid: worldY1.922926 and1.904817 respectively. The broad low-radiance tongues therefore extend higher than the compact high-radiance core.

Analytical upper-rim-only classification predicts48.31%/50.80% of source energy and88.08%/90.05% of the L>4 sample count below the local escape condition. The explicit triangle result below is the better model because it handles the finite bowl and logs/coal.

## CPU triangle occlusion check

128×128 direct-radiance samples, only samplesL>.02 tested. Each source sample was placed on the actual upright quad using its bridge TRS, actual unchanged UV orientation, builder Y offset, and full-camera horizontal axis. Rays were tested against the exact imported bridge triangles of that fire's bowl, coal and six logs, preserving individual quaternions and positional jitter. No generated masonry substitution is involved in those eight original non-instanced mesh objects.

| Native X | Source energy blocked by these8 bodies | L>4 sample count blocked |
|---|---:|---:|
| 1.65 | 48.651% | 93.077% (121/130) |
| −6.9 | 53.014% | 94.615% (123/130) |

First-hit source-energy attribution for X1.65: bowl14.772%, coal9.226%, logs24.653%. For X−6.9: bowl11.104%, coal7.095%, logs34.816%. These are fractions of all tested source energy, not exclusive blocker causality: removing one first-hit body may expose another farther body.

The ray model tests two-sided triangle intersections. A closed log/coal body has a front-facing entry surface; the visible exterior near bowl face is also the relevant physical obstruction. Nevertheless this remains a CPU model, not a measurement of native depth fragments. It excludes shader UV warp, importer mip sampling, main-water visibility/masking, fog, postprocessing, nearby pier and pedestal geometry. No percentage here is a measured screen-brightness loss or FPS result.

## Linear native evidence,54 versus55

`reflection-radiance-full.json` is produced by reading the floating-point RT, with bottom-origin peakY.54: peak8.035633,41 pixelsL>1,3 pixelsL>4.55: peak4.815847,140 pixelsL>1,9 pixelsL>4. Thus55 has a lower maximum and broader surviving radiance; the lower peak is not proof that reflected source energy became lower.

Read-only scan of each uncompressed floating-point `reflection-linear-full.exr` corroborated peaks and measured fixed projected fire neighborhoods. The EXR rows here are top-origin,1024×683. Warm predicate: R>1.3G and G>1.3B. These regions contain both flame and lit geometry and are not an emitter-only segmentation:

| Fixed top-origin region | 54 warm sumL / countL>1 | 55 warm sumL / countL>1 |
|---|---:|---:|
| X476–516,Y375–426 | 209.284 /36 | 350.260 /109 |
| X711–752,Y450–503 | 43.052 /3 | 100.654 /29 |

Projected centerline X is495.890 and731.429. For sourceY1.7, predicted top-origin reflectionY is394.175 and471.161; for the rim escape height1.863354 it is397.953 and474.939.54/55 left measured peak is atY401; right regional peak atY475. This spatial agreement supports the upper-survivor interpretation; without isolated emitter/depth captures it is not pixel-perfect emitter identification.

The existing54 `hdr-component-comparison.json` contains52/53/54, not55. Its warm-component measures are separate from the fixed-ROI measures above and must not be silently mixed.

## Required native isolation and V17 guidance

1. Keep the same saved scene, full camera, shader time, texture/gain, water, point lights and exposure. Capture baseline main + reflection PNG and linear EXR.
2. For one temporary reflection-only diagnostic, omit precisely the two bowls, two coal meshes and12 logs from the reflection culling mask. Identify by bridge mesh UUID plus exact world TRS; do not omit every bronze/dark material or pedestal batch. Preserve main-camera visibility. Compare the same linear ROI sum, high-radiance population and image silhouette. This isolates local opaque occlusion without changing source emission or water.
3. If useful, separately omit bowls only and then coal+logs only. First-hit CPU attribution is not a substitute for these independent masks. Optional emitter-only depth-disabled reflection diagnostic can establish the unoccluded ceiling, but is strictly a test, not the adopted rendering behavior.
4. V17 should preserve the original lower luminous contact and outer silhouette while extending substantial bright core radiance into V≈.34–.48, not merely whitening the bottom. That band lies above the centerline full-view rim escape threshold while remaining inside the existing quad. Quantify energy above/below the geometric escape boundary on the actual new bitmap before import. A bbox reachingV.52 is insufficient if nearly all high-radiance samples remain concentrated low.
5. Recheck full/orbit/zoom with the same physical quad and ordinary depth. Higher orbit elevation raises the threshold; a full-view-only repair can fail in motion. Preserve the visible fire-to-coal connection and avoid turning the whole source into a uniformly white strip.

Changing actual source radiance distribution is a physical-scene change that can improve both main and reflected fire. It does not by itself establish that the water integration, direct light range, reflections of other objects, visual target, or performance gate is complete.

## V17 pre-import extension — same geometry and gain

Root provided `Migration/Source/AtmosphereV2/FlameV17/flame-v17.png`, SHA256 `ebdee4969b509cd1f81c89ecc44d5514b14dbe7d3d6c23e0ed4c50b9fed2fd1c`. The actual bitmap was opened and inspected. Its broad bright body extends upward while recognizable outer tongues and low fire-to-coal contact remain. This is source-image review; it is not a Unity visual result.

The same two imported emitter TRS, eight local blockers per emitter, gain1.044874, BaseColor(5.5,5.5,4.5), BICUBIC grids and CPU ray algorithm were applied to both16 and17. Both full(.46,.72) and orbit(.70,.85) were tested. No bitmap was modified.

|256² source measure|V16|V17|
|---|---:|---:|
|Mean linear source luminance, BICUBIC|.267103182|.508956669|
|L>4 sample count|663|3605|
|L>4 energy-centroid V|.222381158|.272620274|
|L>4 UV bbox U / V|.40039–.57617 / .08398–.52148|.30273–.64258 / .05664–.79102|
|L>.02 luminous bbox U / V|.27930–.72070 / .05273–.94336|.27930–.72070 / .04883–.94336|

The V17 core centroid in native world coordinates is Y1.794556/Y1.767728. It still lies below the full centerline escape height, but significantly more high-radiance body extends above that height. The higher orbit centerline escape height is2.075918m, so even more core remains obstructed there.

|View, nativeX|Total energy blocked V16→V17|Unoccluded total sample-energy V16→V17|L>4 samples blocked V16→V17|Unoccluded L>4 energy V16→V17|
|---|---|---|---|---|
|Full,1.65|48.65%→51.42%|2175.19→3988.15|121/130→593/876|40.50→1323.09|
|Full,−6.9|53.01%→56.51%|1990.37→3570.06|123/130→634/876|31.77→1135.07|
|Orbit,1.65|68.24%→72.43%|1345.58→2263.09|130/130→815/876|0→268.77|
|Orbit,−6.9|70.40%→74.38%|1253.98→2103.16|130/130→822/876|0→237.52|

These energy sums are CPU source-sample sums at128², not projected RT sums. V17 creates a much larger surviving high-radiance body in this model. However the overall blocked-energy fraction actually increases. The absolute surviving total rises approximately1.83×/1.79× in full largely alongside a1.9055× BICUBIC source-mean increase. An equal-mean comparison would not predict a larger total escaped energy; it would still reveal a changed bright-core distribution. Thus this is not a clean occlusion-fraction improvement and should not be described as one.

For direct compatibility with the existing source-energy.json convention, an additional256² BILINEAR measurement gives meanL .262174246 forV16 and.504177726 forV17, approximately1.9231× at unchanged gain. This independently confirms that same gain is not same total emitted source energy. Native comparison should report both the changed source distribution and this increased emission, then review direct fire saturation and water appearance together. All CPU/model limitations above still apply.
