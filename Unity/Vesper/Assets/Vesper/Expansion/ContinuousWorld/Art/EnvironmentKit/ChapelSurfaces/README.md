# Chapel surface modules

New additive FBXs, source blend, reproducible generator, previews and FBX reimport audit. Original chapel modules, world code, textures and prior builds remain untouched. Blender XYZ is width/length/up in metres. Export uses Y-up/-Z-forward and the same -90 degree X FBX conversion as the existing environment kit; preserve imported roots and place by an outer world wrapper.

| Model | Source dimensions | Triangles | Pivot |
|---|---|---:|---|
| CW_ChapelPaving4m | 4 x 4 m; base -.18, top +.008 | 810 | nominal walking surface center at 0 |
| CW_ChapelBrokenSlateRoof6x8m | 6 x 8 m; bottom -.27, ridge +2.4 | 16,840 | eave / wall-top center at 0 |
| CW_ChapelRubblePile3m | 3 x 2 x .95 m | 792 | ground center at 0 |

Paving uses sixteen broad flagstones with staggered joints, irregular corners, low edge chips and a recessed mortar core. The broad walking surfaces remain between 0 and +.008; use the parent-owned smooth floor collider.

The gabled roof has individual staggered slate tiles, pointed jointed ridge caps, actual continuous pitched boarding, principal rafters, purlins, tie beams and king posts. The positive source-Y short end is torn back by a varying amount, with supporting timbers exposed. Forty-nine vertical ray checks cover the intact roof region X +/-2.8 and Y -3.8..3.0, allowing the parent to use real roof geometry for rain interception. The intentional open/torn end is outside that guaranteed region.

All material UVs are within 0..1. Paving, mortar, rubble and slate use the top-right WorldSurfaceAtlas stone quadrant through parent material ST. `CW_ChapelRoofSlate` / `CW_ChapelRoofSlateLight` should use dark blue-grey tint; the preview intentionally retains visible stone grain. `CW_ChapelRoofTimber` uses the bottom-left bark/wood quadrant through its own material ST. No atlas changes were made.

`generate_chapel_surfaces.py` reuses only the named geometry helper functions from the stable sibling BridgeHero generator via AST extraction; it never executes the earlier bridge build. `audit_chapel_surfaces.py` checks exported counts, triangles, degeneracy, UV range, pivot/bounds and actual walking/rain surface rays. Final visual acceptance and Unity placement remain with the parent scene pass.
