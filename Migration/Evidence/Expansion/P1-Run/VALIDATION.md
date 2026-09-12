# VESPER P1 — Mixamo running follow-up, 2026-09-09

**P1_RUN_PLAYABLE_BUILD_READY / DIRECT_INPUT_REVIEW_PENDING**. New normal player: repository-root **PLAY_VESPER_RUN.cmd**, `Unity/Vesper/Builds/VesperRun/VesperRun.exe`. Scene: `Assets/Vesper/Scenes/Expansion/VesperAdventurerRun.unity`. Hold either Shift while moving to run; release to return to walking. Shift alone does not create a destination. Click/drag/wheel/R are preserved.

## Implemented behavior and source

Official Mixamo Running (Running With Intention) is retargeted onto the same24-bone skin. Existing Mixamo Idle/Walk actions, geometry31,113triangles, weights, UVs, bind matrices and material are preserved. Run has bent-arm swing, longer alternating strides and natural flight intervals. Contact offset is constant so airborne frames are not flattened onto the ground. [Source and provenance](../../../Source/Expansion/P1-Run/BRIEF.md), [source QA](SOURCE_QA.md).

Walking speed2.25; running5.4scene units/s (2.4x); acceleration5.5/7.5. Actual speed blends walk/run, traveled distance advances a shared cycle, and Run phase offset0.975 aligns support sides. Authored Run speed6.90606 at display scale1.8 yields0.781922x playback at full speed. Braking and sharp turns reduce the gait toward walking. Dedicated planted start/stop/turn clips, foot IK, stamina and combat are not added.

All runtime changes are new P1Run components attached only to the new scene. The existing motor/camera/navigation and shared visual assets are unchanged. The prior Mixamo walking build and older P1/candidate58 builds are preserved; P2 maps remain unstarted. No new Meshy or Higgsfield generation.

## Verification

- Windows build: errors0/warnings0, [build report](candidate-02/build-report.json).
- Static full/orbit/zoom: [full](candidate-02/full.png), [orbit](candidate-02/orbit.png), [zoom](candidate-02/zoom.png). Editor capture exit0, shader errors0/missing scripts0/runtime errors0/reflection frames107. Same camera as [prior Mixamo walk](../P1-Mixamo/capture-cleanup-01/full.png).
- Actual standalone [motion report](player-02/motion/motion-report.json):1536×1024,469frames,41.02643units excluding reset teleport, peak5.4,23checks passed, errors0/skipped0/all-focused, exit0. Covers walk→run, run→walk, stop, reversal, tree clearance, orbit/zoom and reset. Capture throughput9.41–10.08Hz is separate from application FPS. [Motion video](player-02/motion/motion.mp4) preserves recorded timestamps.
- Existing [functional probe](player-02/functional/functional-report.json):21checks passed/errors0/exit0 for route acceptance/arrival/clearance, rejection, mid-route changes, camera limits and reset.
- [Self-review](candidate-02/SELF_REVIEW.md) opens actual source and game frames before independent review. Neither selected frames nor automatic checks are final user input acceptance.
- [Fresh independent review](candidate-02/INDEPENDENT_REVIEW.md): running is clearly distinct from walking; no major visual blocker in35+ inspected actual static/adjacent frames. Stops still move toe proxies about0.20/0.22units toward idle; this is not a foot-locked stop. Camera orbit/zoom samples show idle presentation, not running from every angle. No claim of full realtime video viewing.
- First short-route probe failed three cruise expectations because acceleration/braking occupied the3.36-unit route. Candidate02 uses a longer already-valid courtyard path and passes. [Original failed report explanation](player-01/motion/QA_ROUTE_NOTE.md). Only QA route changed, not runtime motion or speed.

## Remaining limits

Stopping and reversing still reposition the feet through a short blend; perfect planted contacts are not claimed. Slight contact drift may remain. The character's original skin/materials are retained, including existing small deformation limits. Native Windows direct input tools are unavailable, so automated `SetRunning` requests are not physical Shift key tests. User Play review is still needed for keyboard feel and subjective motion naturalness.

## Isolated performance and preservation

1536×1024/D3D12/Intel Arc130V8GB. No Unity Editor, Blender, other player, Mixamo WebGL preview or video encoding overlapped these measurements. [Comparison JSON](performance-comparison.json).

| Same automatic stage | Previous Mixamo walking build FPS | New running build FPS |
| --- | ---: | ---: |
| Static |37.17|34.73|
| Walk |37.75|35.26|
| Orbit |37.12|34.77|
| Zoom |36.86|34.87|

New build measures5.4–6.6% below the preceding walking build in these adjacent runs, below the10% large-regression threshold. Do not call this identical performance or infer an exact cause from a single pair. Within the new build, separate continuous-route12-second stages measured walk33.96FPS/23.28units and run33.99FPS/40.06units, peak speeds2.25/5.4, errors0/all-focused/exit0. These are natural application frame cadence, not hardware display FPS;60FPS remains unmet. Historical43.44–44.09FPS is not the current adjacent baseline.

Video encoding ran only after all performance measurements completed. The469-frame video preserves capture timestamps; video throughput is not application FPS.

[Protection audit](protection-audit.json): candidate58176files, original P1 build174files and preceding Mixamo walking build173files all retain their hashes. [New build manifest](player-02/build-hashes.json). Git diff confirms original scenes, shared runtime/material/shader/settings, old launchers and previous evidence are unchanged. New sources/scene/components/evidence and latest status/play instructions are committed locally; build folders remain Git-ignored. No remote push or P2 implementation.
