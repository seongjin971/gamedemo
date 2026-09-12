# Candidate58 playable build validation

Later user decision,2026-09-09: candidate58 visual quality was accepted as sufficient. This does not change these build/FPS/motion measurements or establish direct input verification. Original observations below are historical; current acceptance and the reviewed expansion plan are in [CHECKPOINT.md](../../../../CHECKPOINT.md).

Windows build succeeded: errors0, warnings0, 111.30s. Delivered executable: Unity/Vesper/Builds/VesperPreview/Vesper.exe. PLAY_VESPER.cmd starts ordinary interactive mode without QA flags or depth priming.

1536x1024, default D3D12, Intel Arc130V8GB, FrameTiming disabled, natural application frame loop: static 43.45, walk 44.09, orbit 43.44, zoom 43.84 FPS. All sampled frames focused; runtime errors0. No other Unity/Blender render or heavy QA ran concurrently. This is not a monitor-present trace or proof of unobscured display. The walk FPS segment includes time after arrival. 60FPS is not achieved.

Separate automated continuous motion: 427 JPEG95 frames, 33.424m traveled, skipped0, errors0, unfocused0. See motion-report.json for timestamps, camera transforms and actual destination arrivals. Actual representative player images were inspected separately. This test drives the real navigation/camera code, but is not direct mouse/keyboard input. Native Computer Use remains unavailable despite authorization.

Directly inspected player static.png and original motion0034/0119/0203/0272/0337/0396, covering walk, near-root, orbit, zoom and both camera limits. All three near-root destinations have actual arrival records. Knight movement, cape silhouette and background fade are visible; no missing/pink assets appeared in these samples. Close-limit framing crops the lower character body near the bottom edge, and low wide views still expose repetitive outer walls. The six samples do not constitute a direct watch of every recorded frame. motion.mp4 preserves actual frame timestamps without interpolation.

The clean43.44-44.09FPS is below candidate52's49.88-50.72FPS; this combined geometry/material/light-range update does not isolate the cause, and no new GPU timing claim is made. Further optimization was deferred to honor the user's request to finish for play.

Actual saved-scene five-view review is in ../candidate-58/SELF_REVIEW.md. Latest independent score remains candidate52's6.1/Tier2, not a score for58. Original8/10 visual target and user final acceptance remain open. User requested finishing for play, so further aesthetic iterations and a new independent visual submission were deferred.
