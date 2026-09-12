Current Unity baseline is candidate58 (`7f7fd09`), visually accepted by the user on2026-09-09. Play it using [PLAY.md](../PLAY.md). The reviewed next plan is [EXPANSION_PLAN.md](../EXPANSION_PLAN.md); adventurer and environment expansion has not started. User acceptance does not change the measured43.44-44.09FPS or assign a new independent score.

Current candidate commands and evidence: [AtmosphereV2](Evidence/AtmosphereV2/README.md). [CHECKPOINT.md](../CHECKPOINT.md) takes precedence over the historical migration notes below, including their earlier missing-build/visual-gate statements. Preserve the accepted scene and use separate expansion scenes/assets/builds when implementation begins.

# VESPER Unity migration

The browser baseline is preserved by tag `browser-baseline-2026-09-08` on `main`. Work proceeds on `unity-migration`; no remote repository or push is configured.

First package: a separate Unity 6000.5.7f1 URP project at `Unity/Vesper`, importing the existing authored geometry and texture images, then matching a bounded knight/tree/courtyard/fire view. Browser source and historical assets remain available. Full-scene visual adoption follows the initial comparison; a successful import is not visual acceptance.

`Reference/browser-baseline.png` is an actual browser render. `Reference/concept.png` remains the visual target. The browser score is 6.5/10, not the Unity score. `ArtSource` at repository root contains the three current Blender masters. Extended source history and evidence remain locally in the ignored `.dream-loop` directory.

## Open and compare

1. Open `Unity/Vesper` with Unity **6000.5.7f1**. Its manifest pins URP **17.5.0**.
2. Open `Assets/Vesper/Scenes/VesperMigrationSlice.unity` and press Play.
3. Click the courtyard to move, drag to orbit, scroll to zoom, and press **R** to reset. The camera follows slowly. Movement is bounded to the court.
4. Compare [the actual Unity capture](Evidence/unity-slice.png) with [the matching browser capture](Reference/unity-browser-slice.png), both **1037 × 739**. Set that Game view aspect ratio for the same framing. The original full-scene target remains 1536 × 1024.

The first native scene contains the knight hierarchy and motion, tree, masonry, distant architectural context, flame sprites/flickering point lights, native planar floor reflection, contact shading, and saved tone/bloom overrides. The mesh bridge imports **95 geometries, 22 source materials and 4,711 instances**; **146 deep foundation instances** are deferred from this comparison package.

This is an initial migration comparison, not full visual parity or a final Dream Loop result. The floor still reads drier/brighter, fire reflections are weaker, tree shadows differ, and the distant haze/panorama needs matching. Browser line/particle/custom-shader effects (including the rune rings, embers and drifting haze), grass wind, browser UI and full-scene camera polish are not fully ported. The knight's rounded shoulders are an inherited art issue. See [the self-review](Evidence/SELF_REVIEW.md).

## Verification and reproducibility

- `node --test`: 5 tests, including real Three.js Sprite interleaved-buffer export and normalized attributes.
- `npm.cmd run build`: passes; the existing bundle-size advisory remains.
- `Evidence/import-report.json`: imported object counts and missing-script check.
- `Evidence/validation.json`: 47 valid obstacle-avoiding routes, valid materials, and persistent volume overrides.
- `Evidence/render-report.json`: native URP capture, shader/runtime error counts and reflection frames, after reopening the saved project in a fresh Editor process.
- `Evidence/play-smoke.json`: scripted Editor Play movement and repeated reflection updates. The harness submits render requests explicitly; its frame count is **not presented FPS** or direct mouse/keyboard acceptance.

No standalone Windows build, continuous user input review or final 60 FPS acceptance has been completed for Unity. No Unity art score is assigned yet; its first comparison needs the material and atmosphere work above before the full target can be judged fairly.

The checked-in `Assets/Vesper/Import` snapshot preserves the exported hierarchy, transforms and geometry. The importer reflects the X axis, adjusts quaternions/normals, reverses winding once, preserves instance/mesh colors, and combines masonry in batches. It rebuilds native Unity materials and rendering effects; Three.js shader code is not converted automatically.

`VESPER > Build migration slice` rebuilds **the generated scene and generated assets** from that snapshot while retaining existing asset GUIDs. Keep later hand-edited scenes under a different name if rebuilding this generated comparison. Normal review only requires opening the saved scene; rebuilding is unnecessary.

For automated checks, close this project's interactive Editor, then run its installed Editor with `-batchmode -projectPath <absolute Unity/Vesper path>` and one of these execute methods:

| Method | Action |
| --- | --- |
| `Vesper.Editor.VesperCapture.BuildAndRun` | Rebuild and render comparison; exits itself |
| `Vesper.Editor.VesperCapture.Run` | Reopen saved scene, validate and render; exits itself |
| `Vesper.Editor.VesperValidation.PlaySmoke` | Validate, enter Play, move and render; exits itself |

Supply `-logFile <absolute log path>`. Use normal graphics (omit `-nographics`) and omit `-quit` for these methods. Evidence is written into repository-local `.dream-loop/unity-migration`. Wait for the Editor process to finish and inspect the result JSON and `VESPER_*_PASS` markers; the Windows launcher can return before Unity finishes.

New browser exports are explicit via **U** and appear under `.dream-loop/evidence`. Refreshing the checked-in import snapshot is a separate action. The Vite watcher excludes Unity/import/evidence directories to avoid Unity lock-file errors. Only `Assets`, `Packages` and `ProjectSettings` are tracked from Unity; its caches and personal settings are ignored.
