# Abbey rubble V2

Additive assets for the D01 abbey's exposed wall toes and broken opening ends. All old asset versions are preserved. No new external generation or credits were used.

| Asset | Unity width / depth / height, metres | Triangles | Fragments |
|---|---|---:|---:|
| CW_AbbeyRubbleStrip6m | 6 / 1.424175 / 0.55 | 21,115 | 136 |
| CW_AbbeyRubbleMound3m | 3 / 1.952592 / 0.729768 | 19,356 | 124 |

Local pivot is centered horizontally at ground level. Blender source X is width, Y depth, Z up. Raw FBX root rotation is X=-90.000009 degrees, Y=Z=0; preserve it inside the existing world wrapper. Strip source bounds are (-3,-.712087,0) to (3,.712087,.55). Mound source bounds are (-1.5,-.976296,0) to (1.5,.976296,.729768).

Each stone is a closed custom convex polyhedron, cut by 6–9 irregular fracture planes and chamfered along its remaining arrises. Broad offcuts, smaller corner fragments, loose peripheral chips, and overlapping low pockets produce the silhouette. These are decorative overlapping rubble meshes, not a rigid-body simulation. The strip is limited to .55 m height; keep it outside the route's clear walking area.

Exactly two exported material slots:

- **ChapelRubbleStone**: UV0 0..1 per fragment. Bind the existing stone atlas quadrant with parent ST, or full LimestoneSurface with identity ST. Blender previews use the latter. Parent controls runtime stone tint and wetness.
- **ChapelMoss**: UV0 0..1. Bind the dedicated parent moss material. Thin irregular cushions follow selected upward fracture faces near their edges; they do not recolor entire rocks. Moss geometric area is approximately 4% of total stone surface area. The mesh has crisp small contours; no alpha fringe or dedicated photogrammetry moss texture is included.

`generate_abbey_rubble.py` reproduces the source blend and writes only `staged/`. `audit_abbey_rubble.py` reimports staged FBXs, checks explicit triangles, zero degenerates, finite vertices, exact width and maximum strip height, bounds agreement, UV0..1, and FBX root rotations. `rubble-fbx-audit.json` passes both assets. Material `.001` suffixes in the second reimport's audit are Blender in-memory duplicate naming; original exported slots and manifests use the exact two names above.

Previews are `CW_AbbeyRubbleStrip6m-preview.png` and `CW_AbbeyRubbleMound3m-preview.png`. They establish geometry and localized moss coverage under a controlled overcast Blender setup; runtime scene lighting and visual acceptance remain separate. The first tiny round moss-patch experiment was revised before final export.

Only the two FBXs and their two manifests are intended for the new Unity Art/EnvironmentKit/AbbeyRubbleV2 folder. Scripts, renders, logs and the source blend remain outside Unity Assets.
