# Structural bridge V3

This is the later explicitly requested structural variant, added beside the earlier read-only V2 diagnosis in this folder. The prior diagnosis, images, scripts, old assets and builds are preserved. It does not revise the earlier finding: V2's Boolean did not close the arch. V3 deliberately widens the valid arch to improve its silhouette.

**CW_StoneBridgeHeroV3_14m**: 14 m length, 6.5 m exterior width, 5.2 m clear walking width, deck pivot at height zero. Arch clear span is 12.8 m, crown -.18 m, spring -3 m. Full-width bank abutments occupy only the outer .6 m at each end. Source bounds: (-3.25,-7,-3.02) to (3.25,7,1.34). 15,985 explicit triangles, zero degenerates.

All 7,488 source triangles touching or extending above deck zero are **bit-identical float32 geometry** to V2; the SHA256 signatures match. This preserves the entire visible paving, parapets, copings and terminal piers. The same seeded V2 generator is reused with bounded below-deck parameters. The recessed continuous deck core underside is raised from -.22 to -.16, entirely below deck, to prevent it from occluding the newly requested -.18 crown. Arch rings, vault and spandrels remain continuous and open; no Unity physics changes are included.

Use the existing outer wrapper and preserve imported FBX root X=-90 degrees. Blender source X=width, Y=length, Z=up in metres. Parent's negative-local-up-only scaling by 1.5 and world deck height2.8 can remain. Walking maximum is+.007892 m; 40 walking rays pass.

Materials remain **CW_BridgeStone**, **CW_BridgeStoneLight**, **CW_BridgeMortar**. UV0 remains within0..1 per stone; parent stone-atlas ST stays compatible. Paving size/count/UV generation remains exactly V2 (42 mixed-size slabs).

Evidence:

- `structural-fbx-audit.json`: bit-exact upper geometry signature, FBX root, UV, finite bounds, zero degenerates and reimport agreement. All606 interior rays at six heights (-.35,-.6,-1,-1.5,-2,-2.6) clear; all48 exterior rays remain opaque; all40 walking rays pass.
- `structural-v2-raised-camera-preview.png` and `structural-v3-raised-camera-preview.png`: identical camera angle.60/elevation.62, ortho8.2, deck2.8, negative vertices×1.5, water-.95 and river bed-4. The same neutral bright water and daylight reveal the wider curved opening. Source camera X sign follows the previously verified Unity FBX handedness.
- `structural-camera-comparison.json`: exact camera and projected near-facade quadrilateral.
- `structural-opening-visibility.json`: geometry-alpha camera visibility, including occlusion by the complete bridge, inside the identical near-facade region above water. Open pixels increase35,553→52,201 (**+46.8%**); open portion of that region37.61%→55.22%. This measures a visible silhouette improvement, not just analytic ellipse size or horizontal clear rays. Boundary antialiasing adds small pixel uncertainty.

The paired images visibly show narrower piers and a longer continuous curved opening. This is a controlled asset comparison; it does not establish a new independent Unity water-gate score or full-scene acceptance.

`prepare_structural_v3.py` derives the additive generator from untouched V2 with asserted exact text substitutions. `generate_structural_v3.py` writes `staged/CW_StoneBridgeHeroV3_14m.fbx`, `staged/manifest.json`, the source blend and `structural-manifest.json`. `audit_structural_v3.py`, `render_structural_comparison.py` and `measure_structural_opening.py` reproduce the evidence. Only the staged FBX and manifest are intended for the new Art/EnvironmentKit/BridgeHeroV3 directory. No external spending was used.
