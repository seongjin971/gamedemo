# TreeV11 derivative integration contract

This is a bounded reduction and preview package, not whole-scene adoption or unrestricted orbit acceptance. All 17 downloaded source/metadata files remain byte-identical to `protected-input-hashes.json`. No Meshy calls or Unity edits were made.

## Files

- `derivative/tree-v11-art-directed-mesh.json`: candidate for native scene comparison (depth 1.65, tapered root flare).
- `derivative/tree-v11-base-mesh.json`: normalized reduced baseline without art direction.
- Matching `.blend` files contain the derivative and original textured material.
- `derivative/original-*.png`, `reduced-base-*.png`, `art-directed-*.png`: identical five-camera/light comparison, 1024 square, Cycles 16 samples, AgX. These are local Blender renders using actual source textures, not downloaded thumbnails.
- `build_tree_v11.py`: full reproducible source-to-export build.
- `validate_tree_v11.py`: independent strict native Unity winding/normal/bounds/UV/preservation check. Requires NumPy; it was run with Blender bundled `5.2/python/bin/python.exe` as a standalone Python process.

## Placement and coordinate convention

JSON uses flat positions/normals/uv/colors/indices arrays. Positions are model-local native Unity; geometry conversion from Blender is `(-x,z,-y)` and triangle order reverses exactly once to `[0,2,1]`. Do not apply another handedness conversion. UVs are imported glTF coordinates, unchanged by export. Colors are white RGBA because the source has no vertex color.

Both variants have width 6.3, height span 6.4, minimum Y -0.06 and maximum Y 6.34. The bounding center of the lowest 8% height region is XZ=(0,0). Root-region centering is a defined reproducible measurement, not center of mass. Existing scene parent scale 1.73 yields height span 11.072. Current V10 world height span was 11.34898; its world AABB width was 10.86972 and depth 4.03989. Existing parent position (7.2,0,3.7), yaw -5.73 degrees can stay; root can apply its separately chosen local yaw for actual permitted cameras.

The render labelled FRONT views Blender -Y, which corresponds to native Unity viewer at local +Z looking inward. With existing parent yaw -5.73 degrees, that front-facing direction is world (-0.099833,0,0.995004). BACK is local -Z; Blender LEFT image views native local +X and RIGHT views local -X. Isometric camera Blender (8,-13,8) maps to native local (-8,8,13). Its camera target is native (0,3.05,0). These labels specify source views, not scene compass directions.

Use downloaded `texture-0-base_color.png` as sRGB color and `texture-0-normal.png` as tangent-space normal; normal-map orientation/import is the Unity shader owner's responsibility. Roughness and metallic are separately downloaded maps. The Blender comparison instead uses the equivalent embedded source image nodes. This package does not decide final metal/roughness/shader response.

## Normal handling

Anisotropic normalization and depth/root deformation invalidate unchanged imported split-normal directions. Geometry normals are recomputed after those deformations while UVs and source tangent normal-map detail remain. A small number of folded/sliver triangles whose averaged smooth corner normals point behind their face receive face normals only in JSON. Exact count is reported per variant. This tiny local export sanitation is distinct from flipping triangles; winding remains unchanged. Blender renders show the recomputed smooth surface, with those exceptional per-triangle export normal overrides not rendered separately.

## Acceptance limit

The generated crown remains strongly planar: strict side views collapse the branch hierarchy to a narrow column even after depth expansion. It is actual volumetric sculpted bark geometry rather than a billboard, but depth scaling cannot invent missing radial limbs. It is suitable to compare in the permitted VESPER camera range with a chosen front-facing yaw; unrestricted 360-degree hero-tree acceptance is not supported. Native captures and movement review are still required.
