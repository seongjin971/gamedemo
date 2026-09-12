# P1 Mixamo retarget source delivery ? prepared-01

Status: SOURCE_RETARGET_READY_FOR_UNITY_VISUAL_REVIEW. Unity and direct user acceptance are separate and are not claimed here.

## Delivered source

- `prepared-01/Adventurer.blend` and `prepared-01/Adventurer.fbx`: existing TravelerRig / TravelerSkin, 24 bones, 37,706 vertices.
- `prepared-01/calibration.json`: source SHA-256 provenance, clip duration, target planted-foot samples, calibration, preservation digest.
- `retarget.py`: reproducible source preparation; `verify.py`: numeric and FBX roundtrip QA; `preview.py`: neutral deformation renderer. Source FBX downloads and original P1 remain preserved.

## Selected clips

| Exported clip | Official Mixamo source | Frames at 30 fps | Use |
| --- | --- | ---: | --- |
| Walk | Walking-Swagger.fbx | 32 | Selected upright stride with relaxed arms |
| WalkAlternative | Unarmed-Walk-Forward.fbx | 42 | Preserved comparison; visibly more crouched |
| Idle | Breathing-Idle.fbx | 299 | Grounded breathing stance |
| Stop | Stop-Walking.fbx | 91 | Non-looping optional stop, relaxed final pose |

Walk native source-scale speed is **1.4826746285 m/s**, measured as median backward velocity of the planted target ankle during its low portion of the cycle. At visual scale 1.8 and motor speed 2.25 m/s, nominal playback is **0.843071x**. Source root travel scaled by target/source leg proportion predicts 1.5788956 m/s; that cross-check is recorded separately. Runtime contact must still be observed because source-only calibration does not prove exact sliding-free feet.

## Retarget method and preservation

Source global rotations are converted to target local poses using limb reference directions from child heads, avoiding the target rig's oversized display tails. Anatomical A-rest to source T-rest correction is applied to limbs, preserving source swing and target bone lengths. Target spine order is mapped Spine02 -> Mixamo Spine, Spine01 -> Spine1, Spine -> Spine2; neck -> Neck. Horizontal Hips drift is removed so translation belongs to the runtime motor. Boot sole grounding preserves foot roll and knee bend; this is not a full IK/contact solver. Closed Walk/WalkAlternative/Idle endpoints are identical; Idle's final 12 frames blend to its first pose. Stop keeps its non-looping ending.

Before/after digest of bind matrices, bone hierarchy, mesh vertices, vertex weights, UVs and material slots is identical: `87ed4ec77495151d9d91889726178fb0496d29f432d3125e13f3ff01ff4d3a42`. No material changes. No Unity runtime files were modified by this source package.

## Verified and remaining limitations

Direct neutral render inspection covered Walk quarter-cycle frames 1/9/17/25, the alternative's 1/11/21/31, Idle frame 1, and Stop frame 91. The chosen walk shows upright posture, opposite arm swing, boot heel/toe roll, and distinct left/right strides; no visible wing arms, collapsed knees, detached limbs, or gross sleeve collapse were seen in those views. The alternative is more crouched and was not selected. Idle has a wider stance than Walk, so stop/blend foot placement still needs runtime review.

Numeric QA scans every keyed frame: chosen Walk knee interior angles 107.735?166.110 degrees, signed ankle separation 0.14488?0.16857m, zero loop endpoint bone-head mismatch, zero endpoint Hips horizontal drift. FBX reimport confirms one 24-bone rig, one 37,706-vertex skin, and four correctly ranged clips. These checks establish structural validity only.

No continuous runtime, turning, wall collision, stop blending, foot-sliding, final in-game scale, performance, or user Play acceptance is claimed by this source QA. These belong to the parent Unity integration. The selected filename includes Swagger and retains some stylistic body sway. Source still poses alone do not establish natural motion at the user's final motor speed.

Evidence: `Migration/Evidence/Expansion/P1-Mixamo/source-qa/Walking-Swagger-{1,9,17,25}.png`, `Idle-1.png`, `Stop-91.png`; `source-numeric-qa.json`; `source-qa/bounds.json`. Comparison image filenames use source names to distinguish them from final exported clip aliases.
