# P1 Run source delivery ? prepared-01

Status: SOURCE_RETARGET_READY_FOR_UNITY_VISUAL_REVIEW. Source-only preparation and review are complete; continuous runtime and user acceptance remain separate.

## Delivery

- `Migration/Source/Expansion/P1-Run/prepared-01/Adventurer.blend` and `Adventurer.fbx`: same TravelerRig and TravelerSkin, 24 bones, 37,706 vertices; Idle, Walk, Run actions.
- `prepared-01/calibration.json`: source hashes, native pacing, flight/ground offset, phase alignment, retained action hashes and bind/skin digest.
- `retarget.py`, `verify.py`, `contact_qa.py`, `preview.py`: reproducible preparation and checks. Source filenames and existing P1-Mixamo remain preserved. Unused Stop and WalkAlternative omitted only in this derivative.
- Official authenticated Mixamo source: Running With Intention (`Running-With-Intention.fbx`); FBX Binary, With Skin, 30 fps, no keyframe reduction; In Place false, Mirror false, Overdrive 50, arm space 50. No additional remote calls were made by this source preparation.

## Runtime calibration

| Value | Result |
| --- | ---: |
| Walk native speed (unchanged) | 1.4826746285 m/s |
| Walk duration (unchanged) | 1.0333333333 s |
| Run native speed | 3.8366997242 m/s |
| Run duration | 0.7 s (22 frames, 30 fps) |
| Run native stride per cycle | 2.6856898069 m |
| Run phase offset | 0.975 |
| Run playback at scale 1.8 / motor 4.5 | 0.6516016837x |
| Walk playback at scale 1.8 / motor 2.25 | 0.8430710123x |

Apply `RunPhase = Repeat(WalkPhase + 0.975, 1)`. Signed left-versus-right ankle swing correlation is 0.993587 across 200 normalized samples. Run retains the same support side at shared phase; frame 1 has right support, around frame 11 has left support.

Run native speed uses median backward ankle velocity during actual boot-sole contact intervals: both interval endpoints below 0.025 m; 9 qualifying samples. The earlier walk-style low-ankle heuristic includes airborne recovery in running and underestimates speed, so it is not used. Source root travel scaled by leg proportion predicts 4.1991671 m/s, 9.45% above the selected contact estimate; ankle motion includes foot roll, so exact sliding-free motion is not claimed. The source at original cadence would cover about 6.9061 scene m/s at scale 1.8. Requested 4.5 scene m/s therefore gives a gentler jog cadence (about 1.074 s/cycle); retain the requested motor setting for continuous runtime review before deciding any pace change.

## Grounding and preservation

One constant vertical offset of -0.0628739385 m grounds the entire Run cycle while retaining source hip vertical motion. No frame-by-frame sole snapping, no IK, and no Humanoid remapping are used. Horizontal source root travel is removed. Boot sole clearance is 0.0080000265 to 0.0994911939 m for the lower of the two boots. Both soles exceed 3 cm during frames 3?7 and 14?18, retaining two natural flight phases. No sole crosses the ground plane at keyed frames.

Bind matrices, hierarchy, mesh vertices, weights, UVs and material slots before/after share digest `87ed4ec77495151d9d91889726178fb0496d29f432d3125e13f3ff01ff4d3a42`. Idle and Walk keyframe coordinates, handles and interpolation hashes match exactly. Material changes: none. Existing P1-Mixamo source files were not changed. Only P1-Run source/evidence paths were written by this package.

## QA and limits

Direct neutral render inspection of Run frames 1, 6, 12 and 17 shows a slight forward running lean, opposing arm swing, distinct alternate support, heel/toe roll and airborne phases. No gross torso/sleeve collapse, detached limbs, knee inversion or ground penetration is visible in these four views. Rendering is source QA, not final game visual acceptance.

All 22 keyed Run frames have finite evaluated mesh coordinates. Knee interior angles span 66.057?163.177 degrees; signed ankle lateral separation remains positive (0.107139?0.156659 m). Loop endpoint bone-head mismatch and horizontal hip drift are both zero. Maximum hand/foot step is 0.158238 m per 1/30-second source frame. FBX roundtrip confirms one 24-bone rig, one 37,706-vertex mesh, and Idle 1?299 / Walk 1?32 / Run 1?22.

Evidence: `source-qa/Run-1.png`, `Run-6.png`, `Run-12.png`, `Run-17.png`; `source-numeric-qa.json`; `run-contact-qa.json`; `source-hashes.json`. No continuous transitions, turning, collision, actual runtime foot sliding, performance, or final user acceptance are asserted. No Unity or runtime code was modified by this source package.
