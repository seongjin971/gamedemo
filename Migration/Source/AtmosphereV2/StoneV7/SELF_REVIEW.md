# Stone v7 bounded Blender review

Reviewed `.dream-loop/concept.png`, `round-19-authored-water/full.png`, and both 1500x1500 Blender geometry renders directly.

The foreground's repeated long parallel ridges are not present in the neutral v6 geometry render. This is strong evidence that directional material/normal detail contributes most of that visual defect. Geometry exports alone cannot honestly claim to remove that pattern in Unity.

V7 edits the existing v6 sculpt, including its carved fissures, irregular perimeter and masonry corner losses. One linear topology subdivision supplies local brush resolution without replacing the mesh with primitives. Top support-plane relief is compressed by 70%, with sparse shallow pits and short angular edge losses; it does not introduce full-face random chunky noise. Three unequal loss supports cover 9.25% of the normalized slab perimeter. Brush depths are 0.012–0.036 local units, with additional masonry corner losses up to 0.044. Centimetre interpretation assumes a one-metre instance; actual instance scaling remains unchanged.

In the same-camera before/after renders the slab planes are quieter, while fissures remain readable and localized edge losses vary the contour. The masonry retains a recognizably quarried bulk, but its subdued clay render still reads as a relatively simple fractured block; image-based stone materials and in-scene light will decide whether this meets the visual target. This is a moderate geometric improvement, not evidence of a whole-frame quality gate pass.

All ten existing UUIDs, exact local bounding boxes, and Blender object matrices are retained. The JSON basis and winding match v6: position/normal `(x,y,z) -> (-x,z,-y)`, triangle indices reversed `(0,2,1)`, no object matrices baked. Total unique triangles: 25,554 (v6: 7,024); runtime instance cost and FPS need review by the integrating agent. All meshes are closed after welding their split normal seams, with finite data and valid indices.

Only this new `.dream-loop/unity-atmosphere-v2/stone-v7` directory was written. Existing ArtSource, public model and all v6 source files were hash-checked before/after and preserved. No Unity assets, instance transforms, runtime shaders, Git commits, or prior evidence were changed by this subtask.

The PowerShell process reports exit code 1 due to Blender's Python `Material.use_nodes` deprecation warning on stderr. `build.log` shows both renders saved, the blend saved, `STONE_V7_COMPLETE`, and normal `Blender quit`; mesh QA supplies the substantive completion evidence.

## Runtime derivative

The integrating agent requested a maximum 30% increase over v6 after the initial sculpt master was delivered. Use the ten UUID JSON files in `runtime/`, not the higher-detail JSON files beside this review. The separate `runtime/stone-v7-runtime.blend` contains 8,770 triangles, a 24.86% increase over v6. `build_runtime.py` preserves the master, welds only coincident normal seams, cleans subprecision fissure geometry, triangulates and decimates, restores exact local AABBs, and regenerates sharp fissure normals. Its direct process completed normally.

Direct review of `runtime/before-master.png` and `runtime/after-runtime.png` confirms retained slab contours, support planes and fissures. Some clay masonry highlights become slightly more faceted, which is expected from the reduced geometry. No gross silhouette regression is visible. The runtime render remains suitable for in-scene evaluation, with material and performance judgment owned by the integrating agent.

`runtime/runtime-qa.json` and `runtime/export-qa.json` verify all ten original UUIDs, exact AABBs (zero error), unchanged matrices, closed meshes after seam welding, unit normals, consistent winding, zero opposed geometric normals and zero subprecision export triangles. The high-detail master and all protected source hashes remain unchanged. Normal QA identified a few tiny inherited fissure triangles and smoothed corner normal disagreements in the high-detail master; the runtime derivative cleans those and is the intended delivery.
