# Latest: candidate58 user-accepted visual baseline

On2026-09-09, after the playable handoff, the user stated that the current quality is sufficient. Candidate58 (`7f7fd09`) is now the accepted visual baseline. See [the reviewed expansion plan](../../../EXPANSION_PLAN.md) for the proposed adventurer and environment work; implementation has not started. Original concept parity, measured60FPS and a candidate58 independent score are not newly established. Previous handoff and review records below remain historical evidence.

# Previous: candidate58 playable handoff

User requested finishing for play. Saved scene58 and Windows player are delivered; see candidate-58/SELF_REVIEW.md and player-58/VALIDATION.md. New build0errors/0warnings; static 43.45, walk 44.09, orbit 43.44, zoom 43.84 FPS. Original visual8/10 and60FPS remain unmet. Latest independent score belongs to52 (6.1/Tier2). No58 score or final adoption. PLAY_VESPER.cmd launches interactive mode. The following records are historical.

# Atmosphere V2 work in progress

## Latest saved and judged candidate52, 2026-09-09

Actual full/orbit/zoom/slice plus the exact former glare orbit were directly
reviewed. Fresh independent `verdict-unity-8.md`: **6.1/10, Tier2**. PavingV15,
ContactV14, KnightV7, retained TreeV12/MasonryV13, finer mineral normal/roughness,
shared reflection environment and localized3.6m fire illumination are integrated.
Slab outlines, darker bark, reduced brown bands and diagram halo improved;
rounded smooth paving, weak water, manufactured masonry and exposed root feet
still fail Tier3.48–51 are intermediate diagnostics with no separate judge score.

Player52:0build errors/0warnings, defaultD3D12,1536x1024, noninstrumented natural
cadence49.88–50.72FPS, runtime0errors/all-focused/no competing render or heavy QA.
This misses60 and is not display-present/window-visibility proof. Separate motion
389frames/33.425m/9.648–10.660Hz,0errors/skips/all-focused. All three root-route
destinations were reached; seven original frames were directly inspected. See
`candidate-52/SELF_REVIEW.md`, actual-timestamp VFR video and reports. Latest direct
input remains unavailable because the Windows native pipe still fails after user
permission. Technical checks and motion sampling do not establish visual adoption.

Repeated blockers prompted a structural construction review: new PavingV16,
MasonryV16 and TreeV16 source prototypes are underway, not yet imported or adopted.
Source versions are separate from native candidate numbers. Work remains active.

## Previous saved diagnostic: candidate47, 2026-09-09

See `candidate-47/SELF_REVIEW.md`, four actual Unity views, controlled shadow
reports and actual-timestamp motion video. TreeV12, StairsV13, eight local
MasonryV13 portal replacements, coherent photographed PavingV13, rune halo,
restrained sparks, SH stone light, retained wet normals and local fire shadows
are integrated. Paving now has866 neighboring bodies but reads as too many
rounded pads; water margins, masonry bands and root contacts remain unresolved.
No new judge score: **candidate41's6.0/Tier2 remains latest**.

Same player47-fixed(D3D12): exact local fire casters42.20–43.20FPS versus full
casters28.51–28.73; disabled fire shadows50.42–51.16. All runs focused/errors0,
no competing render or heavy validation. Same binary forcedD3D11 gives44.68–
45.47FPS; project API defaults unchanged. Build0errors/0warnings. These are
natural cadence, not monitor-present or occlusion evidence.60 remains unmet.

Motion396frames/20.606m/9.97–11.20Hz, errors/skips0; actual frame inspection
found the near-root route stopping after the first waypoint due to the probe's
arrival threshold versus snapped grid destination. The whole-root route is
not yet verified. Windows Computer Use list_apps still reports native pipe
unavailable despite user authorization, so latest direct input remains open.
KnightV7 is source-reviewed but not imported. ContactV14/PavingV14 source work
is underway. Work remains active with no inherited one-hour limit.

## Previous judged candidate41, 2026-09-09

Current saved scene is41. `candidate-41` contains actual full/orbit/zoom/slice
captures and the builder's direct self-review. The fresh independent verdict is
`verdict-unity-7.md`: **6.0/10, Tier2**. TreeV11 sculpted volume is a substantial
advance; shallow sheet-like paving, weak pool separation, masonry bands, clean
block faces and root contacts still fail Tier3. This is not final adoption.
KnightV6, photogrammetric PavingV11, integrated stairsV11 and masonryV12 are now
in the native scene. Original assets and previous candidates remain preserved.
Player41 built successfully with0 errors/0 warnings; clean cadence54.55–55.35FPS
misses60FPS. Motion324frames/13.436m/10.04–11.19Hz shows broad silver floor glare
during orbit and simple facade profiles at the lower camera limit. See its
self-review and original-timestamp VFR video. Both checks had0errors/all-focused,
but do not certify display-present FPS or direct input. Candidate36 is historical.

## Resumed 2026-09-09: candidate36

The user explicitly resumed the old paused checkpoint. Current native candidate36
is recorded in `candidate-36`; the newest fresh judge is `verdict-unity-6.md`,
5.8/10 Tier2. Candidate30 was5.6. The lower safe-stop sections are historical.
The target8/10 and final user adoption remain open. Grid-like paving, banded
masonry, tree anatomy and coherent pool boundaries remain the dominant blockers.

Candidate36 capture reports zero shader/runtime/missing-script errors. Its player
build has zero errors and zero warnings. Clean noninstrumented1536x1024 natural
frame cadence is static58.753/walk59.829/orbit59.909/zoom59.931FPS; all frames focused,
zero runtime errors, no concurrent Unity or Blender rendering. This is near60,
not a hardware display-present or window-occlusion trace. The walk benchmark
includes arrival and standing time.

