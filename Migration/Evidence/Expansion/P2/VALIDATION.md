# VESPER P2 — playable Windows delivery, 2026-09-09

Launch repository-root **[PLAY_VESPER_P2.cmd](../../../../PLAY_VESPER_P2.cmd)**. [Controls](../../../../PLAY_P2.md). Scene `Assets/Vesper/Scenes/Expansion/VesperP2.unity`, executable `Unity/Vesper/Builds/VesperP2/VesperP2.exe`.

The accepted traveler now walks/runs from the duplicated courtyard through an amber gateway to a small crossing:1.6m incline, short timber bridge, upper landing and blocked masonry. The return gateway restores the courtyard. R resets the current entrance and camera. This is the bounded P2 terrain test space, not P3 landscape acceptance. Current P1 skin, Mixamo clips and stride calibration remain unchanged; no extra Meshy or external image/model generation.

## Implementation and preservation

P2-only motor, camera, input/animation bindings and zone owner. AI Navigation2.0.14 was installed using Unity Package Manager, verified under6000.5.7f1. URP stays17.5.0. A complete NavMesh path and tight same-height surface match are required after the first collision ray hit. Water/wall/rail/blocked ledge hits reject; bridge clicks cannot fall through to a lower surface. Movement height is corrected from the collision surface, with2.25walk/5.4run world-distance limits. Courtyard collision tessellation retains the accepted walkable footprint; existing P1 navigation is used only in the Editor preparation, not runtime.

One scene contains mutually exclusive courtyard/crossing roots and separate NavMesh data. Shared player/camera persist. The fade disables old content, allows reflection resources to be destroyed, enables the next root and assigns its entrance. Lighting/effect owners live under each area root. No disk saves, combat, jumping, swimming, weather framework or streaming.

[Protection audit](protection-audit.json) compares6,634 pre-existing tracked/build files against pre-work SHA256, including all four original builds. Only CHECKPOINT/EXPANSION_PLAN/PLAY_EXPANSION and the two authorized package files may change. [Final P2 build manifest](build-hashes.json). Original launchers, scenes, assets, shaders, runtime, public, root ArtSource and previous evidence remain protected. Main and browser baseline refs remain2413d5d; no remote configured, no push.

## Actual verification

- [Final build](build-report.json): errors0/warnings0, succeeded. Final build03 differs from reviewed02 only in diagnostic coverage/background performance handling.
- [Final actual player report](player-03/motion-report.json): **121 checks passed,0 errors,679frames,0 skipped,all focused**, maximum5.4. Walk/run on flat ground, up/down ramp and bridge, acceleration/arrival/turning, upper obstacle routing, close orbit/zoom, six portal transitions/three round trips, both current-entry resets.
- All six transitions pass one active area, one player/controller, total camera limits, no old-area lights/atmosphere, correct reflection ownership and correct spawn. Water, wall, obstacle top and disconnected high ledge reject. Both downward collision rays and the actual game-camera ray accept the upper bridge correctly.
- [Timestamp-preserving motion video](player-03/motion.mp4), [raw frames/report](player-03/motion-report.json).679images span76.40seconds, about8.87 recorded samples/s; this is capture throughput, not game FPS. Sequence footage is automatic gameplay, not physical mouse/Shift input.
- [Self-review](SELF_REVIEW.md), [independent high-effort review](INDEPENDENT_REVIEW.md). Reviewers opened actual adjacent frames. No demonstrated normal-play blocker found in the bounded P2 candidate. Direct input and final user acceptance are separate.
- Candidate01 failure is retained in player-01: its return destination lay outside the eroded landing NavMesh. Candidate02/03 move the target inside and pass. Initial red character lighting is corrected by applying the existing ambient supplement after initialization; P2 water glare is reduced without shared material edits.

## Performance and limits of comparison

Intel Arc130V8GB,1536×1024,Direct3D12. Measurements were sequential, without another Unity Editor/player, Blender render or video encoder. Encoding started after all measurements stopped. Natural application frame cadence is not display-present FPS. The matching-stage probe takes a screenshot at each stage boundary, following the prior P1 protocol; it does not continuously read back frames. P2's matching diagnostic uses the old camera follow factor; normal P2 retains height follow and stronger horizontal tracking.

| Same stage | Preserved P1 Run FPS | P2 FPS |
|---|---:|---:|
| Static |32.69|33.45|
| Walk |32.81|32.72|
| Orbit |32.66|32.02|
| Zoom |31.60|31.03|

[Comparison and raw references](performance-comparison.json), [baseline](perf-baseline/player-report.json), [P2](perf-p2/player-report.json). Both completed error-free/all-focused. Average difference is-2.0% to+2.3%, not an additional10% average regression. Initial zoom p95 rose35.38→39.78ms (+12.4%); this triggered investigation. A completed all-focused [P2 repeat](perf-repeat-p2/player-report.json) measured32.05–32.56FPS and zoom p9532.44ms, so the tail spike did not reproduce. A reverse-order P1 repeat paused after its orbit capture and was stopped; it produced no complete report. [Explicit repeat limit](perf-repeat-baseline/INCOMPLETE.md). Exact transient scheduling/thermal cause is not established; no claim that an optimization fixed it.

[Normal-camera continuous performance](perf-final-continuous/run-performance.json), error0/exit0: courtyard walk33.23FPS (all focused); run32.80FPS (384/394frames unfocused). Crossing walk59.64/run59.88FPS were entirely unfocused with background execution enabled **only by the opt-in performance probe**. These crossing results are not foreground/monitor60FPS certification. The earlier default-background-pausing continuous attempt produced no result and is [retained as incomplete](perf-p2-continuous/INCOMPLETE.md).

## Important remaining limits

Native Computer Use initialization succeeded but app listing failed with native pipe unavailable/os error2. No repeated permission request or substitute physical-input claim. User's latest “오케이 모션좋다” adopts the P1 motion; it does not mean tools verified Shift/mouse. The P2 launcher is ready for direct play.

The slope uses the retained upright authored gait without per-foot IK. Minor sole mismatch on slopes and accepted stop/reversal foot repositioning remain; fully planted stance is not claimed. Test-course water and geometry are intentionally simple. HUD contrast/water readability are optional independent-review recommendations. Diagnostic-only `-p2ManualQA` retains a courtyard-only reflection lookup and should not be used after crossing; normal launch and delivered automated checks do not use that flag.

Delivery ends at P2. P3/daytime water/rain/snow work is not started.
