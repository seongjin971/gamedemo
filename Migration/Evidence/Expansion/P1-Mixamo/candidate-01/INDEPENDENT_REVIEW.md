# Independent bounded Mixamo movement review — 2026-09-09

Reviewer: fresh independent agent `mixamo_motion_review`. Read SELF_REVIEW.md, then personally opened the actual images listed below with `view_image`. No implementation edits, Unity/Blender runs, new rendering, video playback/encoding, or performance measurement were performed for this review.

**Result: no blocking gross movement or visual regression observed in the reviewed samples. Ready for direct user movement review; this is not final adoption.** Candidate58 courtyard acceptance is outside this review and is not re-scored. No numerical visual target or polish loop is requested.

The Mixamo walk has a visible but modest benefit at the delivered camera scale: the torso reads upright, the forward boot extends clearly, and arm positions vary naturally without a wide wing-like silhouette. The closer near-root side view (new0264 versus baseline0275) shows a less folded trailing leg and a more relaxed stride silhouette. These are similar route positions with nearby, not identical, phases. Several matched wide-camera walk poses are quite similar. The stills support a plausible improvement in pose quality, not a claim that continuous gait quality is conclusively much better.

The stop sample0044/0046/0047/0048/0049/0050/0054 changes from extended stride into a settled stance. Foot repositioning is plainly visible as the trailing boot draws inward while the root finishes stopping. The report records speed0 at0048 and blend0 at0050; subsequent inspected0054 remains settled. This is a short blend, not a planted authored stop. Comparable baseline0050/0052 also repositions the feet. I do not see a new gross skating failure here, but these samples cannot establish foot-lock or rule out smaller sliding in continuous play.

After receiving the parent's low-toe diagnostic concern, I additionally opened every frame0038–0042 at cruise speed2.25. The supporting boot stays in approximately the same floor area while the other leg passes; I do not see persistent large skating across these adjacent images. Small residual drift remains possible and should not be called fixed: the actual left-toe joint coordinates move about0.070 units in the floor plane over these frames, while its height changes from0.109 to0.095. Joint motion includes rolling/pivoting and does not isolate sole sliding. The parent's broader low-toe proxy reports a larger median than baseline, so improved ground contact is specifically not established by this review.

Turn starts0130–0132 and reversal0174–0176/0178/0182 preserve an intact torso/leg silhouette. Turning happens quickly across the sampled interval and feet rotate/reposition; it does not demonstrate planted turning. No collapsed/inverted knee, detached limb, wide arm wing, or large garment penetration was visible. Near-root0234/0240/0264/0290/0296 retains the character on the courtyard with readable legs and no obvious trunk/cloth intersection in these views. Close-limit0612 remains intact. Fine sleeve, hip, and sole contacts remain difficult to resolve at this character size and lighting.

Full/orbit/zoom pairs preserve the scene's broad composition, character scale, and materials visually. Animated tree/atmosphere differences between captures are visible; this review does not infer asset preservation from pixel equality.

Evidence opened, relative to `Migration/Evidence/Expansion/`:

- Both `P1/candidate-03/` and `P1-Mixamo/candidate-01/`: full.png, orbit.png, zoom.png.
- `P1-Mixamo/player-01/motion/`: 0036,0038,0039,0040,0041,0042,0044,0046,0047,0048,0049,0050,0054,0130,0131,0132,0174,0175,0176,0178,0182,0234,0240,0264,0290,0296,0612.jpg.
- `P1/player-03/motion/`: 0038,0044,0046,0050,0052,0138,0184,0244,0250,0275,0301,0638.jpg.
- Both motion-report.json files were parsed for stage, phase, speed, blend, and player coordinates to avoid equating different stages by frame number. For example, new0036/baseline0038 have phases0.16/0.15, new0044/baseline0046 phases0.75/0.72, and new0234/baseline0244 phases0.37/0.34.

Limits: this is selected still/adjacent-frame review of actual standalone captures, not continuous realtime playback, direct-input play acceptance, exhaustive deformation QA, or clean FPS evidence. Performance belongs to the separate benchmark. No further visual iteration is justified by the bounded findings alone.
