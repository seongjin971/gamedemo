# DEFERRED — not adopted in playable candidate58

The user requested finishing for play. Candidate57's late CityBackdrop queue caused a visible foundation fade regression; candidate58 restores queue1000. Depth priming remains disabled by default. The optional runtime diagnostic is preserved, but its on-mode is not an accepted delivery setting. No early-backdrop helper was written. The following plan is historical and requires new implementation/visual/performance validation before adoption.

# Lossless-first depth priming experiment

Read-only installed URP17.5 and saved55 shader census:119 opaque slots =56AtmosphereStone,43URP/Lit,19URP/Unlit,1AtmosphereBackdrop. This is serialized source evidence, not measured draw calls.52 player has validTimings0 and about19.7–20.0ms/frame; CPU/GPU bottleneck remains unclassified.

The existing SSAO uses DepthNormals before opaques while main depth priming is Disabled. Forced can reuse the prepass depth for an Equal/ZWriteOff opaque color pass, avoiding covered expensive fragments. It does not remove the prepass and may add CameraDepthTexture copy cost. No FPS benefit is assumed.

Two common prerequisites are applied before BOTH comparison conditions: AtmosphereStone DepthOnly and DepthNormals now use the same material Cull as Forward (one double-sided wind grass renderer previously differed); CityBackdrop moves from opaque background queue1000 to2501 with its existing ZWriteOff/LEqual shader, avoiding forcedEqual on a shader with no depth pass. Background/fog ordering must first be visually checked. Internal URP/Lit and Unlit already provide matching depth/cull passes. Transparent water/flame/mist/distant stone are excluded from opaque priming.

`VesperDepthPrimingDiagnostic` supports startup `-vesperDepthPriming off` or `on`. It writes the public live UniversalRenderer.depthPrimingMode for main renderer0 only and requires reflection renderer1 to remain Disabled. No settings/data assets are modified. A two-second warmup check asserts the renderer identity and mode survive; Editor capture reapplies the requested mode at each view. A data setter instead invalidates/recreates a renderer, so it is deliberately avoided for this same-player comparison.

First compare actual fixed-time full/zoom/glare/slice, then continuous grass/knight/motion. Only if intact, run the same standalone binary clean non-instrumented off/on loops without other heavy work. Record natural app loop FPS separately from monitor-present visibility and direct input. If mode changes the picture materially, do not call it lossless or adopt it based on FPS alone.

Two later candidates from the audit remain unimplemented: compile-time removal of exactly-zero patina/legacy reflection ALU (the nine legacy texture samples are already skipped at runtime), and static point-shadow depth caching with dynamic character composition. Neither has a measured saving.
