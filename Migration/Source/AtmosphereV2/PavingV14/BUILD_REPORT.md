# Paving V14 — larger aligned photographic slabs

Status: source frozen, independent QA passed, actual before/after Blender full/close images directly inspected. Root handles native import, water/material integration and FPS. Original V13 and all earlier meshes/maps remain unchanged. No Unity files were edited by this package.

## Frozen import contract

File: `paving-v14-mesh.json`.

SHA256: `00ee641f13bdc841a4d0fd531379380a33952ee8f952133e750380e9e4be5c59`.

The Geo object has id `paving-v14-hybrid-scan-slabs`, name `PavingV14HybridScanSlabs`, `alreadyUnity:true`. Use identity Unity-world placement. Positions/normals have stride3, UV stride2, RGBA colors stride4; colors are all1. Indices retain the established positive face-cross/normal convention. Do not mirror coordinates or reverse winding. Preserve the exported geometry normals and use exported UVs for all source maps.

The original ambientCG Tiles130 maps remain read-only in `../PavingV11/maps`. Published horizontal source area is2.3 ×1.15 m. Current source-height, contour and material UV period is12.4 ×6.2 m: an additional1.347826x enlargement from V13's9.2 ×4.6 m and total5.391304x art scale from the published source. This is explicit art direction, not newly measured photogrammetry. Geometry, bed height sampling and UVs all use the same new period. No source map was rescaled or rewritten.

Whole-ground bounds remain X[-8.936228752,9.040660858], Z[-11.101970673,21.067903519] m. Current Y is[-0.115000002,0.010417859]. The former front rectangle and rear row-segment/staircase void bed are preserved. New bodies cover the front rectangle Z[-1.567998648,21.067903519]; the rear remains a continuous source heightfield. Stairs and upper landing stay separate. The existing ground extension under the lowest stair nose is retained.

Independent water reference stays Y=-0.004. Ninety-four bodies have some vertices above it and399 lie wholly below. Bed Y is[-0.063600004,-0.027403038]. These figures do not certify rendered pool connectivity or water visibility. Contact14 horizontal pockets must be projected against this complete frozen floor's actual top surfaces, because changing the source period changes local heights. Metadata supplies every part range, cap/source polygon and per-stone plane.

## Change and direct visual decision

The actual concept and candidate47 full were opened side-by-side before building. The concept gives more weight to large angular rectangular slabs and restrained edge relief;47 had coherent paving but too many smaller rounded pads and some cap fan highlights. V14 therefore changes scale, physical rim relief and cap shading together in the separately approved bounded package. Normal smoothing alone was not treated as a pad-silhouette fix.

The same92 real photo contours,40 dominant and52 subordinate regions, now produce493 closed bodies instead of866. Their original photo positions and neighboring relationships are retained. No arbitrary shrink, shuffle or random UV offset is used. Nominal major shoulders remain32–52 mm wide; subordinate shoulders remain18–30 mm. Their systematic vertical drop is multiplied by0.75, giving major nominal15.75–22.5 mm and subordinate9.75–14.25 mm drops. Twelve bodies use a reduced inset to maintain valid bevel strips, minimum inset scale0.5.

Each body keeps its independent plane level and tilt. Cap normals are area-weighted only within that body's cap, using an explicit face attribute through triangulation. Bevels, sides and bottoms retain flat normals across the hard cap boundary. The floor is not averaged to global Y-up.

The final neutral full/close comparison shows larger broad rectangular faces and fewer repeated small pads. The thin fan-shaped cap lighting visible in V13 is no longer apparent in the inspected V14 neutral close image. Actual4K textured full/close images retain source grain and photo-aligned fissures on those faces. The change is useful for native diagnosis; it does not establish whole-concept acceptance.

Remaining visible limits: some small source stones still have rounded outlines, some perimeter lines remain strong, and the source's photographed courses/tile repetition persist. The rear continuous bed and its transition are visible in the isolated source preview. Raw photo color is warm and bright under neutral lights. Grain/glints, actual water BRDF, scene lighting and final native appearance remain root's material/capture work. Before/after Blender cameras match each other, but `native-ground` is an angle/elevation/scale diagnostic with the previously documented Blender/Unity projection convention difference, not certified pixel-identical native evidence.

