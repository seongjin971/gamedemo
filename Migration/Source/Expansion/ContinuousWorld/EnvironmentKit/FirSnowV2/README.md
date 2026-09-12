# Fir snow V2

New cap-only derivatives for the unchanged carded alpine fir. Original tree, needle atlas, snow covers and builds are preserved. No external generation or credits used.

| Model | Paired tree | Triangles | Supported sprays | Visible snow, inspection view | Visible snow, default Unity angle |
|---|---|---:|---:|---:|---:|
| CW_CardedAlpineFir_SnowCoverV2 | CW_CardedAlpineFir | 13,759 | 132 | 31.47% | 31.03% |
| CW_CardedAlpineFir_SnowCoverV2_LOD1 | CW_CardedAlpineFir_LOD1 | 6,973 | 105 | 30.74% | 30.08% |

The default-angle measurement uses angle .46 radians, elevation .72 radians, tree wrapper yaw zero. These are projected white-snow pixels divided by visible snow-plus-tree pixels from a flat emission mask, with needle alpha respected. They verify the requested 25–35% coverage for two controlled views, not every yaw or an independent Unity visual score. Original V1 projected coverage was not measured; its generator selected only 33 sprays.

V1's strict four-solid-alpha-corner filter, narrow center strip, random selection of less than half the primary sprays, 4 cm lift, and aggressive decimation left sparse pockets obscured by rolled secondary needle cards. V2 samples both existing upper-facing primary and retained secondary sprays, closes only tiny single-grid alpha gaps, and keeps intermittent snow ridges following actual branch-card curvature. Snow is raised 7.5–11.5 cm above supporting cards and given 7.2 cm settling thickness before rounding. No whole-tree cone, snowball stacks or continuous horizontal tier plates were added. Original green needle geometry remains unchanged; airy needle-tip refinement is outside this cap-only change.

Use each cap at **exactly the same outer wrapper position, quaternion and scale as its paired tree**. Original source pivot and units are retained; no placement offset should be added. Both raw FBX roots are X=-90.000009 degrees, Y=Z=0; preserve that transform independently under the wrapper. Do not parent the cap under an already converted tree mesh root.

Source bounds (Blender X width, Y depth, Z up, metres):

- Full: (-1.872488,-1.884883,.728697) to (2.103649,1.983643,8.383290).
- LOD1: (-1.872488,-1.884883,.803830) to (2.103649,1.983643,8.388243).

One material slot, **CW_SettledSnow**, UV0 0..1. Bind the existing snow atlas quadrant using parent ST, or full SnowSurface with identity ST. The `_LOD1.fbx` file intentionally contains the internal node `CW_CardedAlpineFir_SnowCoverV2_Reduced` to avoid Unity's orphaned LOD naming warning.

`generate_fir_snow_v2.py` reproduces both caps and the unchanged paired tree previews, exporting only `staged/`. `FirSnowV2-pairs.blend` keeps both original trees and their paired caps. `audit_fir_snow_v2.py` and `fir-snow-fbx-audit.json` confirm explicit triangles, zero degenerates, finite bounds, UV0..1, reimport bounds agreement and root conversion. `measure_coverage.py`, `render_actual_angle.py` and `coverage-audit.json` document the masks and verify both paired original FBX hashes remain unchanged.

Final previews: `fir-v2-paired-preview.png`, `fir-v2-lod1-paired-preview.png`. They use controlled Blender overcast lighting; parent owns Unity material binding, placement, scene capture and acceptance. Only the two FBXs and two manifests belong in the new Art/EnvironmentKit/FirSnowV2 folder; source scripts, blends, images and evidence remain outside Unity Assets.
