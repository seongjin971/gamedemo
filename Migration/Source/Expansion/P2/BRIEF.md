# VESPER P2 — height and area transitions

Requested 2026-09-09. Accepted baseline: candidate58 courtyard and the user's latest “오케이 모션좋다” feedback for 727ee87 P1 Run. That acceptance does not certify automated native Shift/mouse input. This task authorizes P2 implementation, playable Windows delivery and a local commit; P3 and later areas remain outside scope.

P2 has its own motor, input, animation connection, camera, zone owner, scene, NavMesh data and generated small crossing. Reuses the exact existing skin, material and Mixamo Idle/Walk/Running With Intention clips with the accepted stride calibration. No external generation or new external art assets. No Meshy calls.

Unity 6000.5.7f1 / URP17.5.0; Package Manager successfully installed AI Navigation2.0.14. Official release evidence: https://unity.com/releases/editor/whats-new/6000.5.5f1 lists2.0.13→2.0.14. Actual install and preparation evidence are in Migration/Evidence/Expansion/P2. Packages were installed through Unity Package Manager API. Scene, material, mesh, NavMesh and metadata creation use Editor APIs.

Single loaded scene, mutually exclusive area content roots with separate NavMeshSurface data. The common player, camera and input persist. Switching disables previous content before enabling the next, lets reflection resource destruction complete behind a fade, assigns the entrance spawn and updates the camera. No streaming framework, save system, combat, jump, swimming or new weather.

First collision wins for clicks. A hit must be on a designated walkable collision surface, within0.18m of NavMesh with at most0.15m height correction, and have a complete reachable path. Water, walls, rails and disconnected ledges reject. The collider height corrects NavMesh voxel approximation during movement; the character remains upright on slopes. The small courtyard collision tessellation is baked from its accepted walkable footprint; P1 navigation is not used at runtime. Existing masonry/tree collision blockers are P2-only scene additions.

Current Computer Use package imported, but sky.list_apps returned native pipe unavailable / os error2. No repeated permission request. Automatic commands and actual standalone captures must remain distinct from native input verification.

Validation resolution1536×1024, standalone D3D12. Performance must run after Editor/import workers exit, without any other player, Blender render or encoding. Compare the existing P1 Run build in adjacent runs; historical34–35FPS is context only. Independent reviewer requested only after self-review of a prepared candidate.