## Strict topology and normal repair

The first V14 area-weighted normal preflight found17 nonpositive cap face/normal dots. No mesh was exported from that failed pass; `normal-preflight-rejection.json` preserves the failing triangle evidence. Thin ear triangles can amplify even a bounded1–3 mm sampled residual into a steep local slope. Reversing indices or relaxing the gate would not repair that geometry.

The builder now conditions only problematic residual vertices relative to each stone's own authored plane until cap face slopes fall within a12-degree cone. This preserves different planes between stones and keeps all accepted cap normals mutually compatible for area weighting. Across493 bodies,422 had at least one conditioned vertex;4,877 vertices were adjusted, with maximum height adjustment2.79996 mm and maximum16 iterations. Residual samples remain bounded by2.8 mm, but conditioned samples can be smaller or nearly planar. The original normal/grain map is unchanged. Matching shoulder vertices receive the same cap-boundary adjustment, retaining the intended local drop.

The independent cap classifier originally compared double-precision contour metadata directly with float32 Blender vertices and misclassified one boundary sample. It now represents the metadata contour in the same float32 coordinate format before classification. The original membership tolerance, normal cosine gate, positive-dot gate and projected-area tolerance remain unchanged.

## Independent exported QA

`validate_hybrid.py` independently reads the JSON, checks geometry/normal/UV invariants, then compares cap normals to recomputed area-weighted geometry normals and noncap normals to flat face normals. Full results are in `export-qa.json`.

| Check | Result |
|---|---:|
| Closed bodies | 493 |
| Triangles / exported vertices | 104,872 /161,710 |
| Bed triangles | 36,032 |
| Positive / nonpositive face-normal dot | 104,872 /0 |
| Degenerate triangles | 0 |
| Minimum triangle area | 0.00000006211 m² |
| Finite attributes, valid indices, matching lengths | pass |
| Unit normal range | 0.999999831–1.000000164 |
| Body welded boundary / overfull edges | 0 /0 |
| Body signed volumes | all positive,0.00328–0.31216 m³ |
| Maximum projected-top/footprint area error | 0.0000006206 m² |
| Projected area tolerance | 0.00001 m², unchanged |
| Minimum cap area-weighted-normal cosine | 0.999999824 |
| Minimum hard-side flat-normal cosine | 0.999999857 |
| Normal cosine acceptance gate | >0.999999, unchanged |
| XZ bounds difference from preserved coverage | <0.000000001 m |
| Recorded original source hashes preserved | pass |

Front area is406.9231 m². Complete stone top surfaces including arrises project to278.0027 m²,68.32%. Flat inner caps project to232.5254 m²,57.14%. Those are sums of projected body areas, not a polygon-union or rendered visibility measurement. The bed is an intentionally open surface with818 welded outside/mask boundary edges. Aggregate unwelded boundary counts include normal-split vertex copies and do not represent body holes.

## Artifacts and reproduction

- `build_hybrid_v14.py`: canonical deterministic Blender builder; `source_seeds.json`: preserved92 source-photo guides.
- `paving-v14.blend`: authored geometry, source materials, custom cap normals and preserved V13 comparison geometry.
- `hybrid-metadata.json`: part ranges, source/UV/plane contracts, conditioning details and source hashes.
- `validate_hybrid.py`, `export-qa.json`: independent validation and frozen mesh hash.
- `render_previews.py`: sets the matched cameras/materials and renders only when the exported mesh hash matches passed QA.
- `previews/before-v13-neutral-native-ground.png`, `after-v14-neutral-native-ground.png`, `after-v14-textured-native-ground.png`, plus their three `close` counterparts.

Reproduction sequence is canonical builder with `-- --geometry-only`, independent validator, then Blender opening the saved blend with `render_previews.py`. Coordinate the6-thread build/render slot with root first. The geometry-only blend does not promise a ready-framed default camera; the preview script sets the comparison cameras explicitly. `prepare_sources.py` is initial scaffolding, not the canonical rebuild command after subsequent conditioning/QA refinements.
