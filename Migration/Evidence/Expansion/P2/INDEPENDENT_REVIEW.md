# P2 candidate02 independent review — 2026-09-09

Reviewer: separate read-only agent `/root/p2_review`; same model as main requested, high effort explicitly requested. Agent independence is available; the review session does not expose an independently verifiable internal effort setting. The reviewer did not implement or edit the candidate.

**Final verdict: READY for the bounded P2 delivery, with the evidence limits below.** The build03 and performance closeout addenda supersede the initial pending items. No normal-play blocker or persistent material performance regression was demonstrated. This is not user acceptance, native-input certification, a new courtyard score, or P3 landscape approval.

The current BRIEF authorizes a compact ramp/bridge/obstacle test and three courtyard round trips while preserving the accepted courtyard and current P1 running character. I inspected the raw candidate images and relevant source before reading the implementer's self-review. The retained P1 image is `../P1-Run/candidate-02/full.png`. Candidate `player-02/0000.jpg` preserves its courtyard composition, masonry, tree, cool atmosphere and warm fire/reflections while adding the crossing marker. `0240.jpg` and `0670.jpg` show the courtyard restored after returns. The crossing is visibly a simple geometric test course; completing a detailed landscape is outside this review.

I opened uphill walk `0108–0110`, uphill run `0292–0294`, downhill run `0190–0192`, downhill walk `0383–0385` and `0390–0398`, plus upper orbit/zoom `0166`. The sequences show changing gait and translation across the deck/ramp at both paces, upright body posture and usable player framing. No demonstrated severe foot sliding, body collapse, obstacle penetration or wrong-level bridge movement was found. Flat authored feet on a slope remain an approximation; these images do not establish fully planted soles or continuous real-time smoothness. Fade samples `0069–0072` show the old area disappear into black and the crossing appear; `0223–0224` show the return fade.

Direct code review covered P2Motor, P2World, P2RunInput, P2Camera, P2Animation, P2Probe, P2Performance, P2ContinuousPerformance, P2Build and P2Revise. The first collision must be designated walkable, pass the normal/height checks and produce a complete NavMesh path. Movement corrects the voxel height to the same nearby collision level; bridge geometry is 1.6 m above the lower landing. Content roots own their surfaces/lights. Switching disables the old root before enabling the next, waits a frame for reflection destruction, resets the current entrance and camera, and blocks movement through the fade. The unchanged reflection OnDisable releases its texture, destroys its camera and clears its global availability. Git status shows P2 additions and the navigation package changes, with no tracked P1 source/scene modification.

`player-02/motion-report.json` contains 673 actual standalone frames, 103 passed checks, no errors and no skipped captures. I read the probe implementation as well as the results: automated routes and collision rays cover three round trips, bridge height, camera-projected bridge clicks, rejected water/walls/obstacle top/disconnected ledge, current-entrance reset and single-area/player/gameplay-camera/reflection ownership. This supports the recorded routes and rejection cases, not arbitrary native mouse input.

**Must fix:** none demonstrated for normal P2 play in the reviewed candidate.

**Recommended:**

1. Increase the small HUD/control text contrast or add a subtle backing; the lower instruction line is difficult to read over some dark/busy surfaces (`0000`, `0166`). This does not block using the accompanying controls document.
2. If the test course later receives a visual pass, make the dark water rectangle more immediately recognizable as water (`0108`, `0166`). Do not turn this into a P3 landscape task.
3. Diagnostic only: make `P2Performance.Save()` tolerate no active planar reflection. Its current unconditional component dereference can throw after entering the crossing in opt-in manual QA. Normal play and the supplied courtyard-only performance run do not call that path.

**Optional:** none requiring another visual candidate. Do not reopen the accepted skin, gait or courtyard to chase a different art preference.

**Evidence limits and pending closeout:**

