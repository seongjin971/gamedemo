# Flat 14 m hero stone bridge

Additive replacement candidate `CW_StoneBridgeHero14m.fbx`, preserving all earlier bridge assets. The deck uses 63 mixed-size staggered flagstones with individually clipped/chipped corners and subtle height variation. Thick bonded parapets have large coping stones and terminal piers. The structural underside is a continuous barrel arch with real open space, radial face voussoirs and fitted spandrel courses.

**Placement contract:** origin at deck center, nominal walking height 0. Source axes are X width, Y length, Z up. FBX is Y-up/-Z-forward with node X = -90 degrees; preserve this imported rotation and apply world yaw/position/scale on a wrapper.

| Dimension | Value |
| --- | --- |
| Deck length / full model length | 14 m |
| Clear walking width | 5.2 m |
| Full masonry width | 6.5 m |
| Exact source bounds | X [-3.25, 3.25], Y [-7, 7], Z [-1.72, 1.34] |
| Highest paving vertex | +0.00772 m |
| Parapet coping top | about 1.02 m |
| End-pier cap top | 1.34 m |
| Triangles | 16,160 |

All wall/decorative structures remain outside the central X ±2.6 m walking corridor. No collider is supplied: retain the parent's smooth continuous deck and parapet blockers. Narrow decorative joints can expose the recessed deck core at -0.032 m; they are not intended as navigation holes or physical steps. All paving stays below the requested +0.015 m maximum.

Each stone uses UV0 inside 0..1. Parent material ST may select the stone quadrant of WorldSurfaceAtlas; this mesh does not preselect that quadrant and uses no tiled metre UV. Slots are `CW_BridgeStone`, `CW_BridgeStoneLight`, `CW_BridgeMortar`. Blender preview nodes select the existing stone quadrant for visual inspection only; no supplied texture was modified.

The generator asserts 40 clear-corridor walking samples and 10 rays through the open arch, plus the triangle budget. `audit_bridge_hero.py` independently reimports the FBX, repeats those geometric checks, records UV bounds/raw root rotation and renders `bridge-side-preview.png`. The main inspection is `bridge-preview.png`. These are asset geometry and Blender preview checks, not Unity navigation/FPS or user acceptance.
