# Masonry V12 source delivery

Eight native JSON meshes are ready for a Unity integration comparison: `masonry-v12-0.json` through `masonry-v12-5.json`, plus `facade-v12-0.json` and `facade-v12-1.json`. The final geometry is pass4. `masonry-v12.blend` contains the normalized masters and two identical wall assemblies for comparison. Earlier rejected cube-based experiments and the face-flattened third pass are retained in explicitly named subdirectories; they are not delivery inputs.

The final method preserves V8's useful fractured body and top fissures. A monotone coordinate reshape compresses the broad projecting shoulder toward upright face planes. Near the perimeter, an old 0.10-unit shoulder depth becomes about 0.017 unit and an old 0.05-unit depth becomes about 0.00285 unit. Face centers receive only 20% of that displacement so their original uneven stone volume survives. This is a shape change, not a material change. Unequal finite arris losses, selected shallow mineral patches and broad open corner fractures on variants 2 and 5 are then added. There is no continuous new bevel. Dimensions are normalized; the physical size of wear depends on each instance's scale.

The eight normalized AABBs are exactly `[-0.5, +0.5]` on all Unity axes. Runtime decimation can move isolated extrema slightly; boundary overshoot is clamped and missing extrema are restored only when their displacement is below 0.002 unit. No full-mesh normalization stretches a damaged face back outward. Normals and topology are recalculated on the resulting mesh.

## Integration contract

Change the versioned source directory and filename prefix in the candidate builder's `LoadArchitecture`. Keep the existing `AppendStone` instance TRS, materials, and seed handling unless intentionally applying the separately reviewed coursing/material changes. JSON positions and normals are already in Unity coordinates, with triangle winding validated against their summed corner normals. Do not perform a second basis conversion or bake the Blender preview transforms. The inspection scale/spacing is not part of the export.

The JSON schema is `id`, `name`, `positions`, `normals`, `uv`, `indices`. The builder assigns its existing per-instance vertex color. The new meshes do not include material slots, colors, textures or scene placements. Root owns Unity Editor API import, materials, row layout and native rendering.

Final per-mesh triangle counts: 800, 800, 746, 800, 800, 782; facade 166 and 158. Total 5,052 versus the eight V8 source meshes' 4,340. Independent validation and hashes are in `independent-validation.json`. Welded closure and preserved original file hashes are in `build-validation.json`. All eight pass finite/array/index/bounds/normal/winding/degenerate/closure checks; native FPS remains unmeasured for these replacements.

## Reproduction and evidence

Run `build_masonry_v12.py` with Blender 5.2.1 in background mode using 4 threads. Run `validate_export.py` with normal Python. `render_variants_wide.py` adds a fully framed variant comparison from the saved blend without changing geometry or exports. Prefer `variants-before-wide-clay.png` and `variants-after-wide-clay.png`; the original closer variant view slightly crops the outermost stone. Wall comparison is `wall-before-clay.png` and `wall-after-clay.png` at the same camera, lights, material, instances, spacing and 1536x1024 resolution.

Only new MasonryV12 and its scratch directory were written. V8, Stair V11, Unity assets and all original sources remain unchanged. A native Rock05-material comparison is required before visual adoption.
