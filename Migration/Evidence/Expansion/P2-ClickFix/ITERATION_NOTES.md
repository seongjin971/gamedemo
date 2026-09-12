# P2 visible-ground movement — 2026-09-09

**PAUSED BY USER.** See [PAUSED.md](PAUSED.md) for authoritative current state. First ground build failed three arrivals; the second preparation is saved but unbuilt/unverified. The launcher has been restored to the original preserved P2. Historical candidate results below are not a current release approval.

## Current candidate: actual ground geometry

The user tested the initial tolerance correction, said it improved input, and requested widening movement to the areas that visually look like ground. This supersedes the initial boundary-only scope below.

New isolated scene: `Assets/Vesper/Scenes/Expansion/VesperP2ClickFix.unity`. `P2GroundBuild.Prepare` clones the original P2 scene through Unity Editor APIs. It removes the invisible floor tessellation derived from P1's old flat footprint. Existing visible masonry mesh colliders now supply walkable floor and solid wall geometry. Actual tree/root meshes are nonwalkable obstacles. The courtyard surface is baked into new `ClickFixCourtyardNav.asset`; original P2 scene/NavMesh are preserved. Spawn/return heights are aligned to the actual paving. Rendering meshes, materials, lighting and connection geometry are unchanged.

The bake covers a courtyard volume and requires a complete path from the player. Elevated disconnected tops, walls and void are not authorized destinations merely because they look horizontal. The same-height click-edge correction remains, along with its discrete-support limitation explained below. `visible-ground-grid.csv` records physical surface samples and path results; it is not by itself a playability acceptance test.

Ground candidate build succeeded with zero errors/warnings (`ground-build-01.log`, 24.59s). Expanded standalone route and independent review pending. The current launcher targets `Builds/VesperP2ClickFix/VesperP2.exe`.

## Previous boundary-only candidate and diagnosis

Scope: fix courtyard floor clicks; retain P2 scenery, movement, navigation assets and all previous builds. Baseline commit: 7a4c4d2. New executable: `Unity/Vesper/Builds/VesperP2ClickFix/VesperP2.exe`.

## Reproduction

The user operated the trace-only standalone with their trackpad and confirmed movement and camera rotation. `user-input.log` records real IMGUI and raw mouse events at 1536×1024, DPI 192. Successful clicks actually changed the player position. Input/device failure was not reproduced. The user refined the issue to the walkable floor feeling much smaller than the visible floor.

Two rejected real clicks hit designated courtyard paving at (4.73,0,0.24) and (4.68,0,0.35). Editor inspection of the unchanged scene shows both valid in the original courtyard footprint, with a complete path to their nearest NavMesh point. Distances 0.409642 and 0.526314 exceed the old 0.18 click tolerance. The footprint already includes obstacle clearance, followed by further erosion in the NavMesh bake. `reported-targets.txt` and `courtyard-rays.csv` retain this evidence. The rejected root-area point (4.91,0,3.78) is outside the original footprint and 1.103543 from the mesh; it should stay blocked.

## Change

After the first ray hit passes the original walkable-layer and normal checks, clicks may resolve up to 0.65m to a complete path on the same level. Height tolerance remains 0.15m. Downward support samples every ≤0.08m must hit designated walkable ground between the hit and destination. These are discrete checks, not continuous collision proof for arbitrary narrow gaps or origin-inside-collider cases. The tested pier, root exclusion, water and disconnected ledge remain rejected. Motor stepping and `Walk` retain their existing tolerances. The scene and NavMesh are unchanged.

The production IMGUI path delegates to a shared pointer handler, allowing the standalone regression to exercise press/release → camera ray → floor → NavMesh → movement. Orphan releases after focus loss do not issue moves. A brief green destination square or orange blocked marker makes the response visible. Opt-in tracing is silent in normal launches.

## Verification status

Final build: zero errors and warnings, 29.77 seconds (`fix-build-02.log`, `build-report.txt`). Standalone `player-02/checks.txt`: 16/16 passed, including both reported paving clicks and arrival at (4.79,0,-0.17), drag without movement, orphan release suppression, preserved root/pier/water/disconnected-ledge rejection, bridge arrival and a full courtyard/crossing round trip. No error/exception entries in the player log.

Self-review of full-resolution `player-02` screenshots: courtyard appearance remains intact; actual arrival is visible behind existing tree branches, while the bridge screenshot shows the player on the deck and legible blocked feedback. First probe screenshots had an asynchronous capture/reset timing issue; `player-02` waits for capture before resetting and supersedes those images. This is an evidence correction, not a gameplay change.

The previous four builds retain all 695 recorded file hashes; the original P2 build also matches its full manifest (`original-builds-protection.json`, `old-p2-protection.json`). Only the P2 launcher is redirected. Existing scene, NavMesh, rendering assets, shared runtime and settings have no content diff. Status headers that were previously damaged by Korean shell encoding were rewritten in UTF-8 while retaining older history.

Independent review pending. A final normal interactive player with opt-in input logging was opened for the user; no automatic QA commands run there. The earlier P2 121-check report bypassed courtyard screen-click handling and does not establish this fix. Synthesized pointer events are distinguished from the real trackpad trace above; neither should be relabeled as the other. No new FPS certification is claimed; the extra support casts occur only on clicks and the small overlay lasts 0.9 seconds.
