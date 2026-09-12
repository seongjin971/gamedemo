# ContinuousWorld EnvironmentKit

Additive environment assets authored locally in Blender 5.2.1 for the continuous map. No web assets, paid services, Unity scene edits, shared material edits, or manually authored `.meta` files are used by this package.

`generate_environment_kit.py` reproduces the source blend, 11 FBX models, bounds/material manifest and Blender contact render. Run with the installed Blender executable using `--background --threads 6 --python <script>`. `audit_environment_kit.py` checks finite vertices and UVs, zero-area triangles and FBX roundtrip mesh/triangle counts. It writes `.dream-loop/continuous-world/assets/mesh-audit.json`.

Meshes use metres. Source Blender coordinates are Z-up; FBX export is Y-up, -Z-forward. Placement in Unity must retain the importer conversion so a model's vertical axis remains Unity Y. Tree/rock origins are at their ground center with a small buried skirt. Full source bounds are in `manifest.json`.

## Placement and materials

- `CW_StoneFootbridge_Flat12m`: flat deck local Y = 0 in Unity, 12 m deck along Z, 5.2 m clear width, outer masonry bounds about 6.49 m wide and 12.52 m long. Place at world Y = 0.8 for the agreed deck elevation. End masonry extends below deck by about 1.76 m. No collider is included; use the world's continuous walking collider and wall blockers. Deck stone joints are visual only.
- `CW_StoneFootbridge`: optional 10 m arched-deck version. Unity deck Y = `0.8 * (1 - (Z/5)^2)` for -5 <= Z <= 5. Do not substitute without matching navigation height.
- `CW_LayeredRock_A`, `CW_LayeredRock_B`, `CW_CliffLedge`, `CW_RiverBoulder`: carved continuous rocks with broad fracture planes, localized erosion and ledges. Names remain stable from the first kit export, but uniform stacked ring geometry was replaced after visual review.
- `CW_Reeds`, `CW_RiverGrass`: curved creased blade geometry, with separate cattail seed heads on reeds. No alpha texture is needed. Use double-sided blade materials.
- `CW_RiverBirch`: tapering branched trunk, bark lenticels, open canopy of individually folded leaves. Use double-sided leaf materials.
- `CW_AlpineFir`: serrated needle sprays, woody boughs and a separate `CW_AlpineFir_SnowCaps` mesh. Hide that mesh for lower-elevation firs. Use double-sided needle materials; snow can remain opaque.
- `CW_StoneWaymarker`: weathered hewn direction marker, pointer along local X, about 2.65 m above its ground origin.

Material slots use stable `CW_` names. Blender materials provide a neutral rough surface preview with nodes; those node graphs are not an exported Unity shader. Assign the expansion's stone/bark atlas, snow and vegetation materials after import. Suggested mapping: `CW_Rock`, `CW_RockLight`, `CW_Crevice`, `CW_Stone`, `CW_StoneDark` -> stone; `CW_Bark`, `CW_Birch` -> bark; `CW_Snow` -> snow; the remaining green/brown slots -> opaque vegetation. All meshes have UV0. Geometry is explicitly triangulated and degenerate faces removed before export so Unity need not tessellate weathered n-gons.

## Evidence and limits

The v3 numeric audit passes every model, including FBX roundtrip. The contact image is `.dream-loop/continuous-world/assets/environment-kit-contact.png`. v1 and v2 contact renders are preserved next to it to record the structural correction. This is Blender asset evidence, not Unity lighting/material quality, navigation, FPS, or user visual acceptance. The fir is the highest-cost asset at approximately 24k triangles; reduce distant tree density or supply an LOD if measured world cost requires it.