- I inspected ordered raw stills and code, not continuous real-time playback or physical Shift/mouse input. Native tool connectivity was reported unavailable; this review does not certify physical input feel.
- The initial camera-matched comparison reports P2 average FPS within approximately -2.0% to +2.3% of adjacent P1 stages. Zoom p95 increased from 35.38 to 39.78 ms in that pair and is awaiting the main agent's reverse-order investigation. No isolated crossing continuous-performance report was available at this initial review.
- Initial ownership checks count the reflection component and the active content roots, supported by visual samples and cleanup code. Expanded light/effect/total-camera runtime assertions are pending the final diagnostic run; do not claim those assertions passed yet.
- A reported stalled continuous-performance attempt produced no completed report and is not a pass. Image capture cadence and frame-loop telemetry are distinct from monitor presentation and physical input.
- Final build, lifecycle and performance evidence will be reviewed in an addendum. The reviewer launches no heavy process while those isolated measurements run.

## Final diagnostic build03 addendum

The final `build-report.json` reports success, 0 errors and 0 warnings. `player-03/motion-report.json` contains 679 frames, 121 passed checks, 0 errors, 0 skipped images and all frames focused. I checked the added P2Probe assertions directly: after each of the six portal transitions, active lights equal the active area's child lights, active atmosphere ownership is 1 in the courtyard / 0 in the crossing, and camera counts allow only the gameplay camera plus the courtyard reflection camera. All six instances of each assertion passed. This resolves the pending expanded lifecycle evidence for the recorded three round trips.

I also opened final raw frames `player-03/0000.jpg`, `0299.jpg`, `0488.jpg`, `0584.jpg`, and `0676.jpg`. They show the retained initial courtyard, ramp running, third crossing entry, upper camera view and final courtyard reset without a new visible regression. No visual redesign or normal-play behavior change was submitted for this diagnostic build.

`perf-final-continuous/run-performance.json` completed with no errors. Foreground courtyard walking measured 33.23 FPS / 31.98 ms p95 over 399 frames, all focused. Courtyard running measured 32.80 FPS / 32.63 ms p95 but 384 of 394 frames were unfocused. Crossing walk/run measured 59.64 / 59.88 FPS with approximately 16.8 ms p95, entirely unfocused under opt-in background QA. Recorded travel and peak speeds show these were moving routes. The crossing numbers are background frame-loop evidence, not a claim of foreground or displayed 60 FPS. Normal play is not configured by the opt-in diagnostic flag.

The manual-QA reflection lookup recommendation remains unresolved and explicitly diagnostic-only. There is no normal launcher impact. The reverse-order paired camera performance closeout is still pending this addendum; the repeat P2 half already completed error-free and fully focused, including zoom p95 32.44 ms.

## Performance closeout and final disposition

I read the completed `perf-repeat-p2/player-report.json`, updated `performance-comparison.json`, and `perf-repeat-baseline/INCOMPLETE.md`. The reverse baseline run stalled and has no final report; its partial screenshots yield no FPS conclusion. The reverse-order pair is therefore incomplete. The original adjacent matched-camera baseline/P2 reports remain complete and fully focused. Their average stage rates differ by approximately -2.0% to +2.3%.

The repeat P2 run is complete, error-free and fully focused, with stage averages 32.05–32.56 FPS and zoom p95 32.44 ms. The initial P2 zoom p95 of 39.78 ms was not reproduced. This supports treating the first tail increase as an unconfirmed transient observation, not a demonstrated persistent regression; it does not establish its exact cause or prove an optimization fixed it. No claim of foreground crossing 60 FPS follows from the background-only continuous run.

The expanded lifecycle evidence is resolved; the bounded visual/functional judgment remains READY; there are no demonstrated normal-play must-fix findings. The missing reverse baseline, unavailable physical input, noncontinuous visual inspection, background performance conditions and diagnostic manual-QA null lookup remain disclosed limitations. These do not justify expanding P2 into another art/optimization phase. Provide the runnable P2 build for the user's direct play acceptance, keeping that acceptance separate from this independent review.
