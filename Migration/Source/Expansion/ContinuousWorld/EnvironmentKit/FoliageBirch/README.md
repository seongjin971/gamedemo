# Carded river birch

`CW_CardedRiverBirch.fbx` and `CW_CardedRiverBirch_LOD1.fbx` use a curving forked white-bark skeleton, brown outer twigs and curved radial leaf cards. The cards follow the supplied atlas's diagonal twig direction. Height is 7.2 m and maximum crown width is 4.8 m, with a ground-center pivot. LOD1 preserves branch placement and removes secondary crossed cards.

**Unity transforms:** preserve imported model-node X = -90 degree axis conversion. Apply placement/yaw/scale to an outer wrapper. Source coordinates are Blender Z-up; Unity uses Y-up.

**Material bindings:**

- `CW_BirchLeaves`: supplied `Art/Textures/BirchBranches.png`. Full map, no ST/quadrant remap: UVs already select the four quadrants. Preview uses opaque alpha clip at 0.4, Cull Off. The atlas original is unmodified and its hash is in each manifest.
- `CW_WhiteBirchBark`: **dedicated** `Art/EnvironmentKit/FoliageBirch/BirchBark.png`, UV0 0..1, no ST remap. Do not bind the brown WorldSurfaceAtlas bark quadrant to this slot.
- `CW_BirchTwigs`: opaque rough dark brown (linear preview color 0.16, 0.13, 0.10), no texture required.

The bark is a new 1024-square Higgsfield Nano Banana Pro output, job `f37da558-07d4-4b9d-832c-94ab5c605428`, cost 2 credits confirmed in account transactions. Its complete prompt and provider result URL are retained in `bark-job.json`. This brings this agent's generated-asset spending to 72 credits: 70 for the earlier 3D trials plus 2 for bark. No credentials are stored. The bark and source branch atlas were visually inspected before binding.

`generate_foliage_birch.py` is reproducible and preserves supplied textures. `birch-preview.png` is Blender asset evidence only; scene quality, performance and user acceptance remain separate. Import the supplied foliage normals when practical; they follow canopy volume rather than each flat card.
