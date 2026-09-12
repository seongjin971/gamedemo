# VESPER P1 Mixamo — playable delivery, 2026-09-09

**MIXAMO_PLAYABLE_BUILD_READY / DIRECT_INPUT_REVIEW_PENDING**. Run repository-root `PLAY_VESPER_MIXAMO.cmd`. Player: `Unity/Vesper/Builds/VesperMixamo/VesperMixamo.exe`. Separate scene: `Assets/Vesper/Scenes/Expansion/VesperAdventurerMixamo.unity`. Existing P1 and candidate58 launchers, scenes and builds are preserved. No P2 work or additional Meshy request.

## Visible change and source

The same novice adventurer now plays official Mixamo **Walking (Walking With A Swagger)** and **Breathing Idle**, retargeted in Blender onto the existing24-bone Generic skin. Geometry31,113triangles, weights, UVs and material are unchanged. The gait has more upright posture, forward boot extension and restrained opposite arm swing. Independent review found the matched-phase improvement **modest**, with no blocking gross skating, collapsed knees, wing arms or large garment penetration in inspected frames. This is actual Mixamo integration, not a renamed original clip or final user acceptance.

Distance-driven walk calibration is1.4826746285 source units/s,2.668814 at visual scale1.8; nominal playback0.8431 at motor speed2.25. Translation remains owned by the existing motor. Idle/Walk use the existing short blend. Downloaded Stop and Unarmed alternative remain source comparisons and are **not** played. No full foot-lock solver or dedicated start/stop system was added. Source/download details and hashes: [BRIEF](../../../Source/Expansion/P1-Mixamo/BRIEF.md), [SOURCE_QA](SOURCE_QA.md).

## Actual visual and motion evidence

- [Before/after video viewer](COMPARE.html), [Mixamo motion video](player-01/motion/motion.mp4). The HTML can be opened locally; connected Chrome playback of both sources was verified through a temporary localhost server.
- Same-camera static frames: [full](capture-cleanup-01/full.png), [orbit](capture-cleanup-01/orbit.png), [zoom](capture-cleanup-01/zoom.png); original [P1 full](../P1/candidate-03/full.png).
- Actual standalone [motion report](player-01/motion/motion-report.json):1536×1024,643frames,25.41694units, six route arrivals, skipped0/errors0/all-focused. Captures cover idle→walk→stop, direction reversal, tree clearance, orbit, zoom and camera limits. Capture throughput9.87–10.90Hz is **not** game FPS. Variable-timestamp video preserves the recorded cadence.
- [Self-review](candidate-01/SELF_REVIEW.md), [independent review](candidate-01/INDEPENDENT_REVIEW.md). Reviewers opened original frames and adjacent movement samples; neither claims a realtime viewing of every frame or direct player input.
- [Functional report](player-01/functional/functional-report.json):21checks passed, errors0, exit0. Includes destination acceptance/arrival, courtyard clearance, invalid target rejection, mid-walk change, camera bounds and reset handlers. Actual mouse/keyboard input counters remain0; automatic commands are distinct from manual input.

## Performance and build

Windows build succeeded with errors0/warnings0. Motion/functional/performance players exited0. Static capture initially completed its images/report but the old helper exited with native code-1073741819 during shutdown. The separate `VesperMixamoCapture` fork explicitly releases render resources and unloads the scene before exit; [cleanup capture](capture-cleanup-01/capture.json) exited0, shader errors0/missing scripts0/runtime errors0/reflection frames134. Original helper is preserved.

Adjacent isolated natural player frame loops,1536×1024/D3D12/Intel Arc130V8GB, same automatic static/walk/orbit/zoom stages. No Unity Editor, Blender, FFmpeg encoding or other heavy QA overlapped either benchmark.

| Stage | Original P1 FPS | Mixamo FPS |
| --- | ---: | ---: |
| Static |32.25|33.66|
| Walk |32.75|34.05|
| Orbit |32.26|33.56|
| Zoom |32.58|33.64|

[Comparison JSON](performance-comparison.json). No large regression. The small positive difference is run variability, not proof of an optimization. These are application frame cadence measurements, not monitor displayed FPS or CPU/GPU timer measurements. Historical candidate58 43.44–44.09FPS was a different run;60FPS is still unmet.

## Important limits and preservation

Stop visibly draws the trailing foot into the wider idle stance. Modest contact drift remains possible; [same-method toe proxy](contact-comparison.json) does not show improved foot lock (new left median0.20units/s; right had no comparable low-height samples). Joint-height sampling is not exact sole geometry and does not establish severe skating by itself. Inspected frame sequences did not reveal persistent large skating. Motion naturalness and direct click/drag/wheel/R feel remain for user Play review.

Native Windows Computer Use remains unavailable in this session; no repeated permission request or shell input injection was used. The user can play the unrestricted normal launcher.

[Protection audit](protection-audit.json): candidate58 protected176files and delivered P1 build174files all retain their hashes. [New build manifest](player-01/build-hashes.json) records the delivered Mixamo files. Shared runtime/material/shader assets and original scenes are unchanged. All new art/scene/build/evidence is additive. Local Git contains sources, import settings, scene and evidence; build directories remain Git-ignored.
