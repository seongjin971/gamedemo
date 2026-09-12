# Paving V13 delivery — source diagnostic candidate

Candidate45 full was directly inspected before this change. V12's 24 isolated raised bodies looked like scattered stepping stones on a flat bed. V13 now constructs neighboring photographed stones throughout the front courtyard. Original Paving V10/V11/V12 assets and downloaded maps are preserved. No Unity files were edited by this package.

## Stable import contract

- JSON: `paving-v13-mesh.json`, id `paving-v13-hybrid-scan-slabs`, name `PavingV13HybridScanSlabs`, `alreadyUnity: true`.
- SHA256: `dd46aefd74c0470bfea77fee2d22df8c72a1d2d47a75d18e7e6944c0c8f87e3c`.
- Identity Unity-world geometry. Flat arrays: positions/normals stride3, UV stride2, RGBA colors stride4, triangle indices stride3. Colors are all (1,1,1,1). Keep the exported positive face-cross/normal convention; do not reverse winding or mirror coordinates.
- Use the exported source UV with the same original Tiles130 maps. Effective art period remains 9.2 × 4.6 m, four times the published 2.3 × 1.15 m source area. V13 removes V12's selected local shrink; current stone scales are all1, so photo positions and source grain remain attached to the original source coordinates.
- Whole-ground bounds: X [-8.936228752,9.040660858], Z [-11.101970673,21.067903519] m. Y [-0.115000002,0.008338741] m.
- Independent water plane remains Y=-0.004. Of866 bodies,157 have some surface above it and709 lie wholly below. This is a geometry classification, not a rendered pool-coverage or connected-water result.
- Existing ground-only replacement scope remains. The exact rear row-segment/staircase void bed is preserved. New bodies occupy the existing front rectangle X[-8.936228752,9.040660858], Z[-1.567998648,21.067903519]. Rear ground remains a continuous heightfield; stairs and upper landing are separate and unchanged. The front bed's former overlap under the lowest stair nose is retained.

## Construction and actual coverage

Forty dominant source contours cover only52.3% of the original image. Following root's explicit approval,52 subordinate neighboring source regions were added, for92 distinct photo contours. These are manual Color/AO traces with bounded AO/height-gradient refinement, not semantic auto-segmentation. Repeat and clip those actual regions in their original positions; no random UV offset, arbitrary stone reordering or new rectangular grid is introduced.

The front rectangle is406.9231 m². Projected stone surfaces including sloping arrises occupy272.3521 m², or66.93%. Their flat inner caps occupy213.8899 m², or52.56%. The difference,14.37% of the foreground, is real bevel surface. Therefore this package meets60–75% coverage only when counting the complete stone top including its arrises; it does not claim60% flat-cap-only coverage. These are sums of projected body areas, not a separately measured polygon-union or rendered visible-area result.

All866 stone bodies are closed. Concave source outlines use ear-clipped caps and bottoms, with one microheight sample per cap triangle. Nominal contour sampling is190 mm plus the authored corners. Clipped remnants shorter than25 mm are removed before building bodies; exact bed coverage remains. Larger stones use32–52 mm nominal bevel widths and21–30 mm drop. Subordinate pieces use18–30 mm widths and13–19 mm drop. Local inset scales down to preserve valid convex strips:28 of866 bodies use reduced inset, minimum scale0.25. No validation tolerance was relaxed.

Cap planes vary independently around water level, retaining bounded2.8 mm source scan residual after removing each island's fitted base plane. The bed uses205 mm nominal samples and the previous40 mm source-height art amplitude. These vertical dimensions are authored, not measured scan elevations. Bed Y ranges[-0.063600004,-0.025597092]. Original Color, NormalGL, AO, roughness and height bytes are unchanged; preview NormalGL strength is0.4. Geometry does not resolve every4K texture pixel.

## Independent QA

`validate_hybrid.py` reads the exported JSON independently from Blender. It checks attributes, indices, winding, position-welded closure, signed volume, geometry-projected area, source UV, bounds and source hashes. Results are in `export-qa.json`.

| Check | Result |
|---|---:|
| Triangles / exported vertices | 141,312 /323,235 |
| Bed triangles | 36,032 |
| Positive / negative triangle-normal dot | 141,312 /0 |
| Degenerate triangles | 0 |
| Minimum triangle area | 0.0000002764 m² |
| Finite attributes, valid indices, lengths | pass |
| Unit normal range | 0.999999854–1.000000157 |
| Closed bodies, position-welded boundary edges | 866 /0 |
| Overfull edges per part | 0 |
| Signed closed volumes | all positive,0.00348–0.16258 m³ |
| Max complete-body projected-top/footprint error | 0.0000006807 m² |
| Projected area acceptance tolerance | 0.00001 m², unchanged |
| XZ bounds difference | <0.000000001 m |
| Recorded source hashes preserved | pass |

The large vertex count reflects flat normal splits, not additional triangle count. The bed is intentionally an open surface with818 welded outer/mask boundary edges. The JSON's aggregate308,084 unwelded boundary edges include normal-split vertex duplicates and are not a physical-hole count. Per-body closure is checked after position welding.

`PREFLIGHT_HISTORY.md` records rejected clipped/inset geometry and the strict repairs. Face orientation was not hidden by flipping isolated triangle indices. Body triangles are explicitly authored before geometry normals are computed; cap triangulation and each bevel strip are tested before export, and total projected area is independently checked after export.

## Direct preview review and limits

The final before-V12 neutral full, after-V13 neutral full/close, and actual4K textured full/close images were opened directly. The foreground now reads as neighboring paving across its width. V12's scattered24 isolated bodies are no longer the only raised elements. Actual source grain follows the stones and photo-filled gaps remain between them.

Two limitations are visible. Some flat-shaded cap triangles produce thin fan-shaped highlights in the neutral close image; the same relief is subdued by the real texture but not eliminated. The source's photographed courses and tile repetition remain visible. Larger and smaller source stone proportions are retained, so this is not a fully authored replacement with only large concept-style slabs. Rear ground remains continuous and its transition to the segmented front can be seen in the isolated asset preview. Raw photo color is warmer/brighter than the target under these lights. Actual Unity lighting, water/reflection, final native appearance and FPS are root's checks.

Before/after Blender cameras match each other. The `native-ground` filename denotes the native angle/elevation/scale diagnostic, not a certified pixel-identical Unity camera; the projection can be horizontally mirrored relative to native. A code-only cap-normal smoothing assessment is in `NORMALS_ASSESSMENT.md`. The stable V13 JSON is frozen for candidate47; no normal derivative is included here.

Preview paths: `previews/before-v12-neutral-native-ground.png`, `previews/after-v13-neutral-native-ground.png`, `previews/after-v13-textured-native-ground.png`, and the three corresponding `close` files. Builder: `build_hybrid_v13.py`; source contours: `source_seeds.json`; saved asset: `paving-v13.blend`; metadata: `hybrid-metadata.json`.

The first successful run's optional geometry-only quit request did not stop the Python script immediately, so it completed the six previews as well. Independent JSON QA passed during that batch. The canonical builder now exits the script explicitly after a geometry-only save. Future separated preview runs use `render_previews.py`, which requires a matching passed QA hash first. This control-flow correction does not modify the delivered mesh or its hash.
