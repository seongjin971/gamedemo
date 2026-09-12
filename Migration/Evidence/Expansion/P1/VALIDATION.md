# VESPER P1 delivery — 2026-09-09

**P1_PLAYABLE_BUILD_READY / DIRECT_INPUT_REVIEW_PENDING**. New novice adventurer in a separate copy of the accepted courtyard. P2 and later maps remain unstarted. This is implementation delivery for user play review, not a claim of final user visual acceptance.

## Run

Double-click [`PLAY_VESPER_P1.cmd`](../../../../PLAY_VESPER_P1.cmd). Build: `Unity/Vesper/Builds/VesperExpansion/VesperAdventurer.exe`; preserve the entire adjacent data/DLL folder. [Controls](../../../../PLAY_EXPANSION.md): left click ground to move, left drag to rotate, wheel to zoom, R to reset character and camera. The launcher supplies no QA commands.

Scene: `Assets/Vesper/Scenes/Expansion/VesperAdventurerP1.unity`. Editor:6000.5.7f1, URP17.5.0. Original `PLAY_VESPER.cmd`, candidate58 scene/assets and `Builds/VesperPreview` are preserved.

## Visible implementation and review

The new 31,113-triangle, 24-bone Generic skin has exposed chestnut hair/face, pale tunic, leather vest, trousers, boots, short teal shoulder cloth, compact pack and belt pouch. It has a narrower body and equipment silhouette than the knight. The backpack is largely concealed by the shawl at the normal camera. The scene uses the existing art scale; the1.78m source is displayed at1.8 scale against the original knight's approximately3.50-high renderer bounds.

One motor owns translation using the existing courtyard navigation. Idle/walk clips blend through acceleration, stopping and turning; the walk clock follows actual distance, calibrated against the source planted foot and visual scale. The motor cruises at2.25 scene units/s. Blender corrections replace the supplied staggered idle and excessive sideways arm spread. Cloth/accessories use the skin; no physical cloth or facial animation. The P1 camera keeps the accepted limits and recenters toward the character at close zoom. All runtime changes are expansion-only.

[Actual comparison images and video](COMPARISON.md). Self review directly inspected matched default/orbit/close captures, diagnostic portraits and actual player frames. The fresh [independent review](candidate-03/INDEPENDENT_REVIEW.md) opened baseline/current views and adjacent stop/turn frames and found no blocking visible defect. No further courtyard or microdetail loop was requested by that review. Hair/face/fingers are simplified at diagnostic magnification. The simple stop blend visibly repositions the rear foot; this is not a fully planted authored stop or motion-matching pivot. Reviewed samples show no large persistent penetration or severe sustained slide; neither reviewer claims to have continuously watched every frame.

## Build and runtime checks

- Windows StrictMode build succeeded, errors0/warnings0,26.83s: [build report](player-03/build-report.json). Build artifacts are local and Git-ignored, with [174-file hash manifest](player-03/build-hashes.json).
- Static scene capture: shader errors0, missing scripts0, runtime errors0, reflection134: [capture report](candidate-03/capture.json).
- [Functional test](player-03/functional/functional-report.json):21 checks passed, errors0,443 rendered frames,18.3984 units traveled. Checked one motor/no knight, skin/Animator, four destinations and existing navigation clearance, out-of-bounds rejection, mid-walk rerouting, zoom/orbit clamps and R handler reset. Player exited0.
- [Motion recording](player-03/motion/motion-summary.json):659 frames,25.4169 units, skipped0, errors0, unfocused0. Walk-stop, both reversal destinations and all three root-route destinations completed. Eight stage capture rates9.876–11.264Hz. The MP4 uses recorded timestamps and is separate from the performance run.
- [Contact proxy](player-03/motion/contact-proxy.json): low-toe constant-cruise samples have median horizontal speeds .0204/.0270 units/s against2.25 root speed. This supports cadence calibration; toe bones are not sole geometry and this is not a substitute for visual acceptance.
- The optional editor portrait helper initially crashed at shutdown after writing its images. Releasing temporary render/material resources and unloading the diagnostic scene fixed it. [Clean retry](portrait-03-clean/portrait-complete.json):three views/resources released, process exit0. The earlier log remains under `portrait-03`.

## Performance

Adjacent runs on the same Arc130V8GB,1536×1024 windowed, defaultD3D12, same quality settings,5s warmup and8s per stage. No other Unity/Blender/player render or video encode ran concurrently. FrameTiming instrumentation was disabled; values are natural application frame cadence, not hardware display-present/monitor FPS. Each stage takes one end screenshot, using the same probe pattern in both builds. Walk stage includes arrival and idle, so it is not eight seconds of uninterrupted walking. The P1 close-zoom framing intentionally differs slightly from the baseline camera.

| Stage | Candidate58 FPS | P1 FPS | Candidate58 p95 ms | P1 p95 ms |
| --- | ---: | ---: | ---: | ---: |
| Static |32.8387|33.4045|31.7496|31.5368|
| Walk/arrival |33.1283|33.7765|31.6162|31.1146|
| Orbit |32.6362|33.3087|32.0931|31.3660|
| Zoom |33.3057|33.4402|31.7036|31.2216|

[Baseline report](baseline/final/player-report.json) and [P1 report](player-03/performance/player-report.json):both errors0/unfocused0, player exit0. No10% regression threshold is triggered. The small difference is not claimed as a proven optimization. Both remain below60FPS. Historical candidate58 evidence was43.44–44.09FPS; the unchanged original build itself now measures32.64–33.31, so the historical gap is not attributed to the P1 character. The earlier same-session baseline measured33.77–34.46. No whole-courtyard performance work was added.

## Input limits, provenance and preservation

Windows Computer Use reconnect failed with native pipe unavailable / os error2. No repeated permission request and no alternative native input injection were used. Automated commands exercised runtime components; they are **not actual mouse/keyboard input**. Input counters are0 in the automatic runs. Direct click/drag/wheel/R feel and monitor presentation remain for the user to check in the supplied normal launcher.

Original imagegen reference, Meshy model/rig/idle, Blender sources and request/status/hash records: [BRIEF.md](../../../Source/Expansion/P1/BRIEF.md). Meshy **3 submitted jobs /43credits**; status queries/downloads are not additional generations. No extra Meshy or Higgsfield generation was needed. Credentials and signed download URLs are excluded from tracked files.

[Protection audit](protection-audit.json):176 original launcher/scene/build files have unchanged SHA256. Tracked original assets, materials, shaders, runtime code, package/project settings and historical evidence have no diff. New Unity scene/material/import settings/metas were produced through Editor APIs. The original atmosphere/migration builder was not run to generate expansion assets. Only P1 expansion paths, separate launcher/instructions and current status documents are delivered; P2 navigation heights/NavMesh, map transitions and environment expansion were not implemented.
