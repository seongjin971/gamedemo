# Higgsfield environment heroes

Generated through the authenticated Higgsfield CLI under the user's explicit credit authorization. Complete prompts, job IDs, original result URLs and returned parameters are in `*-job.json`; cost accounting is in `provenance.json`. Original provider GLBs are retained unchanged. No credentials or third-party source media are stored here.

## Practical shortlist

- **CW_HF_Limestone**: clear improvement over the initial manually generated rock kit. Irregular fractured shelves and dense realistic stone PBR detail. Normalized to 5 m width, ground-centered pivot. Use LOD0 for foreground hero outcrops and LOD1 for repeated medium-distance placements. Patchy moss is sparse; the dominant surface remains pale limestone.
- **CW_HF_GothicButtress**: useful ornate damaged stone pier/wall fragment, normalized to 5 m height. The model has carved Gothic moldings and broken side masonry. It did **not** realize the prompt's open window: use it as a solid pier/buttress, never as a walk-through arch.
- **CW_HF_AlpineFir**: natural bark and irregular woody structure, but Tripo fused many needle sprays into thick leafy surfaces. Consider mid-distance only, pending the alternate Hunyuan fir trial.
- **CW_HF_RiverAlder**: botanical shape failed. The output has sparse spiky clusters instead of natural alder leaves. Preserve for comparison; not recommended as waterside hero foliage. The original custom birch is safer until a better tree is accepted.
- **CW_HF_AlpineFir_Hunyuan**: rejected after direct Blender preview. The alternate model produced smooth stacked foliage plates with less botanical detail than Tripo. Preserved separately as comparison evidence; do not use for the scene's fir improvement.

## Unity files and material mapping

Exports are additive under `Assets/Vesper/Expansion/ContinuousWorld/Art/HiggsfieldAssets/<model>/`. Each directory contains LOD0 and LOD1 FBXs, source-resolution PNG PBR maps, a prepacked Unity metallic/smoothness map and a manifest. All geometry is explicitly triangulated and normalized with the bottom-center pivot at ground. FBX uses Y-up/-Z-forward; source blend and GLB normalization records use Blender Z-up.

Read each manifest's material `texture_inputs`; do not assume image numbering for every provider. For Tripo exports:

- Texture0: BaseColor, sRGB.
- Texture1: tangent-space OpenGL normal, import as a Unity normal map.
- Texture2: ORM with **R=occlusion, G=roughness, B=metallic**, linear. Do not feed this directly to Unity's metallic/smoothness slot.
- MetallicSmoothness0: prepared Unity map, **R=metallic, A=1-roughness**, linear.

Source maps are 4096 square. Unity's texture import size/compression should be chosen against actual camera distance and memory measurements; it need not retain every source map at full resolution. If using Unity's occlusion slot, that shader expects its AO convention; read the ORM red channel or repack it rather than treating roughness as AO. No Unity material/shader/importer settings are edited by this asset package.

`prepare_assets.py` imports the original GLB, extracts PBR maps, applies documented scale/pivot, sanitizes and explicitly triangulates meshes, exports full and 40% LOD meshes and renders a Blender preview. `--no-render` skips only the preview. `audit_assets.py` independently reimports FBXs and checks mesh counts, finite coordinates, zero-area triangles, triangle-only topology, UV presence and texture reference existence. Evidence is under `.dream-loop/continuous-world/higgsfield-assets`.

These are asset-level checks and previews. They do not establish Unity frame rate, material appearance under the game's weather, navigation safety, or user acceptance.
