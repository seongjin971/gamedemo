# Safe pause — 2026-09-09

Historical checkpoint. The user resumed work; [VALIDATION.md](VALIDATION.md) records the later corrected build and supersedes this launch/validation state.

User requested stopping at a safe point. No further build, probe or iteration is authorized by this pause. Unity preparation completed and exited; no Unity/P2 player remains running. Changes remain uncommitted on `unity-migration`, based on `7a4c4d2`.

## Launch state

`PLAY_VESPER_P2.cmd` was restored to the preserved `Unity/Vesper/Builds/VesperP2/VesperP2.exe`. This is the original P2 with its known restrictive floor-click behavior. The four original builds and original P2 match 695 and 174 recorded hashes respectively. Do not launch `Builds/VesperP2ClickFix` as a finished delivery: it currently contains the failed first ground-expansion build. The later scene changes have NOT been built into it.

## What was verified

The user's real trackpad trace proved input arrives, rotation works and accepted clicks move the player. Two original-valid paving hits were 0.409642/0.526314m outside the old NavMesh tolerance of 0.18m. An initial same-level correction up to 0.65m, first-hit filtering, discrete support samples and short accepted/blocked feedback passed 16 synthesized full input-handler-to-arrival checks (`player-02`). Independent review found no release blocker for that bounded candidate and corrected its initial mistaken claim that B was not reset: logs confirm both A and B start at (-2.25,0,7.5). It correctly cautioned that discrete support samples are not continuous collision proof.

The user then confirmed improvement but requested movement over all visible ground. That scope supersedes the boundary-only candidate. Its binary was overwritten by the subsequent ground-expansion build; its evidence remains. `boundary-build-hashes.json` refers only to the former boundary candidate, not the current executable.

## Current unfinished expansion

`P2GroundBuild.Prepare` creates a separate `Assets/Vesper/Scenes/Expansion/VesperP2ClickFix.unity` and separate `Generated/ClickFixCourtyardNav.asset`, preserving the original P2 scene/nav. First expansion baked actual masonry colliders directly and removed the legacy invisible footprint. Front paving targets at z=13.02 and 17.5 reached correctly, but three tree-side routes failed arrival (`ground-player-01/checks.txt`). Complete NavMesh paths took a stair-side detour and the motor stopped near (-2.92,-0.10,-1.47). `ground-paths.txt` records the failed build's path rising through y=0.2825 and 0.585. Thus a complete path alone was insufficient.

Last completed action: second preparation (`ground-prepare-02.log`), not a player build. It samples actual low paving at 0.15m spacing, excludes occupied body space via a small capsule, creates invisible navigation-only support on layer 27 (`ClickFixGroundSupport.asset`) and bakes radius 0.25/height 1.7/climb 0.2. Actual masonry remains layer 28 for click and foot-height rays; actual tree/root meshes remain layer 29. It targets low courtyard ground, leaving decorative stairs out of ground routes; the original P2 crossing ramp/bridge is unchanged. `visible-ground-grid.csv` now describes this second preparation, NOT the first failed build. This approach has not passed runtime or independent review and must not be treated as adopted.

## Resume only after user asks

1. Read this file, CHECKPOINT.md, git status, current scene/source and processes. Preserve all existing evidence/builds and user changes. Do not touch unrelated Windows AIXHost, shared visuals, P1 assets or P3.
2. Inspect the second preparation and its log for correctness. Build with `Vesper.Expansion.P2.Editor.P2ClickAudit.Build` into the isolated ClickFix directory, using a new log name. Never rebuild or overwrite the original P2 path.
3. Run opt-in `-p2ClickQA <new evidence folder>` at 1536×1024 with a dedicated `-logFile`; it exercises actual handler → screen ray → NavMesh → arrival. Require both tree-side and newly expanded front targets to arrive, blocker rejection, drag and courtyard/crossing round trip. Review raw screenshots, not only test counts.
4. Revisit path/motor compatibility if failures remain; do not mask failed movement with looser assertions or claim sampled support proves all collision safety. Add useful edge/body-clearance coverage for the sampled support approach before adoption.
5. Obtain fresh independent Dream Loop review of the latest candidate and direct user input review; prior review applies only to the narrower boundary candidate. Update build hashes, final validation and launcher only after passing. Keep native input traces distinct from synthesized input.

Relevant code: P2Motor.cs, P2Camera.cs, new P2ClickProbe.cs, Editor/P2ClickAudit.cs, Editor/P2GroundBuild.cs. Scene/material/meta edits were through Unity Editor APIs. Source/scene/nav WIP remains on disk; no reset, stash, commit or push was performed at this stop.
