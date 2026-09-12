# Continuous World independent snow covers

These additive meshes fit the existing normalized rock geometry exactly. The source rocks, textures, normals, FBXs, and previous builds were not modified. `generate_snow_cover.py` reproduces the rock covers. `audit_snow_cover.py` reimports the exported files and checks explicit triangles, zero degenerate triangles, finite vertices, UV range, original model hash, and original source alignment.

## Placement and material

Instantiate each cover and its named base rock under identical outer world transforms. Preserve each imported FBX root's -90 degree X conversion. Do not parent a cover beneath an already converted mesh node, and do not reposition a cover to its own bounds center. Source coordinates are Blender Z-up; Unity uses the same original model conversion. All covers use `CW_SettledSnow`, UV0 within 0..1. Parent material scale/offset should select WorldSurfaceAtlas's bottom-right snow quadrant (for example scale .492,.492; offset .504,.004). The shader/material remains parent-owned.

| Cover | Original pair | Triangles | LOD1 |
|---|---|---:|---:|
| CW_HF_Limestone_SnowCover | CW_HF_Limestone | 17,334 | 8,666 |
| CW_LayeredRock_A_SnowCover | CW_LayeredRock_A | 12,530 | 6,264 |
| CW_CardedAlpineFir_SnowCover | CW_CardedAlpineFir | 10,134 | 4,991 |

Preferred close hero: limestone plus its cover. The rounded cap volume follows exposed, upward-facing shelves and leaves the fractured vertical stone visible. Nominal thickness is .16 m for the limestone and .12 m for the smaller handmade rock. Exact bounds and pairing hashes are in the per-model manifests. LOD0 reimport bounds error is under 0.000001 m; all four rock-cover FBXs pass with zero degenerate triangles. Keep distant repeated instances on LOD1.

The `*-pair.blend` files include the original base read-only-derived object for inspecting alignment; FBX exports contain only the new cover. `*-preview.png` shows the final cover on its matching source rock. `rejected-v1-*.png` retains the rejected miter-spike attempt for evidence, and is not the delivered geometry.

The optional fir cover comes from `generate_fir_snow.py`: 33 actual curved branch sprays receive small, rounded snow pockets only where the supplied needle texture has opaque alpha. This preserves an open canopy and avoids continuous horizontal snow plates. Pair with the carded fir, using identical world transform and no added offset. LOD1 is preferred for repeated trees. Final audit passes all six exports with zero degenerate triangles and unchanged original-model hashes. The fir remains a card-based tree; these pockets do not replace final scene shading and distance checks.