`candidate-36/motion.mp4` uses actual asynchronous screenshot timestamps, about
10.02–10.94Hz, not60FPS footage. `motion-report.json` retains318 frame records,
13.478m movement, zero readback/runtime errors or skipped requests, all focused.
Source JPEGs remain in `.dream-loop/unity-atmosphere-v2/player-v36-motion`.
The corrected upright frames, movement, orbit, zoom and both camera limits were
directly inspected. Lower views expose remaining repeated facade construction.
Direct Windows pointer/keyboard testing remains blocked by the unavailable
Computer Use native pipe despite the user's explicit permission; player16 is
historical direct-input evidence only.

Use `-vesperMotionQA ABSOLUTE_NEW_FOLDER` for the opt-in visual recorder. It exits
after continuous walk/orbit/zoom and wide/close limit stages. Keep this separate
from clean frame-cadence benchmarking; asynchronous capture still adds overhead.

Current saved scene: `Assets/Vesper/Scenes/VesperAtmosphereV2.unity`.
This is an additive candidate, not visual acceptance or completed migration.
The original scene and browser assets remain preserved. See the root CHECKPOINT
for the latest candidate, judge score, open work and process state.

Unity 6000.5.7f1 / URP 17.5.0, Windows Intel Arc 130V 8GB.
Do not open a second Editor for this project. Check running processes first.
All commands below run from the repository root, with a new evidence folder.
Use `Start-Process -WindowStyle Hidden` for background Editor invocations.
Omit `-nographics` because actual GPU renders are required. These methods exit
the Editor themselves; omit `-quit`.

```powershell
$unity = 'C:/Program Files/Unity/Hub/Editor/6000.5.7f1/Editor/Unity.exe'
$project = 'C:/Users/brian/Dev/active/Dream Loop Astra/Unity/Vesper'
$evidence = Join-Path (Get-Location) '.dream-loop/unity-atmosphere-v2'
# Saved candidate capture, without rebuilding:
& $unity -batchmode -projectPath $project -executeMethod Vesper.Editor.VesperAtmosphereCapture.Run -vesperOutput '../../.dream-loop/unity-atmosphere-v2/NEW-CAPTURE' -logFile (Join-Path $evidence 'NEW-CAPTURE.log')
# Rebuild candidate from preserved slice and tracked derivative sources, then capture:
& $unity -batchmode -projectPath $project -executeMethod Vesper.Editor.VesperAtmosphereBuild.BuildAndCapture -vesperOutput '../../.dream-loop/unity-atmosphere-v2/NEW-REBUILD' -logFile (Join-Path $evidence 'NEW-REBUILD.log')
# Build a new Windows player folder:
& $unity -batchmode -projectPath $project -executeMethod Vesper.Editor.VesperPlayerBuild.Run -vesperPlayerOutput '../../.dream-loop/unity-atmosphere-v2/NEW-PLAYER/Vesper.exe' -logFile (Join-Path $evidence 'NEW-PLAYER.log')
```

The two capture sizes are intentional: slice 1037x739 against the preserved
browser comparison, full/orbit/zoom 1536x1024 against the original concept.
`capture.json` reports shader/runtime/missing-script errors and reflection
updates. Explicit render requests do not establish displayed FPS.

Launch the player visibly with `-screen-width 1536 -screen-height 1024
-screen-fullscreen 0` and a new `-logFile` path. Add one optional QA flag:

- `-vesperQA ABSOLUTE_OUTPUT_FOLDER`: natural player loop with static, walk,
  orbit and continuous zoom phases, screenshots/report, then quit.
- `-vesperManualQA ABSOLUTE_OUTPUT_FOLDER`: direct mouse/keyboard validation;
  F9 captures the actual screen; F10 saves the report and quits.

Normal player use has no QA object. Click to move, drag to orbit, wheel to zoom,
R to reset. Reports measure natural frame cadence, not hardware display-present
timing. Keep the player foreground and avoid concurrent Unity/Blender/render jobs
when measuring performance. Manual mixed-input sessions are not static benchmarks.

Independent Unity scores:4.5,4.8,4.9,5.4 in verdict1–4. Candidate23
passes Tier2, not Tier3 or the8/10 target. Its matched captures and player23
natural frame report are tracked here. Player23 runs about50.7–51.8FPS with no
other Unity/Blender render job, allframesfocused and0 runtime errors. This is
below60 and not hardware display-present timing. Player16 direct input evidence
remains separate. Candidate18/player18 are retained as the prior checkpoint.

Past experiments and complete logs remain under `.dream-loop/unity-atmosphere-v2`.
Failed release lifecycle, shader overload, excessive silver reflection and oval
water-surface experiments are retained there. No final visual adoption is claimed.


## User-requested safe stop after candidate27

The saved scene is the technically valid candidate27 photographic-stone diagnostic. It is visibly too smooth and has not passed a new visual judge. Candidate26 and27 captures, final saved-scene checkpoint27, and the instrumented player27 report are retained separately. The latest independent score remains candidate23 5.4/Tier2.

For optional diagnostic timing, build with `-vesperFrameTiming 1` and run with `-vesperTiming` alongside a QA flag. Do not compare that instrumented build directly with a noninstrumented frame-cadence result. Default player builds disable the setting. `VesperPlayerBuild.CaptureCheckpoint` disables timing through Editor API, saves settings, captures the saved scene, and exits. It does not regenerate geometry.

Player27-timing reports29.0-32.1FPS and31-35ms median GPU time, all frames focused and zero runtime errors. The UI screenshot attempt did not establish a displayed game image, so no occlusion or direct manipulation conclusion is drawn from that attempt. Five build warnings (including two possible normal initialization warnings) remain for follow-up. User requested stopping before further experiments or KnightV5 integration.
