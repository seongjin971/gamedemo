# V8 structural tree candidate

Reviewed the requested concept, actual Unity `round-15-pools/full.png`, and
the independent `verdict-unity-2.md` before editing. Opened both final matched
1024x1024 Blender images (`tree-v7-same-light.png`, `tree-v8-preview.png`) and
inspected the final root-tip-preserving candidate directly.

## Changed geometry

- The major wood, existing exposed roots, and 13 additional root buttress
  collars are voxel-unioned at 0.015 Blender units, faired for 22 passes, and
  reduced from 258,056 remesh triangles to approximately 35,000 major triangles.
  The root beginnings now flow up the lower trunk instead of appearing as
  individual cylinders terminating against a stump. Distal root geometry
  (1,318 original vertices) is retained to maintain the spread and fine tips.
- Seven broad proportional sculpt regions and the new continuous surface soften
  the largest upper direction changes. The change is visibly broader than V7's
  small centerline adjustment, especially around the central upper trunk and
  right-hand forks. The existing overall zigzag design remains recognizable.
- Eight substantial offshoots are replaced by 19-ring curved, continuously
  tapering limbs. Each splits into a second 12-ring curved branch. The far-right
  horizontal end, upper center, and inner right offshoots now visibly bend and
  divide; this is replacement topology rather than a color adjustment.
- Source bark UVs are reprojected on the joined wood, with short staggered UV
  changes to interrupt long parallel ridges. New twigs use longitudinal bark UVs.
  The preserved embedded bark textures and material are reused.

## Technical result

Final: **51,654 triangles, 29,222 exported vertices**. Relative to V7's 44,402
triangles this is +7,252 (+16.33%); below the requested approximate 80k ceiling.
Export vertices share exact position/normal/UV tuples, preserving seam splits.
JSON positions and normals convert Blender `(x,y,z)` to Unity `(-x,z,-y)`;
triangle winding is reversed `[0,2,1]`. `export-qa.json` records finite values,
valid indices, normalized normals, source hash preservation, and counts.

All modifications are confined to this new `tree-v8` folder. V7 and original
ArtSource remain preserved. The final Blender process exited after saving the
asset and both previews. Its shutdown reported three unfreed memory blocks
(0.018711 MB); no Python traceback occurred and export assertions passed.

## Limits and integration gate

This is a prepared structural candidate for native Unity comparison. The
continuous root flare and curved replacements are visible in the controlled
Blender evidence, but the full native frame must establish whether their
screen-space size clears the judge's directive. The branch spread and bark
remain those of the current design; some retained very fine twigs still have
straight segments, and a few original tiny splinter shapes remain. The texture
is still visibly directional in parts of the trunk. V8 is not proof of >=8
visual quality, native motion quality, acceptable FPS, or user adoption.

Build entry: `build_tree_v8.py`. Deliverables: `tree-v8.blend`,
`tree-v8-mesh.json`, `tree-v8-report.json`, and the two matched PNGs. Earlier
incomplete log files document an inefficient normal-read loop; the final script
caches normals before adjusting positions and completes the same operation
without repeated whole-mesh normal recomputation.
