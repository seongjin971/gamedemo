# Candidate47 diagnostic, not judge-ready

Opened actual full/orbit/zoom/slice and standalone static capture directly,
against the original concept. Coherent PavingV13 bodies make individual stones
read across the floor, a substantial change from the shallow cracked sheet and
the isolated24 slabs. However, many small rounded raised pads, outlined rims,
some cap fan shading and weak fine wet grain remain. Pools still contain broad
pale shading and lack convincing distinct margins. The new tree and masonry
changes are retained; lower stair bands and root contact gaps remain visible.
There is no new independent score. Latest remains candidate41,6.0/Tier2.

PavingV13 uses866 closed photographed stone bodies,141,312 triangles and323,235
split-normal vertices. Source scan period9.2x4.6m is an art scale. Projected top
surface coverage66.93% includes the bevels; flat cap-only coverage52.56%.
These geometry measures are not visual acceptance. Source hash:
`dd46aefd74c0470bfea77fee2d22df8c72a1d2d47a75d18e7e6944c0c8f87e3c`.

## Shadow comparison and natural frame loop

The exact local caster geometry retains306,324 and191,780 triangles from two
light-intersecting source batches totaling3,269,735 triangles. The same scene
was reopened with original full casters. First diagnostic accidentally set
ShadowsOnly proxies to Off, making them visible; it is invalid and preserved
under diagnostic-47-full-casters. The corrected diagnostic disables those
renderers and is in diagnostic-47-full-casters-fixed. Its full image was opened
directly: major fire/stair occlusion remains consistent. The four-view numeric
comparison records mean absolute8-bit channel differences0.088–0.146 and
0.165–0.401% pixels with luma difference>5. Animated particles and renderer
ordering are not isolated by this comparison; it is not pixel identity proof.

Three sequential runs used the same player-v47-fixed binary,1536x1024,
FrameTiming disabled, natural frames, no other Unity/Blender or heavy asset
validation, every stage focused, errors0. The log confirms **Direct3D12**;
do not infer the graphics API from shader compilation labels.

| Fire caster condition | Static | Walk | Orbit | Zoom |
| --- | ---: | ---: | ---: | ---: |
| Exact local meshes | 42.705 | 43.196 | 42.202 | 42.614 |
| Original full meshes | 28.520 | 28.732 | 28.511 | 28.643 |
| Fire shadows disabled | 50.424 | 51.162 | 50.455 | 51.046 |

The local geometry reduces cost materially while preserving the major static
shadow relationships, but60FPS remains unmet. Walk contains stopped time after
arrival. These are not desktop-occlusion/present traces or direct mouse input.
Build0errors/0warnings,20.038s. Editor capture0errors/0missing/reflection107;
see capture.json for the exact count. New near-root motion and an alternate
API results are recorded below. The user has authorized direct interaction, but
another live Windows list_apps call still fails with native pipe unavailable.

## Actual motion and alternate API follow-up

Same binary with force-d3d11 confirmed Direct3D11 in the log and measured
45.217/45.470/44.680/45.383FPS, errors0/all-focused, no competing renderer or
heavy validation. The default remains D3D12; the alternate is a diagnostic,
and still fails60. Project graphics API settings were not changed.

Separate default-D3D12 motion recording:396 original frames,20.6064m traveled,
errors0/skips0/all-focused. Stage sampling9.968–11.195Hz. Directly opened
0034,0100,0132,0200,0335,0395: walking/turning, approach to the root boundary,
orbit/zoom/limits are visible. Feet remain outside the new root envelope at the
first stop. **The near-root sequence stopped at its first waypoint**: the A*
grid endpoint differs from the requested point by more than the probe's0.15m
arrival threshold. Thus it does not verify the intended whole-root route.
This exposed a probe sequencing limitation despite errors0. Next probe must
advance on actual route completion and repeat the continuous root approach.

Low/close views expose modular architecture, broad pale pool shading and the
overly numerous outlined pads. Technical pass does not close those visual
gaps. The VFR video uses actual timestamps with no generated intermediate
frames; it is not60FPS footage or direct pointer input evidence.
