# VESPER P2 visible courtyard ground — 2026-09-10

Current candidate is built from `Assets/Vesper/Scenes/Expansion/VesperP2ClickFix.unity` into `Unity/Vesper/Builds/VesperP2ClickFix/VesperP2.exe`. Final runtime and review results will be recorded below. Previous paused/failed candidates are history, not current acceptance.

## Problem and implementation

The user's trackpad input was received correctly. The original P2 required a floor click to lie within 0.18m of a NavMesh that was narrower than visible ground. Two recorded paving clicks failed at 0.41m and 0.53m from that mesh. An initial 0.65m edge correction improved input; the user then requested that the visible courtyard ground itself be included.

The new scene preserves the original P2 and all earlier scenes/builds. Existing masonry colliders provide actual floor height and wall geometry. The old hidden rectangular/P1-polygon footprint is replaced with navigation support sampled from the low courtyard paving at 0.15m spacing. A 0.12m-radius downward sphere gathers foot support across narrow decorative grooves; an occupancy capsule excludes solid body space, and the bake adds 0.25m agent clearance. The new support mesh is on layer 27 for navigation only. Actual masonry remains layer 28 for click/ground contact, and actual trees/roots remain layer 29 blockers.

Ground support and clicks use the same small foot-support radius. This intentionally spans narrow paving grooves; it is not a promise that every geometric gap or horizontal-looking object is traversable. The low courtyard floor is covered; tall walls, tree trunks, void and decorative stairs outside the low floor support remain unavailable. The separate P2 crossing ramp/bridge is retained. Rendering geometry, materials and lights were not redesigned.

Click handling still requires the first ray hit to be walkable with an upward normal, a nearby same-level target and a complete path. The 0.65m correction keeps the 0.15m height limit and checks support along the short correction. The destination marker is green; rejected clicks briefly show orange `Blocked`. Dragging remains separate from clicking, and a release without a captured press cannot cause movement. These sampled support checks are not continuous collision proof.

## Evidence and limits

- `user-input.log`: real trackpad trace before the initial correction; `user-final-input-snapshot.log`: user input after the initial edge correction, before full ground expansion. Neither is direct input acceptance of this latest candidate.
- `reported-targets.txt`: original rejected paving locations and distances.
- `ground-player-01`: direct masonry bake failed three tree-side arrivals after a stair detour.
- `ground-player-02`: point-sampled support left a narrow diagonal groove as a disconnected NavMesh boundary. `ground-map.png`, `support-geometry.json` and `navigation-geometry.json` diagnose this failed candidate.
- `ground-prepare-04.log`: foot-support sampling connects the floor across the grooves. `visible-ground-grid.csv` reflects this preparation; its 325 complete paths are sampled grid evidence, not 325 completed player journeys.
- `ground-build-03.log`: build succeeded, zero errors/warnings, 24.95 seconds.
- `ground-player-03`: current synthesized pointer → production handler → screen ray → NavMesh → moving-player checks. Arrival, frame-sampled ground support/body clearance, blockers, drag and round trip are evaluated independently of a static path result.

Native computer input connection was retried after resuming and still reports `native pipe unavailable / os error 2`. Synthetic pointer checks must remain distinct from actual device input. No changes were made to the unrelated Windows AIXHost issue. The original four builds and original P2 were previously hash-verified (695+174 files); final manifests are separate from historical `boundary-build-hashes.json`.

## Current result

`ground-player-03/checks.txt`: **29/29 passed**, no runtime error/exception entries. Both original paving targets, the tree-side target and front floor at z=13.02/17.49 reached their destinations; six journeys total include 990 sampled movement frames with ground support and body clearance checks. Blocked tree trunk, gate pier, outside front boundary, water and disconnected ledge reject. Drag does not issue movement; orphan release is ignored. Clicking the gates completes a courtyard/crossing round trip and bridge arrival.

Self-review of full-resolution screenshots: the player reaches the front floor and stands beside the tree on paving. The accepted scenery, materials and lighting remain visually intact. Existing branches can occlude the player near the tree. The bridge screenshot preserves the original P2 test-space appearance and readable blocked feedback. These captures do not establish foot IK or continuous collision safety between samples.

[Independent Dream Loop review](INDEPENDENT_REVIEW.md): PASS for this bounded candidate; no demonstrated release blocker. The reviewer independently confirmed the 29 checks, 990 movement frames and preserved courtyard appearance. Navigation and sampled static-scene tests are not universal collision protection: the motor has no continuous body sweep and retains its NavMesh height if a ground cast misses.

Adjacent standalone performance at 1536×1024, four 8-second stages, all focused: original P2 32.61/33.69/33.19/33.29 FPS; final 32.02/32.43/32.26/32.47 FPS (static/walk/orbit/zoom). This run is 1.8–3.8% lower, within the existing 10% regression threshold. No 60 FPS or hardware display-present certification is claimed. Both logs have zero reported gameplay errors. See `performance-comparison.json` and the two `player-report.json` files.

The launcher now selects the corrected build. A normal interactive player with opt-in input logging was opened for the user, without automatic commands. Latest direct user review is pending.

Final protection recheck: all 695 original-build files and 174 original-P2 files match their recorded hashes (`final-protection.json`). `final-build-hashes.json` identifies the current corrected executable/data. The earlier `boundary-build-hashes.json` remains historical. Tracked code/document/launcher whitespace checks pass; existing scene/settings/rendering assets have no content changes. The new generated scene and navigation assets were authored through Unity Editor APIs.
