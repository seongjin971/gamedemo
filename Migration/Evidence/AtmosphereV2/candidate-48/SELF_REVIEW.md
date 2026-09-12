# Candidate48 — larger slabs, contacts, cape and exact shadow tiles

Actual Unity full/orbit/zoom (1536×1024) and slice (1037×739), plus the planar reflection image, were directly opened. The original concept and candidate47 full were opened alongside this iteration. This is a working diagnostic, not a new independent verdict or final adoption. Latest independent score remains candidate41: 6.0/10, Tier2.

PavingV14 replaces866 bodies with493 larger photo-aligned bodies,104,872 triangles. The same photographic source, preserved UV relationships and 12.4×6.2m art scale carry across its height and maps. The cap fan shading seen in47 is reduced; bigger rectangular faces read more clearly in all four native views. Rounded small stones and strong perimeter lines remain. Local floor albedo multiplier changed .62→.78, and paired Rock05 roughness now gives fine variation instead of a constant wet smoothness. Whole-frame exposure is unchanged. Native fine grain and wet glints remain too weak against the concept; this is not a completed material pass.

ContactV14 removes exactly50 identified loose offcuts, verifies49 retained identities, then adds26 fragments in four clusters and four small mineral contact bodies. Their heights use the final PavingV14 source, and the tree placement/navigation boundary stay fixed. The quieter distribution is useful but does not make the remaining block shapes fully convincing.

KnightV7 is integrated in the original hierarchy/materials, preserving the six other source records and V6 helmet. Native views show deeper unequal cape folds and an uneven hem. The result is art-directed cloth deformation, not a successful physical equilibrium simulation. Armor remains simplified; dynamic motion has not yet been rechecked on48.

The existing exact local fire shadow geometry is divided into2m XYZ chunks, assigning every triangle once and retaining its exact world positions, normals and winding. Actual mesh bounds include crossing edges.492,370 triangles across167 enabled chunks replace the two combined renderers; those combined renderers remain disabled for the same-player `-vesperUnpartitionedFireCasters` diagnostic. This may improve cube-face culling but performance and shadow equivalence are not yet proven by the initial capture.

Initial native technical capture: shader errors0, runtime/capture errors0, missing scripts0, reflection updates109, root hull25 points. Technical success does not establish the visual goal.

Blocking: pale irregular water regions still resemble cloudy patches, fire reflections are weak/flat, stair risers retain warm/cool banding, and the upper architecture is too dark and regular. Tree branch junctions remain broad. The reflection image contains actual flame imagery, so missing reflected fire is not simply a missing flame renderer. Reflection coordinates, local coverage and surface response require diagnosis.

Self-review decision: not judge-ready. Preserve useful asset improvements; diagnose reflections and finish materials before submitting a prepared candidate to a fresh judge. Clean FPS and the corrected multi-waypoint root approach recording are pending.

## Completed player follow-up

Player48 built in112.711s with0 errors/0 warnings. Same binary, D3D12,1536×1024, no FrameTiming collection, other Unity/Blender renders or heavy QA:

| Condition | Static | Walk | Orbit | Zoom |
| --- | ---: | ---: | ---: | ---: |
| Exact spatial chunks |47.813|48.899|48.275|48.862|
| Exact combined casters |47.327|47.801|47.187|47.789|

Both runs had0 errors/all frames focused. The paired difference is only0.486–1.099FPS, not the entire47→48 gain. Geometry/material changes and run variation prevent attributing that earlier gain to chunking.60FPS remains unmet. These are natural application frame intervals, not a display-present or occlusion trace. Walk includes time after arriving.

The separate motion pass contains390 JPEG95 frames,33.471m,9.657–10.773Hz by stage,0 skipped/0 errors/all focused. The corrected route-completion check records arrivals at all three near-root targets, then repeats the first two. Actual frames0090/0103/0113 were directly opened at the three arrivals, and0204/0324/0389 at orbit/wide/close limits. No foot/root crossing was visible in those inspected frames; all near-root frame positions also stayed within navigation validity. This establishes the automated route, not direct pointer input. Low views still expose simplified armor/architecture. The motion video uses actual timestamps without interpolation.

The old `reflection.png` is captured with the slice camera, not the full camera. Its flame pixels demonstrate reflection rendering but cannot certify full-camera UV correspondence. The next capture helper saves a separate reflection image for every view. Windows native pipe remains unavailable after the user's renewed authorization.
