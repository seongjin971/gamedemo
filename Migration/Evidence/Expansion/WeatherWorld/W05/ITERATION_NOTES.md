# W05 bounded final candidate

The user reiterated on 2026-09-11 that work should finish once visibly meaningful changes exist. W05 is the final visual pass for this package, subject to actual runtime and performance checks. A full-image Pro score below 8 must remain disclosed; the stop request does not convert it into a full-target visual pass.

- W01: additional 48m grove; isolated runtime/materials/meshes; initial lighting and particles. Full-target judge 5.49.
- W02: localized distant glow and stronger snow; native UnityPlayer crash on snow entry. Preserved, not delivered.
- W03: removed per-flake physics, actual snow capture completed. Judge 5.78. Long horizontal flakes and foliage wash identified.
- W04: architectural weather correction: separate foliage silhouette from distant haze; separate night direct/ambient balance; softened shadows; diagonal depth layers; surface-specific wet flash. Judge 5.91. Actual changed-boundary traversal passed: 30 pointer clicks, 180.34m, zero safety stops, failures or managed runtime errors, zero audio sources.
- W05: preserves W04 movement/route/collider implementation. Increases soft diagonal snow and adds separate camera-facing airborne powder layers, while retaining low ground spindrift. Uniform early-outs avoid expensive atmospheric flash math when no flash is active. Snow collisions remain disabled; geometry depth and shelter mask handle weather occlusion.

No old preparation scripts or old full movement suites were run. L09 was only launched for same-resolution FHD screenshot comparison. The initial 221-file preservation manifest passed after W04; final W05 comparison is required at delivery.

W04's `WEATHER_PREVIEW.mp4` is an internal 7.64-samples-per-second screenshot preview with preserved timing. It is **not** an OBS recording, a smooth delivery video or a performance measurement. Do not present it as a 30 FPS gameplay recording. Existing OBS settings and recording workflow are unchanged.
