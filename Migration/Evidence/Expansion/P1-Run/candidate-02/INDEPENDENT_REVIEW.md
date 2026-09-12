# P1 Run — independent movement review, 2026-09-09

Verdict: **READY FOR USER MOVEMENT REVIEW — no major visual blocker found in the inspected evidence.** The new gait reads as running and is clearly distinguishable from the retained walking. This is a bounded movement verdict, with no courtyard score or microdetail iteration target.

I read SELF_REVIEW.md, then personally opened the actual images with view_image. The self-review's claims were treated as questions to check, not as visual proof. No Unity, Blender, encoding, build, or performance workload was launched for this review.

Evidence personally inspected:

- candidate-02/full.png, orbit.png, zoom.png; prior P1-Mixamo/capture-cleanup-01/zoom.png.
- player-02/motion/0039–0043.jpg: consecutive full-run samples.
- 0084, 0088–0090, 0096: running to walking, including consecutive transition frames.
- 0136, 0140, 0143–0145, 0148: approach and stop settling.
- 0184, 0188, 0192–0194, 0198: reversal and subsequent settling.
- 0248, 0252, 0255–0257, 0260, 0264: closer route beside the tree root.
- 0360–0361 and 0410–0411: adjacent orbit and zoom samples.
- Prior P1-Mixamo/player-01/motion/0040–0041.jpg walking samples; P1-Run/source-qa/Run-6.png and Run-17.png as larger supporting deformation views.
- player-02/motion/motion-report.json, including stages, speed, runBlend, phase, root and toe positions for the inspected sequences.

The running sequence has a longer forward/back stride, visibly bent swinging arms, and rear-leg recovery with flight intervals. Root travel is visible across adjacent courtyard paving landmarks. It does not look like the same relaxed walk merely transported faster. The source views show intact knees, sleeves, tunic, belt and cape silhouette at the two inspected phases; actual player frames do not show gross body collapse, wing arms, separated equipment or large cloth penetration. The character is relatively small in the full view, so this does not certify every concealed surface or phase.

The running-to-walking samples visibly reduce the arm/leg action. Matching telemetry changes from runBlend about 0.84 at 0088 through 0.55/0.25 at 0089/0090 to 0 at 0096, where speed is about 2.25. Full-run samples 0040–0042 reach about 5.4 with runBlend 1. These numbers support identification of the observed states; they do not independently establish gait naturalness.

The stop sequence reaches an upright idle instead of continuing to run in place. At 0144–0148 the reported root and phase remain fixed while the feet settle toward idle. That settlement is a real residual: the left toe moves horizontally about 0.20 world units and the right about 0.22 between 0144 and 0148 with the root stationary. These are bone proxy positions, not measured sole contacts, but they confirm that the stop is not foot-locked. The reversal also reads as a quick turn followed by gait/idle blending, rather than a fully authored planted pivot. Minor foot slide and stop/turn polish should therefore remain disclosed.

The closer root-route samples retain a coherent body silhouette. Raised feet at 0255/0256 belong to progressing running phases, followed by a lower foot at 0257; these selected images do not establish persistent hovering. Tree shadow and dark boots make precise floor contact harder to judge. No gross skating failure is apparent in the inspected adjacent sequences, but slip-free stance throughout the full run is not proven.

The static and camera samples preserve the established scene and character presentation without an obvious new framing or material regression. Orbit/zoom samples here show an idle character; they establish camera presentation only, not running from every angle.

This was inspection of selected actual stills and adjacent captured frames, not continuous real-time playback or direct keyboard/mouse play. The capture report describes automatic commands, and automatic Shift requests are not physical Shift-key verification. No FPS conclusion is made here. Continuous movement feel, direct-input acceptance, and final visual adoption remain the user's review; isolated functional/performance results must be reported separately.
