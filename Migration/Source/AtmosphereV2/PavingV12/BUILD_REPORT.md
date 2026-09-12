# Paving V12 source delivery

Status: source geometry and Blender comparison complete; native Unity appearance and water integration pending. No Unity files were changed by this package. Paving V10 and V11 meshes, original maps and previous evidence remain preserved. The separately authorized V11 BUILD_REPORT text corrections now state 4.0 art scale and 20.723 mm minimum water clearance.

## Delivered geometry

The continuous V11 surface now has 24 separately closed stone bodies across the foreground, with independent planes, broad unequal fractured arrises and a recessed continuous stone/soil bed underneath. Eight manually identified source-photo slabs contribute three instances each. AO darkness and height gradients refine bounded contour guides; this is not automatic semantic segmentation. One third of bodies shrink 16–18% on one axis, with their source texture attached through the inverse transform.

The bed retains the source's 40 mm art displacement amplitude at a nominal 145 mm sampling interval. Hero cap planes have bounded 2.8 mm residual scan detail after removing each source island's fitted base plane. Their perimeter descends 21–30 mm and uses approximately 65–105 mm unequal bevel widths. These vertical dimensions and the 4x source scale are art direction, not photogrammetric metric claims. Fine surface detail also comes from the actual 4K NormalGL map in the textured preview (strength 0.4); geometry does not resolve every map pixel.

Original source: ambientCG Tiles130, CC0, photographed area 2.3 × 1.15 m. Maps are read directly from `../PavingV11/maps`; the effective repeat remains 9.2 × 4.6 m. Original map bytes were verified unchanged by the independent validator. See V11's manifest and research package for the official asset, license and download evidence.

## Unity import contract

- File: `paving-v12-mesh.json`; id `paving-v12-hybrid-scan-slabs`.
- `alreadyUnity: true`; identity transform. Flat `positions` and `normals` arrays have stride 3, `uv` stride 2, `colors` stride 4; colors are neutral RGBA (1,1,1,1). `indices` contains triangle vertex indices.
- Do not mirror coordinates or reverse triangle order. The native contract is positive cross(edge1,edge2) dot supplied normals, matching the working source convention.
- Use exported UVs for all source maps. Bed UV is world XZ / (9.2,4.6). Each hero uses `((worldXZ-center)/scale+center)/(9.2,4.6)`; metadata records its center and scale. Replacing this with shader world UV would misalign source grain and geometry on shrunken stones.
- Keep the existing ground-only replacement scope. Stairs and the upper landing are not included. The existing row-segment/rear void footprint remains; the front ground still extends under the lowest stair nose as it did before. Do not fill the whole rectangular AABB with an extra plane.
- Existing coverage bounds are preserved: X [-8.936228752, 9.040660858], Z [-11.101970673, 21.067903519] m. Y now spans [-0.115000002, 0.009885650] m.
- Independent water reference remains Y = -0.004. Ten bodies have some vertices above this level; fourteen are wholly below it. Bed Y is [-0.063600004,-0.024868827]. This classification is not a rendered water-coverage or pool-connectivity result.
- Root owns native material brightness, specular response and water. No glare compensation is baked into vertex colors or the original Color map.

## Independent geometric verification

`validate_hybrid.py` reads the exported JSON independently of Blender. Final results are in `export-qa.json`.

| Check | Final result |
|---|---:|
| Vertices / triangles | 49,398 / 78,926 |
| Positive / negative face-normal dot | 78,926 / 0 |
| Degenerate triangles | 0 |
| Minimum triangle area | 0.0000013017 m² |
| Finite attributes, valid indices, matching lengths | pass |
| Normal length range | 0.999999865–1.000000113 |
| Closed hero bodies | 24 / 24 |
| Hero position-welded boundary / overfull edges | 0 / 0 |
| Hero signed closed volumes | all positive, 0.06302–0.17958 m³ |
| Bed triangles | 64,256 |
| Bed position-welded boundary / overfull edges | 1,068 / 0 |
| Maximum source-UV contract error | 0.0000002282 |
| XZ bounds difference from preserved coverage | < 0.000000001 m |
| Recorded source hashes preserved | pass |

The bed is an intentionally open surface with outer/masked boundary edges. The aggregate unwelded boundary count in the JSON QA includes duplicated vertices at normal seams; it is not a physical-hole count. Closure is tested separately after position welding for each body. Positive volume and face-normal agreement supplement that topology check.

Final mesh SHA256: `4f8088145c1a8a065563a1f55f9e30ad00e8f9be93e1cebeaa5af7aea850346f`.

The first cap tessellation failed independent QA (311 negative dots and 46 degenerate triangles). Its source/export/previews are preserved under `rejected-cap-tessellation` and are not import candidates. The final cap uses explicit nested rings and fans instead of subdividing a long skinny polygon triangulation. This corrected topology passed the tests above; the failure was not hidden by reversing individual triangles.

## Direct preview review and limits

The final neutral and textured full/close images were opened directly. Compared with V11 under the same Blender camera and lighting, the 24 selected units now have visible independent boundaries and stepped edge silhouettes. The actual source color and grain follow the same fractured outlines. Close views show broad cap planes and arrises rather than a uniform displaced sheet.

The neutral full view also shows the bounded nature of the change: only selected foreground bodies have strong independent relief, so some read as isolated raised panels. The remaining bed is continuous. The textured image retains source course repetition and fine photographed cracks; this package does not claim to remove those or to achieve the concept in native Unity. Raw source color remains warm and bright under the neutral preview lights. Water and the scene's actual reflective lighting are absent.

Files named `native-ground` use the native camera angle/elevation/scale as a Blender diagnostic. Before and after use exactly the same preview camera, but the Blender/Unity projection convention can horizontally mirror the diagnostic relative to native capture. Metadata `screen_center` is a Blender diagnostic coordinate, not a certified Unity pixel coordinate. Final lower-frame visibility and the requested 20–30 readable boundaries require root's actual native capture.

Comparison images: `previews/before-v11-neutral-native-ground.png`, `previews/after-v12-neutral-native-ground.png`, `previews/after-v12-textured-native-ground.png`, and their three `close` counterparts. Blender source is `paving-v12.blend`; deterministic source script is `build_hybrid_v12.py`, seed input is `source_seeds.json`. A new build should be run only after coordinating the Blender/performance slot.
