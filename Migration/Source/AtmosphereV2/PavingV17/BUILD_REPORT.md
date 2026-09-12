# PavingV17 — 28 selected fractured paving units

This bounded source package adds 18 large photographed stone units to the ten preserved PavingV16 units. It does not replace the whole courtyard method. Unity integration, material changes and native acceptance belong to root; no Unity files or original maps were edited here.

## Change and preservation

Final new IDs: **19,20,21,22,29,31,32,38,40,41,42,103,104,110,111,255,264,343**. Original V16 IDs **96,97,105,106,107,112,131,134,144,146** remain exact, including their ten existing fill objects. **No new fill objects** are added in V17. Drainage body 280 and all other retained bodies preserve their original referenced attributes and triangle index lists exactly.

Additional source outlines cover 22.34896 square metres. Their combined selection bounds are X[-6.091016,2.100977], Z[1.253320,9.172852]. This targets the foreground, both sides of the knight and the central approach. TreeV16/Contact14 protection is X[4.5,9.05], Z[1.2,6.4], beyond all selected outlines. The previously verified drainage slab around X[.070,1.035], Z[.595,1.138] is outside the new selection.

Every selected unit uses its actual original Tiles130 polygon corners without the earlier contour averaging. `trace_graph.json` specifies one or two connected plane cuts in source pixel coordinates, independent main-plane tilt and one selected chamfered edge. The selective chamfer is 29mm for these dominant slabs; it does not run around the whole perimeter. Plane cuts follow photographed boundary shoulder/notch landmarks, while their internal continuation and vertical angles are explicit authored lithic interpretation, not measured scan fracture depth. The resulting connected bodies retain continuous UV across the cuts.

World period remains 12.4×6.2m, which is 5.3913× the nominal 2.3×1.15m source area. Each instance uses an integer tile translation derived from its preserved source placement. Every new vertex satisfies `u=worldX/12.4`, `v=worldZ/6.2`; geometry and original color registration are kept together. No recoloring, map alteration, random texture offset or shader tuning is included.

## Export contract

- `paving-v17-mesh.json`: native Unity world identity; flat numeric `positions`, `normals`, `uv`, `colors`, `indices` arrays. Read the supplied triangle order directly; do not reverse winding, recenter, renormalize bounds or recalculate normals.
- **100,842 triangles**, down from V16's 104,058; **165,944 vertices**, including the exact preserved old prefix. Unused old vertices from replaced units intentionally remain to avoid changing other indices.
- Colors remain white on new records. Remaining colors are copied exactly.
- Whole XYZ bounds are unchanged: min[-8.936228752,-.126000002,-11.101970673], max[9.040660858,.010417859,21.067903519]. Stair void, ground extent, navigation Y0 and independent water plane are preserved.
- Mesh SHA256: `64ff97f22ef1995723ce5a8883f6f41610354b93ab112911eec169f00cc23b44`.
- Preserved V16 source SHA256: `f812feed57a6b6e2fa3c7378caada08243c650883b5e1f33d630640dd828b7b6`.

`fracture-metadata.json` contains each replacement record, original source contour ID, integer tile shift, cut endpoints, final offset/main tilt, part index ranges and global bounds.

## Independent gates

`validate_fracture_graph.py` reads serialized arrays independently of Blender. Final double and emulated native float32 triangle checks both find zero nonpositive face/vertex-normal dots and zero degenerate triangles. All 18 new bodies have exact float32 welded edge incidence two, opposing directed edges, positive volume and projected cap area matching their raw source polygon within 1e-5 square metres. No new/neighbor outline overlaps or preserved-fill overlaps remain in float32 tests.

All old vertex attributes preserve an exact prefix; all nonselected part triangle lists are exact. V16 replacement/fill parts and drainage 280 are explicitly checked for retention. Unit-normal maximum error is 1.70e-7 and new UV registration maximum error is 5.76e-8. Finite values, index ranges, strides, white new colors, total triangle budget, absence of new fills and unchanged whole bounds pass.

An initial candidate included body94. A stronger preserved-fill check found that its expanded raw outline overlapped existing `V16_joint_fill_96_0`. The original fill was preserved and body94 was replaced in the selection by central body264. The rejected mesh, blend, traces, metadata, failed QA and build log are retained under `rejected-preserved-fill-overlap/`; rejected hash `ccf1d4044810e05a9f77ebfaaf6d94a7b03af98ff8a48f616f90267479f4ed79`. No threshold was relaxed.

## Reproduction and preview contract

1. Launch Blender with preserved `PavingV16/paving-v16.blend` and execute `build_fracture_graph.py` with three threads.
2. Run system Python `validate_fracture_graph.py`; require `passed=true` and the matching mesh hash.
3. Launch the resulting `paving-v17.blend` and execute `render_previews.py` with three threads. It produces six matched full/patch views at 1536×1024: textured full before/after, neutral patch before/after, textured patch before/after.

The source bridge remains `(nativeX,-nativeZ,nativeY)`. V16's older rotation-only preview camera mirrored native screen handedness. V17 corrects the **render context only** by reflecting its complete X axis and rebuilding a proper Blender camera; the export and saved source blend are not reflected. `preview-projection-qa.json` compares four landmark projections against native screen-right/up formulas and requires error below2e-6. The landmarks are mathematical projection tests; the previews contain the actual whole ground and original texture material, not the portal, tree, knight, water, native lighting or root's revised mineral layer. This distinction limits what source previews establish.

## Visual review status

Candidate55 full/orbit/zoom and the concept were opened before authoring. The existing ten angular units were locally useful, but rounded caps remained dominant, particularly across the middle approach and around the knight. The concept has a larger proportion of naturally squared boundaries and broken planes than that native candidate.

Final source preview review is recorded separately below after direct image inspection. Native56 must assess the new plane response and boundary distribution under actual moon/fire/water conditions. The remaining majority of floor bodies retain the older rounded-cap construction; this package must not be described as whole-floor reference completion or an achieved target score.

All six final images were directly opened. In neutral patch view, several large central and right-hand units now have pointed/stepped corners and selective side breaks rather than a uniformly rounded shoulder. The connected main planes change their edge heights without noisy fan triangulation. Existing V16 ten units and their infill remain unchanged. The textured patch retains photographed boundary alignment, and no new fill plates or displaced texture seams are apparent.

The textured full view shows a modest broader distribution of angular stones, not a wholesale visual transformation. Diffuse preview lighting still makes many cap interiors look flat; some new long edges remain clean and their side walls can read as a raised rim. Most unselected smaller rounded bodies remain plainly visible. These limitations are significant relative to the concept. Native lighting may make the connected plane changes clearer, but that effect has not been verified here. Do not describe the six source renders as proof of native quality or a whole-floor material match.

The final preview batch completed in2m13s and released the render slot. Source geometry is stable for parent-owned native comparison. PowerShell reports a nonzero native-command status from Blender's deprecation warnings on stderr; both build/render completion markers and `Blender quit` were reached, all six PNGs exist, and the independent export/projection gates pass. The warnings are retained in the logs.
