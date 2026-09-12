# TreeV16 integration contract

Final source geometry is stable. Native visual adoption remains a separate integration check. This package does not write Unity files.

## Meshes and transforms

All JSON arrays are flat, numeric arrays: `positions`/`normals` are XYZ triples; `uv` is UV pairs; `colors` is RGBA quadruples; `indices` contains zero-based triangle triples. Read indices exactly as delivered. All normals are supplied; do not apply another coordinate reflection, winding reversal, recentering, height normalization or automatic smoothing.

| File | Coordinate space | Vertices | Triangles | Transform |
|---|---|---:|---:|---|
| tree-v16-mesh.json | Native Unity model local, meters | 136927 | 157999 | Existing parent position (7.2,0,3.7), scale (1.73,1.73,1.73), quaternion (0,-0.0499791693,0,0.9987502604); retain mesh-local yaw -20 degrees |
| tree-v16-covers.json | Native Unity world, meters | 216 | 72 | Identity |
| tree-v16-soil.json | Native Unity world, meters | 216 | 72 | Identity |

Combined tree yaw is -25.7295779513 degrees. Main tree local width remains 6.3m and maximum Y 6.34m. Its minimum Y is now -0.78408855m because geometry descends under the floor; this hidden underside must not drive scaling. Main source conversion is (-BlenderX, BlenderZ, -BlenderY), winding reversed once. Cover source conversion is (BlenderX, BlenderZ, -BlenderY), winding retained. These are already baked into the respective JSON arrays.

Tree material, original photo UVs, broad placement, and upper crown above local Y4.9 are preserved. Reuse the current tree material. Cover UVs follow the existing world XZ/Rock05 convention; stone vertex color is (0.79,0.81,0.82,1), soil (0.19,0.145,0.105,1). Parent owns shader assignment and native material evaluation.

Each supplemental JSON has `name` and `id` matching its filename stem. The main tree uses the existing five-array schema with no added metadata. `covers-report.json` lists six exact part names and index ranges. Each stone or soil part has 72 indices/24 triangles. There are three stone covers and three earth pieces, no new parapet cover. Their vertex positions already include world placement.

## Integrity

| File | SHA256 |
|---|---|
| tree-v16-mesh.json | c2a16a66af7845927b48cef2c1ed37199a47a6d14e0ba7151e17dffe466e5121 |
| tree-v16-covers.json | 1c5ca68388f7c10455713da6f1b2e2d5dda3be0aa071534a2374cb4ec687f907 |
| tree-v16-soil.json | 6199c456367d7357f429a6208ba819739610ec1aaeb22d72341b5a04e0c0ad95 |
| tree-v16.blend | 8a26e3cb4edcfbfb72e8dc23ffe5d544fd116bde1df472b444a6ed33778d6f16 |
| tree-v16-covers.blend | dad70cacb92a40ff7513d4eeaa615827c461f61be4ae9639fdbc358eaaf21629 |

Independent final-array QA is in export-qa.json: finite values, valid indices, nonzero triangles, unit normals, strictly positive face/mean-normal dots, exact source triangle UV order, unchanged protected inputs. Minimum tree face/mean-normal alignment is 0.00039818; positive, with a small angular margin on the most extreme source faces. The export has 131 local face-normal fallback cases, so exported vertex count can differ without a topology/UV change.

## Root support and navigation

All four central terminal corridors descend from the last25% of their existing centerlines and reach full descent at90%. Three floor roots narrow earlier; the fourth turns inward and retracts toward the existing parapet. No further radial root extension occurs. Exact support tests use actual Paving15 triangles, with retained parapet support where floor is absent. The remote Paving16 foreground edit leaves this region unchanged.

The measured 546 exposed terminal source vertices (181/143/52/170 across roots1–4) all have support and are at least45mm beneath the corresponding support surface. Test selection is the central1.08-radian corridor, radius90% of the centerline end through end+0.18local, and original local height(-0.03,0.85). This is not an exhaustive watertight ground-intersection proof for every bark triangle or a guarantee that all roots are invisible. Broad attached buttresses intentionally remain visible. `build-report.json` records per-root actual terminal bounds, support values, and sink amounts; `minimumSupportMinus45mmWorldY` is a descriptive minimum, not a universal horizontal cap.

`root-navigation-evidence.json` contains the ordered30-point native-local XZ convex hull at local height[-0.005,0.7], exact mesh hash, and requested0.28m world character clearance. Recompute the installed native navigation geometry with actual parent+mesh transforms and audit covers too. Do not derive a blocker from the whole crown AABB or reuse the earlier V12 hull without comparison. A near-root walking phase is still required.

Existing Contact14 is unchanged. Possible overlapping retained object names are `Root soil contact 1`, `Root soil contact 2`, `Root soil contact 3`; `Parapet moss contact 4` is also retained. No removal is required or requested by this source package. Review for double soil ledges in native context before deciding any exact removal. The new pieces are `TreeV16 root N broken slab cover` and `TreeV16 root N entry earth` for N1–3.

## Preview limits

Matched source context contains actual complete Paving15, Contact14 rubble/deposits and nearby parapet. It omits portal, stair architecture, knight, sky, Unity shader and lighting stack. Roughness0.85/tint0.8 are equal preview-only settings. First-pass geometry evidence is preserved under retained-first-pass. The initial context images under retained-mirrored-context have a horizontal camera handedness error; their before/after comparison remains useful, but they are not exact native projections. Corrected context images are reviewed separately in SELF_REVIEW.md. Native full/zoom/glare and walking review remain the final integration gate.
