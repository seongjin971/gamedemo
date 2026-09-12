# W10 independent controls review

Verdict: **PASS within the controls-only scope.** No blocking defect was found in the reviewed input implementation or supplied Unity-player evidence. Physical keyboard/mouse acceptance and the user's final play review remain separate.

Reviewed 2026-09-12 KST by an independent reviewer. Read the installed Dream Loop skill and `references/pro-mode/workflow.md`; this task does not request a new visual target or visual redesign, so no image-matching score is assigned.

## Code findings

Compared `Unity/Vesper/Assets/Vesper/Expansion/WeatherW10/Runtime/WorldCamera.cs` against the preserved `WeatherWorld/Runtime/WorldCamera.cs`.

- Mouse down only starts pointer ownership. Mouse drag has no camera mutation. A matching left-button release selects the destination through the existing motor, including after a large drag. Both former mouse-orbit paths, including the release-only displacement fallback, are gone. Mouse motion cannot change either desired yaw or elevation through this handler.
- Native polling reads Q and E and passes them to `HandleKeys`. Q decreases yaw, E increases yaw, and both held together cancel the requested increment. The rate is 0.65 radians per second with a 0.05-second per-frame cap. Both keys pass zero elevation change.
- `ResetView` retains the desired angles while restoring zoom, target and player position. R alone therefore does not rotate the camera. Wheel scaling and zoom limits are unchanged.
- `WorldRunInput.cs` and `WorldMotor.cs` differ from their preserved counterparts only by namespace. Left/right Shift polling, walking/running speeds and movement validation remain intact.
- Unpaired releases and non-left buttons are ignored. Component disable and application focus loss clear the held pointer. The report exercises component disable; application focus loss was verified in source only.
- Normal W10 runtime has no other caller of `Orbit`; it remains a public helper. The inherited yaw limits remain -0.05 to 1.10 radians. Camera following, elevation, zoom interpolation and framing formulas are unchanged.

Expected interaction details: movement now targets the release position even after dragging. Q/E rotation retains the existing smoothing, so it eases briefly after key release; an R or mouse event during that easing does not initiate that residual rotation. Simultaneous Q/E cancel new rotation rather than forcibly stopping an already easing camera. These are not blockers for preventing movement gestures from rotating the camera.

## Runtime evidence

Read the completed `input-qa-visible/report.json`, the probe source and `player.log`. The report has **19 PASS checks, 0 failures, no captured errors, 2 movement clicks, 0 mouse-orbit events, 0 safety stops and 0 audio sources**. The two movement cases cover a large drag/release and an ordinary click, with arrival, collision support and stable angles checked over their actual runtime frames (about 11.94 metres total).

The probe ran in the built Unity player at 1920 x 1080. It disables native polling and invokes the same key/pointer handlers directly. Consequently it validates the runtime handler path and resulting camera/movement behavior, but does not prove physical key delivery, IMGUI event delivery, hardware wheel behavior or the user's experience. The run check invokes `SetRunning(true)` and verifies speed; native Shift polling is supported by the unchanged source, not by a physical Shift press in this test.

The three six-second walking samples report approximately 62.0, 51.8 and 61.3 engine FPS, with p95 frame intervals of 20.0, 20.1 and 17.0 ms. These are bounded engine-cadence samples on the reported Intel Arc 130V device. They are not a full-route benchmark, recording result, W09 performance comparison or proof of perceived smoothness.

## Direct screenshot review

Opened and visually inspected all six actual PNGs in `input-qa-visible`:

- `start-qe-help.png`, `q-left.png` and `e-right.png`: the Q view visibly changes the road/building orientation; the subsequent E view returns toward the starting orientation, consistent with opposite yaw directions. The character stays visible, and there is no apparent elevation jump. Stills establish the resulting views, not rotation timing or input latency.
- The bottom help correctly says `Q / E to orbit`, with Click, Wheel, Shift and R instructions retained. It is readable and unclipped at 1920 x 1080, including the normal rain and snow captures. On the bright forced-flash capture, contrast is weaker over vegetation but the text remains discernible with its existing shadow. No HUD layout change is needed for this scope.
- `drag-release-walk-fixed-angle.png` shows the character farther along the same route with the rain, road, abbey and vegetation still visible. Angle stability during travel is supported by the frame-by-frame probe checks, not inferred from this single image.
- `w09-strong-flash-retained.png` visibly retains a bright, broadly distributed flash; `snow-retained.png` retains the blue snowy region and dense windblown snow. These are fixtures, including a forced flash and teleports, rather than proof of natural weather timing or continuous traversal.

`WorldEnvironment.cs` differs from the preserved source only by namespace and the help text. Its weather, flash, lighting and HUD layout code is unchanged. The screenshots show those features present, but are not a pixel-identical comparison against W09. Full historical-file/build preservation is covered by the parent's separate preservation audit.

## Scope and acceptance

This review approves the bounded implementation/evidence for removing mouse orbit and adding Q/E orbit. It does not adopt W10 on the user's behalf, award a new visual score, assert full-world visual acceptance, or request expansion of the controls-only task. No additional implementation blocker was identified.

The reviewer changed only this `judge.md`; no code, old evidence, game process or generated image was modified by this review.
